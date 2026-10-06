import json
from pathlib import Path

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA = json.loads((Path(__file__).resolve().parent.parent / "telemetry.json").read_text())


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
    return {"regions": out}