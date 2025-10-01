from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"]
)

with open("q-vercel-latency.json") as f:
    telemetry = json.load(f)

@app.post("/latency")
async def latency_metrics(request: Request):
    body = await request.json()
    regions = body["regions"]
    threshold = body["threshold_ms"]
    result = {}
    for region in regions:
        records = telemetry.get(region, [])
        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime"] for r in records]
        breaches = sum(1 for l in latencies if l > threshold)
        result[region] = {
            "avg_latency": float(np.mean(latencies)) if latencies else 0,
            "p95_latency": float(np.percentile(latencies, 95)) if latencies else 0,
            "avg_uptime": float(np.mean(uptimes)) if uptimes else 0,
            "breaches": breaches
        }
    return result
