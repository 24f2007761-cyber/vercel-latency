from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import os
import json

app = FastAPI()

# Enable CORS for POST requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry data
data_path = os.path.join(os.path.dirname(__file__), "..", "telemetry.json")
with open(data_path) as f:
    data = json.load(f)

df = pd.DataFrame(data)
df = df.rename(columns={"uptime_pct": "uptime"})

# Request model
class MetricsRequest(BaseModel):
    regions: list[str]
    threshold_ms: float

# POST endpoint
@app.post("/")
async def latency_metrics(req: MetricsRequest):
    results = {}
    for region in req.regions:
        region_df = df[df["region"] == region]
        if region_df.empty:
            continue
        latencies = region_df["latency_ms"]
        uptimes = region_df["uptime"]

        results[region] = {
            "avg_latency": float(latencies.mean()),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(uptimes.mean()),
            "breaches": int((latencies > req.threshold_ms).sum())
        }
    return results
