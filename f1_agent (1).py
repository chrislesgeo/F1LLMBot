import os
import sys
import json
import requests
from datetime import datetime

GROK_API_KEY = os.environ.get("GROK_API_KEY")
GROK_API_URL = "https://api.x.ai/v1/chat/completions"
GROK_MODEL = "grok-3"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"

F1_API_BASE = "https://api.jolpi.ca/ergast/f1"
WEATHER_BASE = "https://api.open-meteo.com/v1/forecast"

LLM_BACKEND = os.environ.get("LLM_BACKEND", "grok").lower()

CIRCUITS = {
    "bahrain":       {"lat": 26.0325,  "lng": 50.5106,   "name": "Bahrain International Circuit",
                      "type": "permanent", "drs_zones": 3, "overtaking": "medium",
                      "tire_deg": "high",  "power_sensitive": True,
                      "characteristics": "Fast, flowing circuit with heavy braking zones. Sandy conditions cause high tire degradation. Strong winds can be a factor."},
    "jeddah":        {"lat": 21.6319,  "lng": 39.1044,   "name": "Jeddah Corniche Circuit",
                      "type": "street",    "drs_zones": 3, "overtaking": "medium",
                      "tire_deg": "medium","power_sensitive": True,
                      "characteristics": "Ultra-fast street circuit. High walls, minimal run-off. Fastest street circuit on the calendar. Safety car probability very high."},
    "australia":     {"lat": -37.8497, "lng": 144.9680,  "name": "Albert Park Circuit",
                      "type": "street",    "drs_zones": 4, "overtaking": "medium",
                      "tire_deg": "low",   "power_sensitive": False,
                      "characteristics": "Semi-street circuit in Melbourne. Smooth surface, low tire wear. Unpredictable early-season conditions. Safety car likely."},
    "japan":         {"lat": 34.8431,  "lng": 136.5407,  "name": "Suzuka Circuit",
                      "type": "permanent", "drs_zones": 1, "overtaking": "low",
                      "tire_deg": "medium","power_sensitive": False,
                      "characteristics": "Technical masterpiece. High-speed S curves demand high downforce. Overtaking is difficult. Typhoon season can bring wet conditions."},
    "china":         {"lat": 31.3389,  "lng": 121.2197,  "name": "Shanghai International Circuit",
                      "type": "permanent", "drs_zones": 2, "overtaking": "medium",
                      "tire_deg": "high",  "power_sensitive": True,
                      "characteristics": "Long back straight rewards top speed. High tire degradation. Cool conditions typical in April."},
    "miami":         {"lat": 25.9581,  "lng": -80.2389,  "name": "Miami International Autodrome",
                      "type": "street",    "drs_zones": 3, "overtaking": "medium",
                      "tire_deg": "medium","power_sensitive": True,
                      "characteristics": "Purpose-built street-style circuit. High temperatures and humidity. Bumpy surface increases tire stress."},
    "imola":         {"lat": 44.3439,  "lng": 11.7167,   "name": "Autodromo Enzo e Dino Ferrari",
                      "type": "permanent", "drs_zones": 1, "overtaking": "low",
                      "tire_deg": "medium","power_sensitive": False,
                      "characteristics": "Narrow, old-school circuit with very limited overtaking. Safety cars frequent. Rain probability significant in spring."},
    "monaco":        {"lat": 43.7347,  "lng": 7.4205,    "name": "Circuit de Monaco",
                      "type": "street",    "drs_zones": 1, "overtaking": "very_low",
                      "tire_deg": "low",   "power_sensitive": False,
                      "characteristics": "Tightest circuit on the calendar. Qualifying position is almost everything. Overtaking near-impossible on track."},
    "barcelona":     {"lat": 41.5700,  "lng": 2.2611,    "name": "Circuit de Barcelona-Catalunya",
                      "type": "permanent", "drs_zones": 2, "overtaking": "low",
                      "tire_deg": "high",  "power_sensitive": False,
                      "characteristics": "High-speed corners demand aero balance. Hot weather causes severe tire deg. Traction out of Turn 1 key to lap time."},
    "canada":        {"lat": 45.5017,  "lng": -73.5222,  "name": "Circuit Gilles Villeneuve",
                      "type": "semi_street","drs_zones": 2,"overtaking": "high",
                      "tire_deg": "medium","power_sensitive": True,
                      "characteristics": "Stop-start layout rewards power. Long pit straight enables overtaking. Wall of Champions claims victims. Rain is common."},
    "austria":       {"lat": 47.2197,  "lng": 14.7647,   "name": "Red Bull Ring",
                      "type": "permanent", "drs_zones": 3, "overtaking": "high",
                      "tire_deg": "medium","power_sensitive": True,
                      "characteristics": "Short, punchy circuit. Huge elevation changes. Long DRS zone makes overtaking easier. Afternoon thunderstorms common."},
    "silverstone":   {"lat": 52.0786,  "lng": -1.0169,   "name": "Silverstone Circuit",
                      "type": "permanent", "drs_zones": 2, "overtaking": "medium",
                      "tire_deg": "high",  "power_sensitive": False,
                      "characteristics": "Classic high-speed circuit. Maggotts-Becketts demands aerodynamic grip. British summer weather is unpredictable."},
    "hungary":       {"lat": 47.5830,  "lng": 19.2526,   "name": "Hungaroring",
                      "type": "permanent", "drs_zones": 1, "overtaking": "low",
                      "tire_deg": "high",  "power_sensitive": False,
                      "characteristics": "Twisty, narrow circuit. Very hot and grippy surface. Overtaking difficult. Qualifying crucial."},
    "spa":           {"lat": 50.4372,  "lng": 5.9714,    "name": "Circuit de Spa-Francorchamps",
                      "type": "permanent", "drs_zones": 2, "overtaking": "medium",
                      "tire_deg": "medium","power_sensitive": True,
                      "characteristics": "Legendary circuit through the Ardennes. Eau Rouge/Raidillon is iconic. Weather changes rapidly."},
    "netherlands":   {"lat": 52.3888,  "lng": 4.5407,    "name": "Circuit Zandvoort",
                      "type": "permanent", "drs_zones": 2, "overtaking": "low",
                      "tire_deg": "high",  "power_sensitive": False,
                      "characteristics": "Banked corners are unique. Very hard to overtake. Coastal location means wind plays a big role."},
    "monza":         {"lat": 45.6156,  "lng": 9.2811,    "name": "Autodromo Nazionale Monza",
                      "type": "permanent", "drs_zones": 2, "overtaking": "high",
                      "tire_deg": "low",   "power_sensitive": True,
                      "characteristics": "Temple of Speed. Minimal downforce setup. Slipstreaming makes qualifying unpredictable."},
    "baku":          {"lat": 40.3725,  "lng": 49.8533,   "name": "Baku City Circuit",
                      "type": "street",    "drs_zones": 2, "overtaking": "high",
                      "tire_deg": "low",   "power_sensitive": True,
                      "characteristics": "Longest straight on the calendar. High-speed walls keep risk high. Safety car/VSC almost certain."},
    "singapore":     {"lat": 1.2914,   "lng": 103.8640,  "name": "Marina Bay Street Circuit",
                      "type": "street",    "drs_zones": 3, "overtaking": "low",
                      "tire_deg": "medium","power_sensitive": False,
                      "characteristics": "Night race in extreme humidity and heat. Very physical for drivers. Safety car very likely."},
    "austin":        {"lat": 30.1328,  "lng": -97.6411,  "name": "Circuit of the Americas",
                      "type": "permanent", "drs_zones": 2, "overtaking": "medium",
                      "tire_deg": "medium","power_sensitive": False,
                      "characteristics": "Copy of classic corners from around the world. Long back straight for overtaking. Bumpy surface."},
    "mexico":        {"lat": 19.4042,  "lng": -99.0907,  "name": "Autodromo Hermanos Rodriguez",
                      "type": "permanent", "drs_zones": 3, "overtaking": "medium",
                      "tire_deg": "low",   "power_sensitive": True,
                      "characteristics": "High altitude (2,200m) reduces engine power and aero efficiency. Unique stadium section. Low tire wear."},
    "brazil":        {"lat": -23.7036, "lng": -46.6997,  "name": "Autodromo Jose Carlos Pace",
                      "type": "permanent", "drs_zones": 2, "overtaking": "high",
                      "tire_deg": "medium","power_sensitive": True,
                      "characteristics": "Anti-clockwise layout. Ibirapuera causes violent rain storms. Good overtaking opportunities on the long straight."},
    "las_vegas":     {"lat": 36.1699,  "lng": -115.1398, "name": "Las Vegas Strip Circuit",
                      "type": "street",    "drs_zones": 2, "overtaking": "high",
                      "tire_deg": "medium","power_sensitive": True,
                      "characteristics": "Night race on the famous Strip. Very cold temperatures in November affect tire warm-up."},
    "qatar":         {"lat": 25.4900,  "lng": 51.4542,   "name": "Lusail International Circuit",
                      "type": "permanent", "drs_zones": 1, "overtaking": "medium",
                      "tire_deg": "very_high","power_sensitive": False,
                      "characteristics": "Extreme tire degradation. Brutal heat demands exceptional tire management. Very physically demanding."},
    "abu_dhabi":     {"lat": 24.4672,  "lng": 54.6031,   "name": "Yas Marina Circuit",
                      "type": "permanent", "drs_zones": 2, "overtaking": "medium",
                      "tire_deg": "medium","power_sensitive": True,
                      "characteristics": "Season finale. Twilight race into night. Redesigned in 2021 to allow more overtaking."},
}


def call_grok(system_prompt, user_prompt, max_tokens=1500):
    if not GROK_API_KEY:
        raise EnvironmentError("GROK_API_KEY not set. export GROK_API_KEY=your_key_here")
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROK_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": max_tokens,
    }
    resp = requests.post(GROK_API_URL, headers=headers, json=payload, timeout=40)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def call_gemini(system_prompt, user_prompt, max_tokens=1500):
    if not GEMINI_API_KEY:
        raise EnvironmentError("GEMINI_API_KEY not set. export GEMINI_API_KEY=your_key_here")
    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": max_tokens,
        }
    }
    resp = requests.post(url, json=payload, timeout=40)
    resp.raise_for_status()
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def call_llm(system_prompt, user_prompt, max_tokens=1500):
    if LLM_BACKEND == "gemini":
        return call_gemini(system_prompt, user_prompt, max_tokens)
    return call_grok(system_prompt, user_prompt, max_tokens)


def parse_json(raw):
    cleaned = raw.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"raw_text": raw}


def find_circuit(name):
    name_lower = name.lower().replace(" ", "_")
    for key, data in CIRCUITS.items():
        if key in name_lower or name_lower in key or name_lower in data["name"].lower():
            return {**data, "key": key}
    return None


def step1_parse_query(state):
    print("\n[Step 1] Parsing user query...")

    system_prompt = (
        "You are a query parser for an F1 race analytics system.\n"
        "Extract structured information from the user's F1 question.\n"
        "Respond ONLY with valid JSON — no markdown, no preamble.\n\n"
        "JSON format:\n"
        "{\n"
        '  "driver":      "driver surname or null if general query",\n'
        '  "team":        "constructor name or null",\n'
        '  "grand_prix":  "GP name or circuit location or null for general/next race",\n'
        '  "focus":       "one of: race_prediction | driver_performance | car_analytics | weather_impact | all",\n'
        '  "season":      "current or a 4-digit year"\n'
        "}"
    )
    user_prompt = f"Parse this F1 query:\n\n{state['user_query']}"

    raw = call_llm(system_prompt, user_prompt)
    state["parsed_query"] = parse_json(raw)
    print(f"  -> Parsed: {state['parsed_query']}")
    return state


def step2_fetch_f1_data(state):
    print("\n[Step 2] Fetching F1 data from Jolpica API...")

    try:
        collected = {}

        r = requests.get(f"{F1_API_BASE}/current/driverStandings.json", timeout=10)
        r.raise_for_status()
        standings_raw = r.json()
        standings_list = (
            standings_raw.get("MRData", {})
                         .get("StandingsTable", {})
                         .get("StandingsLists", [{}])[0]
                         .get("DriverStandings", [])
        )
        collected["driver_standings"] = [
            {
                "position":    int(s["position"]),
                "driver":      f"{s['Driver']['givenName']} {s['Driver']['familyName']}",
                "nationality": s["Driver"]["nationality"],
                "team":        s["Constructors"][0]["name"] if s.get("Constructors") else "N/A",
                "points":      float(s["points"]),
                "wins":        int(s["wins"]),
            }
            for s in standings_list[:10]
        ]
        print(f"  -> Driver standings: {len(collected['driver_standings'])} entries")

        r2 = requests.get(f"{F1_API_BASE}/current/constructorStandings.json", timeout=10)
        r2.raise_for_status()
        con_raw = r2.json()
        con_list = (
            con_raw.get("MRData", {})
                   .get("StandingsTable", {})
                   .get("StandingsLists", [{}])[0]
                   .get("ConstructorStandings", [])
        )
        collected["constructor_standings"] = [
            {
                "position": int(c["position"]),
                "team":     c["Constructor"]["name"],
                "points":   float(c["points"]),
                "wins":     int(c["wins"]),
            }
            for c in con_list[:10]
        ]
        print(f"  -> Constructor standings: {len(collected['constructor_standings'])} entries")

        r3 = requests.get(f"{F1_API_BASE}/current/last/results.json", timeout=10)
        r3.raise_for_status()
        last_raw = r3.json()
        race_info = last_raw.get("MRData", {}).get("RaceTable", {}).get("Races", [{}])[0]
        results_raw = race_info.get("Results", [])
        collected["last_race"] = {
            "name":    race_info.get("raceName", "Unknown"),
            "circuit": race_info.get("Circuit", {}).get("circuitName", "Unknown"),
            "date":    race_info.get("date", "Unknown"),
            "results": [
                {
                    "position": int(res["position"]),
                    "driver":   f"{res['Driver']['givenName']} {res['Driver']['familyName']}",
                    "team":     res["Constructor"]["name"],
                    "time":     res.get("Time", {}).get("time", res.get("status", "N/A")),
                    "points":   float(res.get("points", 0)),
                    "grid":     int(res.get("grid", 0)),
                    "laps":     int(res.get("laps", 0)),
                    "fastest_lap": res.get("FastestLap", {}).get("Time", {}).get("time", "N/A"),
                }
                for res in results_raw[:10]
            ],
        }
        print(f"  -> Last race: {collected['last_race']['name']}")

        r4 = requests.get(f"{F1_API_BASE}/current/next.json", timeout=10)
        r4.raise_for_status()
        next_raw = r4.json()
        next_races = next_raw.get("MRData", {}).get("RaceTable", {}).get("Races", [{}])
        if next_races:
            nr = next_races[0]
            collected["next_race"] = {
                "name":    nr.get("raceName", "Unknown"),
                "circuit": nr.get("Circuit", {}).get("circuitName", "Unknown"),
                "date":    nr.get("date", "Unknown"),
                "time":    nr.get("time", "Unknown"),
                "lat":     float(nr.get("Circuit", {}).get("Location", {}).get("lat", 0)),
                "lng":     float(nr.get("Circuit", {}).get("Location", {}).get("long", 0)),
                "locality": nr.get("Circuit", {}).get("Location", {}).get("locality", "Unknown"),
                "country": nr.get("Circuit", {}).get("Location", {}).get("country", "Unknown"),
                "round":   nr.get("round", "?"),
            }
            print(f"  -> Next race: {collected['next_race']['name']} on {collected['next_race']['date']}")
        else:
            collected["next_race"] = {}
            print("  -> No upcoming race found (end of season?)")

        state["raw_f1_data"] = collected
        state["tool_error"] = None

    except requests.exceptions.RequestException as exc:
        state["raw_f1_data"] = {}
        state["tool_error"] = f"F1 API error: {exc}"
        print(f"  x Error: {exc}")

    return state


def step3_fetch_weather(state):
    print("\n[Step 3] Fetching circuit weather forecast...")

    next_race = state.get("raw_f1_data", {}).get("next_race", {})
    circuit_name = next_race.get("circuit", "")
    circuit_info = find_circuit(circuit_name) or find_circuit(next_race.get("locality", ""))

    lat = circuit_info["lat"] if circuit_info else next_race.get("lat", 0)
    lng = circuit_info["lng"] if circuit_info else next_race.get("lng", 0)

    if not lat and not lng:
        state["weather_data"] = {"error": "No coordinates", "circuit_profile": circuit_info}
        state["weather_error"] = "No coordinates available"
        return state

    try:
        params = {
            "latitude": lat,
            "longitude": lng,
            "hourly": "temperature_2m,precipitation_probability,windspeed_10m,relativehumidity_2m",
            "forecast_days": 7,
            "timezone": "auto",
        }
        r = requests.get(WEATHER_BASE, params=params, timeout=10)
        r.raise_for_status()
        wx = r.json()
        hourly = wx.get("hourly", {})

        temps = hourly.get("temperature_2m", [])
        rain  = hourly.get("precipitation_probability", [])
        wind  = hourly.get("windspeed_10m", [])
        humid = hourly.get("relativehumidity_2m", [])

        def safe_avg(lst): return round(sum(lst) / len(lst), 1) if lst else None
        def safe_min(lst): return round(min(lst), 1) if lst else None
        def safe_max(lst): return round(max(lst), 1) if lst else None

        state["weather_data"] = {
            "temperature_c": {"min": safe_min(temps), "max": safe_max(temps), "avg": safe_avg(temps)},
            "rain_probability_pct": {"min": safe_min(rain), "max": safe_max(rain), "avg": safe_avg(rain)},
            "wind_kmh": {"min": safe_min(wind), "max": safe_max(wind), "avg": safe_avg(wind)},
            "humidity_avg_pct": safe_avg(humid),
            "circuit_profile": circuit_info,
        }
        state["weather_error"] = None
        print(f"  -> Weather: {safe_min(temps)}-{safe_max(temps)}C, rain avg {safe_avg(rain)}%")

    except requests.exceptions.RequestException as exc:
        state["weather_data"]  = {"error": str(exc), "circuit_profile": circuit_info}
        state["weather_error"] = f"Weather API error: {exc}"
        print(f"  x Weather error: {exc}")
    except Exception as exc:
        state["weather_data"]  = {"error": str(exc)}
        state["weather_error"] = f"Unexpected weather error: {exc}"

    return state


def step4_analyze_driver_performance(state):
    print("\n[Step 4] Analysing driver performance...")

    if state.get("tool_error") and not state.get("raw_f1_data"):
        state["driver_analysis"] = {"error": state["tool_error"]}
        return state

    system_prompt = (
        "You are an expert F1 analyst with deep knowledge of driver performance metrics.\n"
        "Analyse driver championship standings and recent race results.\n"
        "Respond ONLY with valid JSON — no markdown, no extra text.\n\n"
        "Required JSON:\n"
        "{\n"
        '  "championship_leader": "name",\n'
        '  "title_contenders": ["name1", "name2", "name3"],\n'
        '  "in_form_drivers": [\n'
        '    {"driver": "name", "team": "team", "form_assessment": "brief analysis", "strengths": ["s1"]}\n'
        "  ],\n"
        '  "constructor_battle": "2-3 sentences on team fight",\n'
        '  "standout_last_race": {"driver": "name", "notable": "what they did"},\n'
        '  "drivers_to_watch": ["name1", "name2"]\n'
        "}"
    )
    user_prompt = (
        f"User query: {state['user_query']}\n"
        f"Specific driver focus: {state['parsed_query'].get('driver', 'none')}\n\n"
        f"Driver Standings:\n{json.dumps(state['raw_f1_data'].get('driver_standings', []), indent=2)}\n\n"
        f"Constructor Standings:\n{json.dumps(state['raw_f1_data'].get('constructor_standings', []), indent=2)}\n\n"
        f"Last Race Results:\n{json.dumps(state['raw_f1_data'].get('last_race', {}), indent=2)}\n\n"
        "Provide a detailed driver performance analysis."
    )

    raw = call_llm(system_prompt, user_prompt)
    state["driver_analysis"] = parse_json(raw)
    print(f"  -> Championship leader: {state['driver_analysis'].get('championship_leader', 'N/A')}")
    return state


def step5_analyze_track_and_weather(state):
    print("\n[Step 5] Analysing track characteristics and weather impact...")

    system_prompt = (
        "You are an F1 race strategist and aerodynamicist.\n"
        "Analyse how track characteristics and weather conditions favour specific teams and cars.\n"
        "Respond ONLY with valid JSON — no markdown, no extra text.\n\n"
        "Required JSON:\n"
        "{\n"
        '  "circuit_summary": "2 sentences on what makes this circuit unique",\n'
        '  "favoured_car_type": "high_downforce | low_downforce | balanced",\n'
        '  "weather_conditions": "dry | wet | mixed | uncertain",\n'
        '  "weather_risk": "low | medium | high",\n'
        '  "weather_impact": "how weather affects the race and strategy",\n'
        '  "tire_strategy": {\n'
        '    "likely_stops": 1,\n'
        '    "preferred_compound": "soft/medium/hard",\n'
        '    "deg_risk": "low | medium | high | very_high"\n'
        "  },\n"
        '  "teams_favoured": ["team1", "team2"],\n'
        '  "teams_disadvantaged": ["team1"],\n'
        '  "safety_car_probability": "low | medium | high",\n'
        '  "key_strategic_factor": "the single biggest variable for this race"\n'
        "}"
    )
    user_prompt = (
        f"Circuit weather forecast:\n{json.dumps(state.get('weather_data', {}), indent=2)}\n\n"
        f"Constructor standings:\n{json.dumps(state['raw_f1_data'].get('constructor_standings', [])[:6], indent=2)}\n\n"
        f"Next race: {json.dumps(state['raw_f1_data'].get('next_race', {}), indent=2)}\n\n"
        "Analyse how the circuit and weather shape the race."
    )

    raw = call_llm(system_prompt, user_prompt)
    state["track_analysis"] = parse_json(raw)
    print(f"  -> Conditions: {state['track_analysis'].get('weather_conditions', 'N/A')} | SC: {state['track_analysis'].get('safety_car_probability', 'N/A')}")
    return state


def step6_generate_odds_and_car_analytics(state):
    print("\n[Step 6] Generating win probabilities and car analytics...")

    system_prompt = (
        "You are an F1 data scientist producing race prediction analytics.\n"
        "Combine driver form, car performance, circuit suitability, and weather into predictions.\n"
        "Respond ONLY with valid JSON — no markdown, no extra text.\n\n"
        "IMPORTANT: win_probability values must sum to exactly 100 across all drivers.\n\n"
        "Required JSON:\n"
        "{\n"
        '  "win_probabilities": [\n'
        '    {"driver": "name", "team": "team", "win_probability_pct": 0.0,\n'
        '     "podium_probability_pct": 0.0, "key_factor": "why"}\n'
        "  ],\n"
        '  "car_performance_scores": [\n'
        '    {"team": "name", "overall_score": 0, "power_unit": 0,\n'
        '     "aerodynamics": 0, "reliability": 0, "circuit_fit_score": 0, "note": "brief"}\n'
        "  ],\n"
        '  "dark_horse": {"driver": "name", "reason": "why they could surprise"},\n'
        '  "prediction_confidence": "low | medium | high",\n'
        '  "key_uncertainties": ["uncertainty1", "uncertainty2"]\n'
        "}\n\nAll scores are out of 100."
    )
    user_prompt = (
        f"Driver performance analysis:\n{json.dumps(state.get('driver_analysis', {}), indent=2)}\n\n"
        f"Track & weather analysis:\n{json.dumps(state.get('track_analysis', {}), indent=2)}\n\n"
        f"Driver standings:\n{json.dumps(state['raw_f1_data'].get('driver_standings', [])[:8], indent=2)}\n\n"
        f"Constructor standings:\n{json.dumps(state['raw_f1_data'].get('constructor_standings', [])[:6], indent=2)}\n\n"
        "Generate win probabilities and car performance scores."
    )

    raw = call_llm(system_prompt, user_prompt, max_tokens=2000)
    state["odds_and_analytics"] = parse_json(raw)
    top = (state["odds_and_analytics"].get("win_probabilities") or [{}])[0]
    print(f"  -> Top pick: {top.get('driver','?')} ({top.get('win_probability_pct','?')}%)")
    return state


def step7_generate_report(state):
    print("\n[Step 7] Writing final race analytics report...")

    system_prompt = (
        "You are a senior F1 journalist writing a professional pre-race analytics report.\n"
        "Write engaging, expert-level analysis in Markdown format.\n"
        "Include Markdown tables for win probabilities and car performance scores.\n\n"
        "Structure the report as:\n\n"
        "# [Race Name] - F1 Race Analytics Report\n"
        "*Round X | [Circuit] | [Date] | Generated: [timestamp]*\n\n"
        "## Championship Context\n"
        "## Driver Form Analysis\n"
        "## Circuit & Weather Analysis\n"
        "## Win Probability Estimates\n"
        "(Markdown table: Driver | Team | Win % | Podium % | Key Factor)\n"
        "## Car Performance Analytics\n"
        "(Markdown table: Team | Overall | Power Unit | Aero | Reliability | Circuit Fit)\n"
        "## Race Strategy Outlook\n"
        "## Key Takeaways\n"
        "(5 bullet points)"
    )
    user_prompt = (
        f"Original question: {state['user_query']}\n\n"
        f"Next race: {json.dumps(state['raw_f1_data'].get('next_race', {}))}\n\n"
        f"Driver analysis: {json.dumps(state.get('driver_analysis', {}), indent=2)}\n\n"
        f"Track & weather: {json.dumps(state.get('track_analysis', {}), indent=2)}\n\n"
        f"Odds & car analytics: {json.dumps(state.get('odds_and_analytics', {}), indent=2)}\n\n"
        "Write the complete race analytics report."
    )

    state["final_report"] = call_llm(system_prompt, user_prompt, max_tokens=2500)
    print("  -> Report complete")
    return state


def save_output(state):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    gp = (
        state.get("raw_f1_data", {})
             .get("next_race", {})
             .get("name", "f1")
             .replace(" ", "_")
             .lower()
    )
    md_path   = f"f1_report_{gp}_{ts}.md"
    json_path = f"f1_state_{gp}_{ts}.json"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(state.get("final_report", "No report generated."))

    state_copy = {k: v for k, v in state.items() if k != "final_report"}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(state_copy, f, indent=2, default=str)

    print(f"\n  Report saved -> {md_path}")
    print(f"  State saved  -> {json_path}")
    return md_path


def run_agent(user_query):
    print("\n" + "=" * 60)
    print(f"  F1 RACE ANALYTICS AGENT  [backend: {LLM_BACKEND.upper()}]")
    print("=" * 60)
    print(f"  Query: {user_query}")

    state = {
        "user_query":          user_query,
        "parsed_query":        {},
        "raw_f1_data":         {},
        "weather_data":        {},
        "driver_analysis":     {},
        "track_analysis":      {},
        "odds_and_analytics":  {},
        "final_report":        "",
        "tool_error":          None,
        "weather_error":       None,
        "timestamp":           datetime.now().isoformat(),
        "llm_backend":         LLM_BACKEND,
    }

    state = step1_parse_query(state)
    state = step2_fetch_f1_data(state)
    state = step3_fetch_weather(state)
    state = step4_analyze_driver_performance(state)
    state = step5_analyze_track_and_weather(state)
    state = step6_generate_odds_and_car_analytics(state)
    state = step7_generate_report(state)

    save_output(state)

    print("\n" + "=" * 60)
    print("  FINAL REPORT")
    print("=" * 60)
    print(state["final_report"])

    return state


if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        print("\nF1 Race Analytics Agent")
        print("Set LLM_BACKEND=gemini or LLM_BACKEND=grok (default)")
        print("Examples:")
        print("  Who will win the Monaco Grand Prix?")
        print("  Analyse Verstappen's chances at Silverstone")
        print("  Give me a full race preview for the next F1 race\n")
        query = input("Your question: ").strip()
        if not query:
            query = "Give me a full race preview and win predictions for the next F1 Grand Prix"

    run_agent(query)
