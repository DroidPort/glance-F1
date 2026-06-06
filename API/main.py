from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
import asyncio

from API_Endpoints.current_race_cleaner import router as current_race_cleaner, get_next_race
from API_Endpoints.constructors_cleaner import router as constructors_cleaner
from API_Endpoints.drivers_cleaner import router as drivers_cleaner
from API_Endpoints.map.router import router as map_router, get_dynamic_track_map
from API_Endpoints.last_race_cleaner import router as last_race_cleaner
from API_Endpoints.session_results_cleaner import router as session_results_router

app = FastAPI()

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend())
    # Pre-warm caches on startup so Glance never times out on first request
    asyncio.create_task(prewarm_caches())

async def prewarm_caches():
    await asyncio.sleep(2)  # Let server fully start first
    try:
        await get_next_race()
        print("Pre-warmed: next_race")
    except Exception as e:
        print(f"Pre-warm next_race failed: {e}")
    try:
        await get_dynamic_track_map()
        print("Pre-warmed: track_map")
    except Exception as e:
        print(f"Pre-warm track_map failed: {e}")

# Include all routers
app.include_router(current_race_cleaner, prefix="/f1/next_race")
app.include_router(last_race_cleaner, prefix="/f1/last_race")
app.include_router(constructors_cleaner, prefix="/f1/constructors_standings")
app.include_router(drivers_cleaner, prefix="/f1/drivers_standings")
app.include_router(map_router, prefix="/f1/next_map")
app.include_router(session_results_router, prefix="/f1/session_results")
