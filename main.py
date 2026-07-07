from fastapi import FastAPI, Request, Query
from fastapi.responses import Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import time
import uuid
from collections import deque
from datetime import datetime, timezone

app = FastAPI()

EMAIL = "24f2004664@ds.study.iitm.ac.in"

start_time = time.time()

logs = deque(maxlen=1000)

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests"
)


@app.middleware("http")
async def middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())

    http_requests_total.inc()

    logs.append({
        "level": "INFO",
        "ts": datetime.now(timezone.utc).isoformat(),
        "path": request.url.path,
        "request_id": request_id
    })

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


@app.get("/")
def home():
    return {
        "status": "running"
    }


@app.get("/work")
def work(n: int = Query(...)):
    # simulate K units of work
    total = 0
    for i in range(n):
        total += i

    return {
        "email": EMAIL,
        "done": n
    }


@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/healthz")
def health():
    return {
        "status": "ok",
        "uptime_s": time.time() - start_time
    }


@app.get("/logs/tail")
def log_tail(limit: int = 10):
    return list(logs)[-limit:]
