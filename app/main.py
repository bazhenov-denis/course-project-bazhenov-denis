# app/main.py
import json
import logging
import time
import uuid

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from starlette.middleware.base import BaseHTTPMiddleware

from .logger_utils import mask_pii

app = FastAPI(title="Notes API (minimal-secdev)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

logger = logging.getLogger("app")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(message)s"))
logger.setLevel(logging.INFO)
logger.addHandler(handler)


class CorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        corr = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.correlation_id = corr
        response = None
        try:
            response = await call_next(request)
            return response
        finally:
            duration_ms = int((time.time() - start) * 1000)
            log = {
                "ts": int(time.time()),
                "method": request.method,
                "path": request.url.path,
                "status": getattr(response, "status_code", 500),
                "duration_ms": duration_ms,
                "correlation_id": corr,
            }
            logger.info(json.dumps(mask_pii(log)))


app.add_middleware(CorrelationMiddleware)


def problem(
    request: Request, status: int, title: str, detail: str, type_: str = "about:blank"
):
    return JSONResponse(
        status_code=status,
        media_type="application/problem+json",
        content={
            "type": type_,
            "title": title,
            "status": status,
            "detail": detail,
            "instance": str(request.url),
            "correlation_id": getattr(request.state, "correlation_id", None),
        },
        headers={"X-Request-ID": getattr(request.state, "correlation_id", "")},
    )


@app.exception_handler(HTTPException)
async def http_exc_handler(request: Request, exc: HTTPException):
    return problem(request, exc.status_code, "HTTP error", str(exc.detail))


@app.exception_handler(RequestValidationError)
async def validation_exc_handler(request: Request, exc: RequestValidationError):
    return problem(request, 422, "Validation failed", detail=str(exc.errors()))


@app.exception_handler(Exception)
async def unhandled_exc_handler(request: Request, exc: Exception):
    return problem(request, 500, "Unhandled error", detail="Internal Server Error")


class NoteIn(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    body: str = Field(..., min_length=1, max_length=5000)
    tags: list[str] = Field(default_factory=list, max_items=8)

    @validator("tags", each_item=True)
    def tag_len(cls, v):
        if not (1 <= len(v) <= 20):
            raise ValueError("tag length must be 1..20")
        return v


class NoteOut(BaseModel):
    id: int
    title: str
    tags: list[str]


NOTES: list[dict] = []
COUNTER = 0


@app.get("/ping")
async def ping():
    return {"ok": True}


@app.post("/notes", response_model=NoteOut)
async def create_note(request: Request, note: NoteIn):
    global COUNTER
    COUNTER += 1
    row = {"id": COUNTER, "title": note.title, "body": note.body, "tags": note.tags}
    NOTES.append(row)
    logger.info(
        json.dumps(
            mask_pii(
                {
                    "event": "note_created",
                    "id": row["id"],
                    "correlation_id": request.state.correlation_id,
                }
            )
        )
    )
    return {"id": row["id"], "title": row["title"], "tags": row["tags"]}


@app.get("/notes")
async def list_notes(
    request: Request, limit: int = Query(10, ge=1, le=200), offset: int = Query(0, ge=0)
):
    end = offset + limit
    items = [
        {"id": n["id"], "title": n["title"], "tags": n["tags"]}
        for n in NOTES[offset:end]
    ]
    resp = JSONResponse(
        status_code=200,
        content={"items": items, "limit": limit, "offset": offset, "total": len(NOTES)},
    )
    resp.headers["X-Request-ID"] = getattr(request.state, "correlation_id", "")
    return resp
