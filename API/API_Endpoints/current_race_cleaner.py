- type: custom-api
  title: Next Race
  cache: 5m
  url: http://192.168.0.210:4463/f1/next_race/
  template: |
    <div class="flex flex-column gap-10">
      {{ $session := index (.JSON.Array "race") 0 }}
      <p class="size-h5" style="font-size: 15px;">
        {{ .JSON.String "season" }}, Round {{ .JSON.String "round" }}
      </p>

      <div class="margin-block-4">
        <p class="color-highlight" style="font-size: 15px;">{{ $session.String "raceName" }}</p>

        <div class="margin-block-10"></div>

        <!--FP1-->
        <p class="color-primary" style="font-size: 15px;">
          <span>Free Practice 1</span>
          {{ $fp1datetime := .JSON.String "race.0.schedule.fp1.datetime_rfc3339" }}
          {{ $parsedFP1Time := parseLocalTime "2006-01-02T15:04:05Z07:00" $fp1datetime }}
          {{ if $parsedFP1Time.Before now }}
            <span class="color-highlight">🏁</span>
          {{ else }}
            <span class="color-highlight" {{ parseRelativeTime "rfc3339" $fp1datetime }}></span>
          {{ end }}
        </p>
        {{ $fp1 := .JSON.String "race.0.schedule.fp1.datetime_rfc3339" }}
        <p class="size-h5" style="font-size: 13px;">{{ slice $fp1 0 10 }} {{ slice $fp1 11 16 }}</p>

        <!--Sprint Qualifying-->
        {{ if and (ne ($.JSON.String "race.0.schedule.sprintQualy.date") "null") (ne ($.JSON.String "race.0.schedule.sprintQualy.date") "") }}
        <p class="color-primary" style="font-size: 15px;">
          <span>Sprint Qualifying</span>
          {{ $sqdatetime := .JSON.String "race.0.schedule.sprintQualy.datetime_rfc3339" }}
          {{ $parsedSQTime := parseLocalTime "2006-01-02T15:04:05Z07:00" $sqdatetime }}
          {{ if $parsedSQTime.Before now }}
            <span class="color-highlight">🏁</span>
          {{ else }}
            <span class="color-highlight" {{ parseRelativeTime "rfc3339" $sqdatetime }}></span>
          {{ end }}
        </p>
        {{ $sq := .JSON.String "race.0.schedule.sprintQualy.datetime_rfc3339" }}
        <p class="size-h5" style="font-size: 13px;">{{ slice $sq 0 10 }} {{ slice $sq 11 16 }}</p>
        {{ end }}

        <!--Sprint Race-->
        {{ if and (ne ($.JSON.String "race.0.schedule.sprintRace.date") "null") (ne ($.JSON.String "race.0.schedule.sprintRace.date") "") }}
        <p class="color-primary" style="font-size: 15px;">
          <span>Sprint Race</span>
          {{ $srdatetime := .JSON.String "race.0.schedule.sprintRace.datetime_rfc3339" }}
          {{ $parsedSRTime := parseLocalTime "2006-01-02T15:04:05Z07:00" $srdatetime }}
          {{ if $parsedSRTime.Before now }}
            <span class="color-highlight">🏁</span>
          {{ else }}
            <span class="color-highlight" {{ parseRelativeTime "rfc3339" $srdatetime }}></span>
          {{ end }}
        </p>
        {{ $sr := .JSON.String "race.0.schedule.sprintRace.datetime_rfc3339" }}
        <p class="size-h5" style="font-size: 13px;">{{ slice $sr 0 10 }} {{ slice $sr 11 16 }}</p>
        {{ end }}

        <!--FP2-->
        {{ if and (ne ($.JSON.String "race.0.schedule.fp2.date") "null") (ne ($.JSON.String "race.0.schedule.fp2.date") "") }}
        <p class="color-primary" style="font-size: 15px;">
          <span>Free Practice 2</span>
          {{ $fp2datetime := .JSON.String "race.0.schedule.fp2.datetime_rfc3339" }}
          {{ $parsedFP2Time := parseLocalTime "2006-01-02T15:04:05Z07:00" $fp2datetime }}
          {{ if $parsedFP2Time.Before now }}
            <span class="color-highlight">🏁</span>
          {{ else }}
            <span class="color-highlight" {{ parseRelativeTime "rfc3339" $fp2datetime }}></span>
          {{ end }}
        </p>
        {{ $fp2 := .JSON.String "race.0.schedule.fp2.datetime_rfc3339" }}
        <p class="size-h5" style="font-size: 13px;">{{ slice $fp2 0 10 }} {{ slice $fp2 11 16 }}</p>
        {{ end }}

        <!--FP3-->
        {{ if and (ne ($.JSON.String "race.0.schedule.fp3.date") "null") (ne ($.JSON.String "race.0.schedule.fp3.date") "") }}
        <p class="color-primary" style="font-size: 15px;">
          <span>Free Practice 3</span>
          {{ $fp3datetime := .JSON.String "race.0.schedule.fp3.datetime_rfc3339" }}
          {{ $parsedFP3Time := parseLocalTime "2006-01-02T15:04:05Z07:00" $fp3datetime }}
          {{ if $parsedFP3Time.Before now }}
            <span class="color-highlight">🏁</span>
          {{ else }}
            <span class="color-highlight" {{ parseRelativeTime "rfc3339" $fp3datetime }}></span>
          {{ end }}
        </p>
        {{ $fp3 := .JSON.String "race.0.schedule.fp3.datetime_rfc3339" }}
        <p class="size-h5" style="font-size: 13px;">{{ slice $fp3 0 10 }} {{ slice $fp3 11 16 }}</p>
        {{ end }}

        <!--Qualifying-->
        <p class="color-primary" style="font-size: 15px;">
          <span>Qualifying</span>
          {{ $qualydatetime := .JSON.String "race.0.schedule.qualy.datetime_rfc3339" }}
          {{ $parsedQUALYTime := parseLocalTime "2006-01-02T15:04:05Z07:00" $qualydatetime }}
          {{ if $parsedQUALYTime.Before now }}
            <span class="color-highlight">🏁</span>
          {{ else }}
            <span class="color-highlight" {{ parseRelativeTime "rfc3339" $qualydatetime }}></span>
          {{ end }}
        </p>
        {{ $qualy := .JSON.String "race.0.schedule.qualy.datetime_rfc3339" }}
        <p class="size-h5" style="font-size: 13px;">{{ slice $qualy 0 10 }} {{ slice $qualy 11 16 }}</p>

        <!--Race-->
        <p class="color-primary" style="font-size: 15px;">
          <span>Race</span>
          {{ $racedatetime := .JSON.String "race.0.schedule.race.datetime_rfc3339" }}
          {{ $parsedRACETime := parseLocalTime "2006-01-02T15:04:05Z07:00" $racedatetime }}
          {{ if $parsedRACETime.Before now }}
            <span class="color-highlight">🏁</span>
          {{ else }}
            <span class="color-highlight" {{ parseRelativeTime "rfc3339" $racedatetime }}></span>
          {{ end }}
        </p>
        {{ $race := .JSON.String "race.0.schedule.race.datetime_rfc3339" }}
        <p class="size-h5" style="font-size: 13px;">{{ slice $race 0 10 }} {{ slice $race 11 16 }}</p>

      </div>

      {{ if .JSON.String "map_svg" }}
      <div style="margin-block: 1rem;">
        {{ .JSON.String "map_svg" }}
      </div>
      {{ end }}

      <p class="color-highlight" style="font-size: 14px;">Circuit Details</p>
      <p class="size-h6" style="font-size: 13px;">{{ $session.String "circuit.circuitName" }}</p>
      <p class="size-h6" style="font-size: 13px;">{{ $session.String "laps" }} laps @ {{ $session.String "circuit.circuitLengthKm" }} km</p>
      <p class="size-h6" style="font-size: 13px;">Lap record: {{ $session.String "circuit.lapRecord" }}, {{ $session.String "circuit.fastestLapDriverName" }} ({{ $session.String "circuit.fastestLapYear" }})</p>
    </div>from fastapi import APIRouter
from fastapi_cache import FastAPICache
import httpx
from datetime import datetime, timedelta
import fastf1
import hashlib 
import json
import os

from .helpers.time_functions import TZ, MT, UTC, convert_to_mt, get_datetime
from .helpers.global_vars import default_expire

router = APIRouter()

def make_signature(race):
    relevant = {
        "winner": race.get("winner")
    }
    return hashlib.md5(json.dumps(relevant, sort_keys=True).encode()).hexdigest()

@router.get("/", summary="Fetch next race")
async def get_next_race():
    cache = FastAPICache.get_backend()
    cache_key = "f1:next_race"

    cached = await cache.get(cache_key)
    old_signature = None

    if cached:
        return cached

    async with httpx.AsyncClient() as client:
        try:
            # Get data from current season
            response = await client.get("https://f1api.dev/api/" + str(datetime.now().year))
            if response.status_code != 200:
                return {"error": "Failed to fetch race schedule"}
            calendar_data = response.json()
        except Exception as e:
            return {"error": f"Exception while fetching: {e}"}

    races = sorted(calendar_data.get("races", []), key=lambda r: r.get("schedule", {}).get("race", {}).get("date", ""))

    # Loop through list in order until find first race with date past today. 
    next_race = None
    now = datetime.now(MT)
    for i, race in enumerate(races, start = 1):
        if datetime.now().year == 2026 and i in (4, 5):
            continue
        race_date_str = race.get("schedule", {}).get("race", {}).get("date")
        race_time_str = race.get("schedule", {}).get("race", {}).get("time")
        if not race_date_str or not race_time_str:
            continue
        
        race_datetime_utc = datetime.strptime(f"{race_date_str}T{race_time_str}", "%Y-%m-%dT%H:%M:%SZ")
        race_datetime_utc = UTC.localize(race_datetime_utc)

        race_datetime_local = race_datetime_utc.astimezone(MT)
        if race_datetime_local >= now:
            next_race = race
            break

    if not next_race:
        return {"message": "No upcoming race found"}

    # Convert schedule times
    schedule = next_race.get("schedule", {})
    for session, val in schedule.items():
        if val["date"] and val["time"]:
            dt_mt = convert_to_mt(val["date"], val["time"])
            val["date"] = dt_mt.strftime("%Y-%m-%d")
            val["time"] = dt_mt.strftime("%-I:%M%p")
            val["datetime_rfc3339"] = dt_mt.isoformat()

    # Clean up race name
    year = calendar_data.get("season")
    calendar_round = next_race.get("round")
    raw_round = calendar_round  # Store original round for fastf1 lookups

    # Handle issues in 2026 calendar due to race cancellations
    if year == 2026 and calendar_round >= 6:
        calendar_round = calendar_round - 2

    event_details = fastf1.get_event(year = year, gp = calendar_round)
    next_race["raceName"] = event_details.EventName

    # Circuit processing
    circuit = next_race.get("circuit", {})
    if "circuitLength" in circuit:
        try:
            raw_length = int(circuit["circuitLength"].replace("km", "").strip())
            circuit["circuitLengthKm"] = raw_length / 1000.0
        except Exception:
            circuit["circuitLengthKm"] = None

    # Fastest driver name formatting
    fastest_driver_id = circuit.get("fastestLapDriverId")
    if fastest_driver_id:
        name_parts = fastest_driver_id.replace("_", " ").split(" ")
        circuit["fastestLapDriverName"] = name_parts[-1].capitalize()

    # Correct laptime formatting 
    fastest_lap_time = circuit.get("lapRecord")
    if fastest_lap_time:
        circuit["lapRecord"] = ".".join(fastest_lap_time.rsplit(":", 1))

    # Compute total distance
    laps = next_race.get("laps")
    if laps and circuit.get("circuitLengthKm") is not None:
        next_race["totalDistanceKm"] = round(laps * circuit["circuitLengthKm"], 2)
    else:
        next_race["totalDistanceKm"] = None

    new_signature = make_signature(next_race)

    sorted_schedule = sorted(schedule.items(), key=get_datetime)

    session_name_readable = {
        "fp1": "Free Practice 1",
        "fp2": "Free Practice 2",
        "fp3": "Free Practice 3",
        "qualy": "Qualifying",
        "sprintQualy": "Sprint Qualifying",
        "sprintRace": "Sprint Race",
        "race": "Race"
    }

    next_event = None
    try:
        detail_level = os.environ.get("EVENT_DETAIL").strip()
    except Exception:
        detail_level = 'main'

    for session_name, session_data in sorted_schedule:
        event_datetime_str = session_data.get("datetime_rfc3339")
        event_date_str = session_data.get("date")
        event_time_str = session_data.get("time")
        if not event_datetime_str:
            continue

        if detail_level == "main":
            print("Showing Quali and Race Events Only")
            if session_name in ('fp1', 'fp2', 'fp3'):
                continue
        elif detail_level == "race":
            print("Showing Races Only")
            if session_name not in ('race', 'sprintRace'):
                continue
        elif detail_level == "detailed":
            print("Showing All Events")
        else:
            raise ValueError("Select one of: 'main', 'race', or 'detailed'. No selection defaults to main.")

        try:
            dt = datetime.fromisoformat(event_datetime_str)
            if dt > datetime.now(MT): 
                next_event = {
                    "session": session_name_readable.get(session_name, session_name.title()),
                    "date": event_date_str,
                    "time": event_time_str,
                    "datetime": event_datetime_str
                }
                break
        except Exception:
            continue


    # Cache expiry logic based on race time
    now = datetime.now(MT)

    # Race time for post race caching logic
    race_session = next_race.get("schedule", {}).get("race")
    race_dt = None
    if race_session and race_session.get("datetime_rfc3339"):
        race_dt = datetime.fromisoformat(race_session["datetime_rfc3339"])

    expire = default_expire
    expiry_dt = now + timedelta(seconds=default_expire)
    if next_event and next_event.get("datetime"):
        try:
            next_event_dt = datetime.fromisoformat(next_event["datetime"])
            if next_event_dt > now:
                # Cache until next session starts
                expire = max(1, int((next_event_dt - now).total_seconds()))
                expiry_dt = next_event_dt
            else:
                expire = default_expire
                expiry_dt = now + timedelta(seconds=expire)
        except Exception:
            expire = default_expire
            expiry_dt = now + timedelta(seconds=expire)

    elif race_dt:
        if now < race_dt + timedelta(hours=1):
            # Race just ended, wait minimum of 1 hour
            expiry_dt = race_dt + timedelta(hours=1)
            expire = int((expiry_dt - now).total_seconds())
        else:
            # 1 hour after race, poll every hour
            expire = default_expire
            expiry_dt = now + timedelta(seconds=expire)

            if old_signature and old_signature != new_signature:
                print("Results updated, polling stopped")
                try:
                    next_race_dt = None 

                    for race in races:
                        r_date = race.get("schedule", {}).get("race", {}).get("date")
                        r_time = race.get("schedule", {}).get("race", {}).get("time")

                        if not r_date or not r_time:
                            continue

                        dt_utc = datetime.strptime(f"{r_date}T{r_time}", "%Y-%m-%dT%H:%M:%SZ")
                        dt_utc = UTC.localize(dt_utc)
                        dt_local = dt_utc.astimezone(MT)

                        if dt_local > race_dt:
                            next_race_dt = dt_local
                            break

                    if next_race_dt:
                        expire = int((next_race_dt - now).total_seconds())
                        expiry_dt = next_race_dt
                    else:
                        expire = 86400
                        expiry_dt = now + timedelta(seconds = expire)
                except Exception as e:
                    print("Next race cache fallback:", e)
                    expire = 86400
                    expiry_dt = now + timedelta(seconds=expire)
    else:
        expire = default_expire
        expiry_dt = now + timedelta(seconds=expire)


    # Output data
    response_data = {
        "season": calendar_data.get("season"),
        "round": calendar_round,
        "raw_round": raw_round,
        "timezone": TZ,
        "next_event": next_event,
        "cache_expires": expiry_dt.isoformat(),
        "race": [next_race]
    }

    await cache.set(cache_key, response_data, expire=expire)
    return response_data
