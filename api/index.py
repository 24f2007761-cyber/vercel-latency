import json
from pathlib import Path

import numpy as np
from fastapi import FastAPI, Request, Response

app = FastAPI()


@app.middleware("http")
async def add_cors(request: Request, call_next):
    if request.method == "OPTIONS":
        response = Response(status_code=200)
    else:
        response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept"
    response.headers["Access-Control-Expose-Headers"] = "Access-Control-Allow-Origin"
    return response


DATA = json.loads((Path(__file__).resolve().parent.parent / "telemetry.json").read_text())


@app.get("/api/latency")
def latency_get():
    return {"status": "ok", "usage": "POST {regions: [...], threshold_ms: N}"}


@app.post("/api/latency")
def latency(body: dict):
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)
    out = {}
    for r in regions:
        rows = [d for d in DATA if d["region"] == r]
        if not rows:
            continue
        lat = np.array([d["latency_ms"] for d in rows])
        up = np.array([d["uptime_pct"] for d in rows])
        out[r] = {
            "avg_latency": round(float(lat.mean()), 3),
            "p95_latency": round(float(np.percentile(lat, 95)), 3),
            "avg_uptime": round(float(up.mean()), 3),
            "breaches": int((lat > threshold).sum()),
        }
    return {"regions": out, **out}