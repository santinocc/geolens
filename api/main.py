"""The GeoLens API. Run from the project folder:

    .venv/bin/uvicorn api.main:app --port 8001 --reload

Interactive docs, generated from the code: http://localhost:8001/docs
"""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from api.db import get_conn, open_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Code before the yield runs at startup, code after it at shutdown."""
    app.state.pool = open_pool()
    yield
    app.state.pool.close()


app = FastAPI(title="GeoLens API", lifespan=lifespan)


@app.get("/health")
def health(conn=Depends(get_conn)):
    """Checks that the API can reach the database."""
    conn.execute("SELECT 1")
    return {"status": "ok"}
