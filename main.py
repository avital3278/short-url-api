import string
import secrets
import io
import qrcode
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from database import get_db, engine
import models
from fastapi import Response, FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from auth import hash_password, verify_password, create_access_token, get_current_user, get_optional_user

# Initialize database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Short URL API", description="Production-ready API for shortening URLs")

# Rate limit storage: {ip_address: [timestamp1, ...]}
request_history: dict[str, list[datetime]] = {}

# --- Pydantic Models ---

class LinkIn(BaseModel):
    url: HttpUrl
    custom_alias: Optional[str] = None  # Optional custom alias for the short link

class LinkOut(BaseModel):
    short_code: str
    short_url: str

class UserCredentials(BaseModel):
    email: str
    password: str

# --- Helper Functions ---

def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))

# --- API Endpoints ---

@app.post("/links", response_model=LinkOut, status_code=201)
def create_link(payload: LinkIn, db: Session = Depends(get_db), current_email: str | None = Depends(get_optional_user)):
    # Rate Limiting
    now = datetime.now()
    history = [t for t in request_history.get("guest", []) if (now - t).total_seconds() < 60]
    if len(history) >= 5:
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a minute.")
    request_history["guest"] = history + [now]

    # Idempotency (only if the user didn't request a custom alias)
    if current_email and not payload.custom_alias:
        existing = db.query(models.Link).filter(models.Link.url == str(payload.url), models.Link.owner_email == current_email).first()
        if existing:
            return LinkOut(short_code=existing.short_code, short_url=f"http://127.0.0.1:8000/{existing.short_code}")

    # Custom Alias Logic & Generation
    if payload.custom_alias:
        # Check if the requested alias is already taken
        existing_alias = db.query(models.Link).filter(models.Link.short_code == payload.custom_alias).first()
        if existing_alias:
            raise HTTPException(status_code=409, detail="Alias already taken")
        code = payload.custom_alias
    else:
        # Generate a random code
        code = generate_short_code()
        while db.query(models.Link).filter(models.Link.short_code == code).first():
            code = generate_short_code()
    
    new_link = models.Link(short_code=code, url=str(payload.url), owner_email=current_email, clicks=0)
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return LinkOut(short_code=code, short_url=f"http://127.0.0.1:8000/{code}")

@app.get("/{code}")
def redirect_to_original(code: str, db: Session = Depends(get_db)):
    link_data = db.query(models.Link).filter(models.Link.short_code == code).first()
    if not link_data:
        raise HTTPException(status_code=404, detail="Short code not found")
    
    link_data.clicks += 1
    db.commit()
    return RedirectResponse(url=link_data.url, status_code=307)

@app.get("/{code}/qr")
def get_qr_code(code: str, db: Session = Depends(get_db)):
    link_data = db.query(models.Link).filter(models.Link.short_code == code).first()
    if not link_data:
        raise HTTPException(status_code=404, detail="Short code not found")
    
    img = qrcode.make(f"http://127.0.0.1:8000/{code}")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")

@app.post("/auth/register", status_code=201)
def register(credentials: UserCredentials, db: Session = Depends(get_db)): 
    if db.query(models.User).filter(models.User.email == credentials.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = models.User(email=credentials.email, hashed_password=hash_password(credentials.password))
    db.add(user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/auth/login")
def login(credentials: UserCredentials, db: Session = Depends(get_db)): 
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": credentials.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/links")
def get_my_links(db: Session = Depends(get_db), current_email: str = Depends(get_current_user)):
    return db.query(models.Link).filter(models.Link.owner_email == current_email).all()

@app.delete("/users/links/{code}")
def delete_link(code: str, db: Session = Depends(get_db), current_email: str = Depends(get_current_user)):
    link = db.query(models.Link).filter(models.Link.short_code == code).first()
    
    # Always return 404 to prevent resource enumeration (IDOR protection)
    if not link or link.owner_email != current_email:
        raise HTTPException(status_code=404, detail="Link not found")
    
    db.delete(link)
    db.commit()
    return {"message": "Link deleted"}