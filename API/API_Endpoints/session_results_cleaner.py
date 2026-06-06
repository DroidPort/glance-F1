from fastapi import APIRouter
from fastapi_cache import FastAPICache
import httpx
from datetime import datetime, timedelta

from .helpers.functions import country_to_code, format_team_name
from .helpers.global_vars import nationality_map
from .helpers.time_functions import MT

router = APIRouter()

F1API_BASE = "https://f1api.dev/api/current/last"

SESSION_CONFIG = [
    {
        "key": "fp1",
        "label": "Free Practice 1",
        "url": f"{F1API_BASE}/fp1",
        "date_field": "fp1Date",
        "time_field": "fp1Time",
        "results_field": "fp1Results",
        "time_result_field": "time",
    },
    {
        "key": "fp2",
        "label": "Free Practice 2",
        "url": f"{F1API_BASE}/fp2",
        "date_field": "fp2Date",
        "time_field": "fp2Time",
        "results_field": "fp2Results",
        "time_result_field": "time",
    },
    {
        "key": "fp3",
        "label": "Free Practice 3",
        "url": f"{F1API_BASE}/fp3",
        "date_field": "fp3Date",
        "time_field": "fp3Time",
        "results_field": "fp3Results",
        "time_result_field": "time",
    },
    {
        "key": "sprintQualy",
        "label": "Sprint Qualifying",
        "url": f"{F1API_BASE}/sprint/qualy",
        "date_field": "sprintQualyDate",
        "time_field": "sprintQualyTime",
        "results_field": "sprintQualyResults",
        "time_result_field": "q3",
    },
    {
        "key": "sprintRace",
        "label": "Sprint Race",
        "url": f"{F1API_BASE}/sprint/race",
        "date_field": "sprintRaceDate",
        "time_field": "sprintRaceTime",
        "results_field": "sprintRaceResults",
        "time_result_field": "time",
    },
    {
        "key": "qualy",
        "label": "Qualifying",
        "url": f"{F1API_BASE}/qualy",
        "date_field": "qualyDate",
        "time_field": "qualyTime",
        "results_field": "qualyResults",
        "time_result_field": "q3",
    },
    {
        "key": "race",
        "label": "Race",
        "url": f"{F1API_BASE}/race",
        "date_field": "raceDate",
        "time_field": "raceTime",
        "results_field": "results",
        "time_result_field": "time",
    },
]


def clean_driver(entry, time_field):
    driver = entry.get("driver", {})
    team = entry.get("team", {})

    nationality = driver.get("nationality", "")
    if nationality in nationality_map:
        nationality = nationality_map[nationality]

    surname = driver.get("surname", "")
    # Known name fixes
    if surname == "Kimi Antonelli":
        surname = "Antonelli"

    time_value = entry.get(time_field) or entry.get("time") or entry.get("q1") or ""

    return {
        "position": entry.get("position"),
        "surname": surname,
        "shortName": driver.get("shortName", ""),
        "flag": country_to_code(nationality),
        "team": format_team_name(team.get("teamId", "")),
        "teamId": team.get("teamId", ""),
        "time": time_value,
    }


async def fetch_session(client, session_cfg):
    try:
        resp = await client.get(session_cfg["url"], timeout=30)
        if resp.status_code == 404:
            return None  # Session hasn't happened yet
        if resp.status_code != 200:
            return None
        data = resp.json()
    except Exception:
        return None

    race = data.get("races", {})
    if not race:
        return None

    raw_results = race.get(session_cfg["results_field"], [])
    if not raw_results:
        return None

    results = [clean_driver(r, session_cfg["time_result_field"]) for r in raw_results]

    return {
        "key": session_cfg["key"],
        "label": session_cfg["label"],
        "raceName": race.get("raceName", ""),
        "date": race.get(session_cfg["date_field"], ""),
        "time": race.get(session_cfg["time_field"], ""),
        "results": results,
    }


@router.get("/", summary="Fetch all session results for current race weekend")
async def get_session_results():
    cache = FastAPICache.get_backend()
    cache_key = "f1:session_results"

    cached = await cache.get(cache_key)
    if cached:
        return cached

    sessions = []
    race_name = ""

    async with httpx.AsyncClient() as client:
        for cfg in SESSION_CONFIG:
            result = await fetch_session(client, cfg)
            if result:
                sessions.append(result)
                if not race_name:
                    race_name = result.get("raceName", "")

    response_data = {
        "raceName": race_name,
        "sessions": sessions,
    }

    # Cache for 30 minutes during a race weekend
    await cache.set(cache_key, response_data, expire=1800)
    return response_data
