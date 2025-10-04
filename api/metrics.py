from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import json

app = FastAPI()

# Enable CORS for POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/api/metrics")
async def metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    # Load telemetry bundle (e.g., telemetry.json in project)
    with open("telemetry.json", "r") as f:
        data = json.load(f)

    response = {}
    for region in regions:
        region_data = [r for r in data if r["region"] == region]
        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime"] for r in region_data]

        if latencies:
            avg_latency = float(np.mean(latencies))
            p95_latency = float(np.percentile(latencies, 95))
            breaches = sum(l > threshold for l in latencies)
            avg_uptime = float(np.mean(uptimes))

            response[region] = {
                "avg_latency": avg_latency,
                "p95_latency": p95_latency,
                "avg_uptime": avg_uptime,
                "breaches": breaches,
            }

    return response
