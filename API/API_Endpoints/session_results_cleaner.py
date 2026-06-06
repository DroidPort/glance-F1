from fastapi import APIRouter
from fastapi_cache import FastAPICache
import fastf1
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

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
        session.load(laps=False, telemetry=False, weather=False, messages=False)
        return session
    except Exception:
        return None


def format_results(session, session_type):
    try:
        results = session.results
        if results is None or results.empty:
            return None

        drivers = []
        for _, row in results.iterrows():
            position = row.get("Position")
            try:
                position = int(position)
            except Exception:
                position = "-"

            # Format time
            if session_type == "Q":
                time_val = row.get("Q3") or row.get("Q2") or row.get("Q1")
            elif session_type == "SQ":
                time_val = row.get("Q3") or row.get("Q2") or row.get("Q1")
            else:
                time_val = row.get("Time")

            # Convert timedelta to string
            if hasattr(time_val, 'total_seconds'):
                total = time_val.total_seconds()
                if total < 0:
                    time_str = "DNF"
                else:
                    mins = int(total // 60)
                    secs = total % 60
                    if mins > 0:
                        time_str = f"{mins}:{secs:06.3f}"
                    else:
                        time_str = f"{secs:.3f}"
            elif time_val is None or (hasattr(time_val, '__class__') and 'NaT' in str(type(time_val))):
                status = row.get("Status", "")
                time_str = status if status else "DNF"
            else:
                time_str = str(time_val) if time_val else ""

            # Country code from nationality
            nationality = str(row.get("CountryCode", "")).lower()

            drivers.append({
                "position": position,
                "surname": row.get("LastName", ""),
                "shortName": row.get("Abbreviation", ""),
                "flag": nationality,
                "team": row.get("TeamName", ""),
                "time": time_str,
            })

        return drivers

    except Exception as e:
        return None


async def fetch_session_fastf1(year, gp_round, session_type, label):
    loop = asyncio.get_event_loop()
    try:
        session = await loop.run_in_executor(
            executor, load_session_sync, year, gp_round, session_type
        )
        if session is None:
            return None

        # Only include sessions that have already happened
        session_date = session.date
        if session_date is None:
            return None

        now = datetime.now(MT)
        if hasattr(session_date, 'tzinfo') and session_date.tzinfo is None:
            import pytz
            session_date = pytz.utc.localize(session_date).astimezone(MT)

        if session_date > now:
            return None  # Session hasn't happened yet

        results = format_results(session, session_type)
        if not results:
            return None

        return {
            "key": session_type,
            "label": label,
            "raceName": session.event.EventName,
            "date": session_date.strftime("%Y-%m-%d"),
            "time": session_date.strftime("%I:%M%p"),
            "results": results,
        }

    except Exception:
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

    # Get current round from next_race cache if available
    next_race_cached = await cache.get("f1:next_race")
    if next_race_cached:
        gp_round = next_race_cached.get("round")
    else:
        # Fallback: use current date to find round
        schedule = await asyncio.get_event_loop().run_in_executor(
            executor, fastf1.get_event_schedule, year
        )
        # Find the most recent or current event
        current_event = None
        for _, event in schedule.iterrows():
            event_date = event.get("EventDate")
            if event_date and event_date <= now.date():
                current_event = event
        if current_event is None:
            return {"raceName": "", "sessions": []}
        gp_round = int(current_event.get("RoundNumber", 1))

    # Fetch all sessions concurrently
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

    # Cache for 30 minutes
    await cache.set(cache_key, response_data, expire=1800)
    return response_data
