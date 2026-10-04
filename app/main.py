from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import URL
from .utils import encode_base62
from .cache import r, CACHE_TTL

Base.metadata.create_all(bind=engine)
app = FastAPI(title="URL Shortener")

class ShortenRequest(BaseModel):
    url: HttpUrl

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/shorten")
def shorten(req: ShortenRequest, db: Session = Depends(get_db)):
    row = URL(original_url=str(req.url))
    db.add(row)
    db.flush()                      # gets row.id without committing
    row.short_code = encode_base62(row.id + 100000)  # offset for longer codes
    db.commit()
    return {"short_code": row.short_code, "short_url": f"http://localhost:8000/{row.short_code}"}

@app.get("/{code}")
def redirect(code: str, db: Session = Depends(get_db)):
    cached = r.get(f"url:{code}")
    if cached:
        return RedirectResponse(cached, status_code=302)

    row = db.query(URL).filter(URL.short_code == code).first()
    if not row:
        raise HTTPException(status_code=404, detail="Short URL not found")

    r.set(f"url:{code}", row.original_url, ex=CACHE_TTL)
    return RedirectResponse(row.original_url, status_code=302)