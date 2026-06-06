from fastapi import APIRouter
from fastapi_cache import FastAPICache
import fastf1
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import pytz

from .helpers.time_functions import MT

router = APIRouter()

SESSION_MAP = [
    ("FP1", "Free Practice 1"),
    ("FP2", "Free Practice 2"),
    ("FP3", "Free Practice 3"),
    ("SQ",  "Sprint Qualifying"),
    ("SS",  "Sprint Race"),
    ("Q",   "Qualifying"),
    ("R",   "Race"),
]

executor = ThreadPoolExecutor(max_workers=4)


def load_session_sync(year, gp_round, session_type):
    try:
        session = fastf1.get_session(year, gp_round, session_type)

        # Practice sessions need laps for timing data; results sessions use results
        is_practice = session_type in ("FP1", "FP2", "FP3")
        if is_practice:
            session.load(laps=True, telemetry=False, weather=False, messages=False)
        else:
            session.load(laps=False, telemetry=False, weather=False, messages=False)

        return session
    except Exception as e:
        print(f"Failed to load {session_type}: {e}")
        return None


def session_has_happened(session):
    try:
        session_date = session.date
        if session_date is None:
            return False
        if hasattr(session_date, 'tzinfo') and session_date.tzinfo is None:
            session_date = pytz.utc.localize(session_date)
        session_date = session_date.astimezone(MT)
        now = datetime.now(MT)
        return session_date < now
    except Exception:
        return False


def format_practice_results(session):
    """For FP sessions, use fastest lap per driver."""
    try:
        laps = session.laps
        if laps is None or laps.empty:
            return None

        # Get fastest lap per driver
        fastest = laps.groupby("DriverNumber")["LapTime"].min().reset_index()
        fastest = fastest.sort_values("LapTime")

        drivers = []
        for pos, (_, row) in enumerate(fastest.iterrows(), start=1):
            import math
            driver_number = row["DriverNumber"]
            lap_time = row["LapTime"]
            if lap_time is None or (isinstance(lap_time, float) and math.isnan(lap_time)):
                continue

            # Get driver info
            driver_laps = laps[laps["DriverNumber"] == driver_number]
            if driver_laps.empty:
                continue

            driver_row = driver_laps.iloc[0]
            abbrev = driver_row.get("Driver", "")
            team = driver_row.get("Team", "")

            # Format lap time
            if hasattr(lap_time, 'total_seconds'):
                total = lap_time.total_seconds()
                mins = int(total // 60)
                secs = total % 60
                time_str = f"{mins}:{secs:06.3f}"
            else:
                time_str = str(lap_time)

            # Get flag from session results if available
            flag = ""
            try:
                result_row = session.results[session.results["Abbreviation"] == abbrev]
                if not result_row.empty:
                    flag = str(result_row.iloc[0].get("CountryCode", "")).lower()
            except Exception:
                pass

            drivers.append({
                "position": pos,
                "surname": abbrev,
                "shortName": abbrev,
                "flag": flag,
                "team": team,
                "time": time_str,
            })

        return drivers if drivers else None

    except Exception as e:
        print(f"Error formatting practice results: {e}")
        return None


def format_results(session, session_type):
    """For quali/race sessions, use results table."""
    try:
        results = session.results
        if results is None or results.empty:
            return None

        drivers = []
        for _, row in results.iterrows():
            position = row.get("Position")
            try:
                import math
                if position is None or (isinstance(position, float) and math.isnan(position)):
                    position = "-"
                else:
                    position = int(position)
            except Exception:
                position = "-"

            if session_type in ("Q", "SQ"):
                time_val = row.get("Q3") or row.get("Q2") or row.get("Q1")
            else:
                time_val = row.get("Time")

            if hasattr(time_val, 'total_seconds'):
                total = time_val.total_seconds()
                if total < 0:
                    time_str = "DNF"
                else:
                    mins = int(total // 60)
                    secs = total % 60
                    time_str = f"{mins}:{secs:06.3f}" if mins > 0 else f"{secs:.3f}"
            elif time_val is None or "NaT" in str(type(time_val)):
                status = row.get("Status", "")
                time_str = status if status else "DNF"
            else:
                time_str = str(time_val) if time_val else ""

            flag = str(row.get("CountryCode", "")).lower()

            drivers.append({
                "position": position,
                "surname": row.get("LastName", ""),
                "shortName": row.get("Abbreviation", ""),
                "flag": flag,
                "team": row.get("TeamName", ""),
                "time": time_str,
            })

        return drivers if drivers else None

    except Exception as e:
        print(f"Error formatting results: {e}")
        return None


async def fetch_session_fastf1(year, gp_round, session_type, label):
    loop = asyncio.get_event_loop()
    try:
        session = await loop.run_in_executor(
            executor, load_session_sync, year, gp_round, session_type
        )
        if session is None:
            return None

        if not session_has_happened(session):
            return None

        is_practice = session_type in ("FP1", "FP2", "FP3")
        results = format_practice_results(session) if is_practice else format_results(session, session_type)

        if not results:
            return None

        session_date = session.date
        if hasattr(session_date, 'tzinfo') and session_date.tzinfo is None:
            session_date = pytz.utc.localize(session_date)
        session_date = session_date.astimezone(MT)

        return {
            "key": session_type,
            "label": label,
            "raceName": session.event.EventName,
            "date": session_date.strftime("%Y-%m-%d"),
            "time": session_date.strftime("%I:%M%p"),
            "results": results,
        }

    except Exception as e:
        print(f"Error fetching {session_type}: {e}")
        return None


@router.get("/", summary="Fetch all session results for current race weekend")
async def get_session_results():
    cache = FastAPICache.get_backend()
    cache_key = "f1:session_results"

    cached = await cache.get(cache_key)
    if cached:
        return cached

    now = datetime.now(MT)
    year = now.year

    # Get current round from next_race cache — use raw_round for fastf1 lookups
    next_race_cached = await cache.get("f1:next_race")
    if next_race_cached:
        gp_round = next_race_cached.get("raw_round") or next_race_cached.get("round")
    else:
        loop = asyncio.get_event_loop()
        try:
            schedule = await loop.run_in_executor(executor, fastf1.get_event_schedule, year)
            current_event = None
            for _, event in schedule.iterrows():
                event_date = event.get("EventDate")
                if event_date and str(event_date)[:10] <= now.strftime("%Y-%m-%d"):
                    current_event = event
            if current_event is None:
                return {"raceName": "", "sessions": []}
            gp_round = int(current_event.get("RoundNumber", 1))
        except Exception as e:
            return {"raceName": "", "sessions": [], "error": str(e)}

    tasks = [
        fetch_session_fastf1(year, gp_round, session_type, label)
        for session_type, label in SESSION_MAP
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    sessions = [r for r in results if r is not None and not isinstance(r, Exception)]
    race_name = sessions[0]["raceName"] if sessions else ""

    response_data = {
        "raceName": race_name,
        "sessions": sessions,
    }

    await cache.set(cache_key, response_data, expire=1800)
    return response_data
