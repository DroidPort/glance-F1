from fastapi import APIRouter
from fastapi_cache import FastAPICache
import httpx
from datetime import datetime, timedelta
import hashlib
import json

import fastf1
from fastf1.ergast import Ergast 

from .helpers.functions import country_to_code, get_next_race_end, format_team_name
from .helpers.global_vars import NEXT_RACE_API_URL, nationality_map, default_expire
from .helpers.time_functions import MT, UTC

router = APIRouter()

def make_signature(results):
    return hashlib.md5(json.dumps(results, 
        sort_keys=True).encode()).hexdigest()

@router.get("/", summary="Fetch current constructors championship")
async def get_constructors_championship():
    cache = FastAPICache.get_backend()
    cache_key = "constructors_championship"

    cached = await cache.get(cache_key)
    if cached:
        return cached

    season = datetime.now(MT).year
    ergast = Ergast()
    standings = ergast.get_constructor_standings(season = season)
    standing_data = standings.content[0]

    results = []
    for _, row in standing_data.iterrows():
        if row["constructorNationality"] in nationality_map:
            row["constructorNationality"] = nationality_map[row["constructorNationality"]]
        else:
            row["constructorNationality"] = ""

        results.append({
            "team": row["constructorName"],
            "position": row["position"],
            "points": row["points"],
            "wins": row["wins"],
            "country": row["constructorNationality"],
            "flag": country_to_code(row["constructorNationality"]),
            "wiki": row["constructorUrl"]
        })

    now = datetime.now(MT)
    race_dt = await get_next_race_end()

    expire = default_expire
    expiry_dt = now + timedelta(seconds=default_expire)

    cached = await cache.get(cache_key)
    old_signature = cached.get("result_signature") if cached else None
    new_signature = make_signature(results)
    if race_dt:
        if race_dt > now:
            expire = max(60, int((race_dt - now).total_seconds()))
            expiry_dt = race_dt
        elif now < race_dt + timedelta(seconds=default_expire):
            expiry_dt = race_dt + timedelta(seconds=default_expire)
            expire = int((expiry_dt - now).total_seconds())
        else:
            expire = default_expire
            expiry_dt = now + timedelta(seconds=default_expire)

            async with httpx.AsyncClient() as client:
                season = datetime.now(MT).year
                ergast = Ergast()
                fresh_standings = ergast.get_constructor_standings(season = season)
                fresh_standings = fresh_standings.content[0]

                fresh_results = []
                for _, row in fresh_standings.iterrows():
                    if row["constructorNationality"] in nationality_map:
                        row["constructorNationality"] = nationality_map[row["constructorNationality"]]
                    else:
                        row["constructorNationality"] = ""

                    fresh_results.append({
                        "team": row["constructorName"],
                        "position": row["position"],
                        "points": row["points"],
                        "wins": row["wins"],
                        "country": row["constructorNationality"],
                        "flag": country_to_code(row["constructorNationality"]),
                        "wiki": row["constructorUrl"]
                    })
                next_response = await client.get(NEXT_RACE_API_URL)

            fresh_results = fresh_results.json()
            data = next_response.json()
            
            new_signature = make_signature(fresh_results)

            if old_signature != new_signature:
                new_next_dt = data.get("next_event", {}).get("datetime")

                if new_next_dt:
                    next_race_dt = datetime.fromisoformat(new_next_dt)

                    if next_race_dt.tzinfo is None:
                        next_race_dt = UTC.localize(next_race_dt)
                    next_race_dt = next_race_dt.astimezone(MT)

                    expire = int((next_race_dt - now).total_seconds())
                    expiry_dt = next_race_dt

    response_data = {
        "season": season, 
        "cache_expires": expiry_dt.isoformat(),
        "constructors": results,
        "result_signature": new_signature}

    await cache.set(cache_key, response_data, expire=expire)
    return response_data