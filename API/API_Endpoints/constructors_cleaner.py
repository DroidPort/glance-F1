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


    response_data = {
        "season": season, 
        "constructors": results}

    await cache.set(cache_key, response_data, expire=600)
    return response_data