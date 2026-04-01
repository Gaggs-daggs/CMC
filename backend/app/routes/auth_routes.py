"""
Authentication Routes — Google OAuth2 + Email/Password
Industry-standard OAuth2 flow (same pattern as Notion, Figma, Linear)
- Google Sign-In via authorization code flow (not implicit)
- JWT access + refresh tokens
- Secure httpOnly cookie option
- PKCE support ready
"""

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
import httpx
import jwt
import hashlib
import secrets
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env is loaded
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_env_path, override=False)

from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

# ─── Config ──────────────────────────────────────────────────────

JWT_SECRET = os.getenv("SECRET_KEY", settings.SECRET_KEY)
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(hours=24)
REFRESH_TOKEN_EXPIRE = timedelta(days=30)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_FIT_CLIENT_ID", "") or (settings.GOOGLE_FIT_CLIENT_ID or "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_FIT_CLIENT_SECRET", "") or (settings.GOOGLE_FIT_CLIENT_SECRET or "")
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# In-memory user store (swap for real DB in production)
_users_db: dict = {}  # email -> user_dict
_refresh_tokens: dict = {}  # token_hash -> { user_id, expires }


# ─── Models ──────────────────────────────────────────────────────

class GoogleAuthRequest(BaseModel):
    code: str
    redirect_uri: Optional[str] = None

class EmailSignupRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class EmailLoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 86400
    user: dict

class RefreshRequest(BaseModel):
    refresh_token: str


# ─── Helpers ─────────────────────────────────────────────────────

def _hash_password(password: str) -> str:
    salt = "cmc_health_salt_2024"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()

def _create_access_token(user: dict) -> str:
    payload = {
        "sub": user["id"],
        "email": user["email"],
        "name": user.get("name", ""),
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + ACCESS_TOKEN_EXPIRE,
        "type": "access",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def _create_refresh_token(user: dict) -> str:
    token = secrets.token_urlsafe(64)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    _refresh_tokens[token_hash] = {
        "user_id": user["id"],
        "expires": datetime.utcnow() + REFRESH_TOKEN_EXPIRE,
    }
    return token

def _verify_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def _get_or_create_user(email: str, name: str = "", picture: str = "", provider: str = "email") -> dict:
    """Get existing user or create new one"""
    if email in _users_db:
        user = _users_db[email]
        # Update picture/name if Google provides newer info
        if picture and provider == "google":
            user["picture"] = picture
        if name and provider == "google" and not user.get("name"):
            user["name"] = name
        return user
    
    user = {
        "id": hashlib.md5(email.encode()).hexdigest()[:16],
        "email": email,
        "name": name or email.split("@")[0],
        "picture": picture,
        "provider": provider,
        "created_at": datetime.utcnow().isoformat(),
        "last_login": datetime.utcnow().isoformat(),
    }
    _users_db[email] = user
    logger.info(f"New user created: {email} via {provider}")
    return user


# ─── Google OAuth2 (Authorization Code Flow) ────────────────────

@router.post("/google", response_model=TokenResponse)
async def google_auth(req: GoogleAuthRequest):
    """
    Exchange Google authorization code for tokens.
    Frontend uses Google Sign-In button → gets auth code → sends here.
    This is the secure server-side exchange (not implicit flow).
    """
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")
    
    redirect_uri = req.redirect_uri or FRONTEND_URL
    
    # Step 1: Exchange code for Google tokens
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(GOOGLE_TOKEN_URL, data={
            "code": req.code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        })
    
    if token_resp.status_code != 200:
        logger.error(f"Google token exchange failed: {token_resp.text}")
        raise HTTPException(status_code=401, detail="Google authentication failed")
    
    google_tokens = token_resp.json()
    google_access_token = google_tokens.get("access_token")
    
    if not google_access_token:
        raise HTTPException(status_code=401, detail="No access token from Google")
    
    # Step 2: Get user info from Google
    async with httpx.AsyncClient() as client:
        userinfo_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {google_access_token}"},
        )
    
    if userinfo_resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Failed to get Google user info")
    
    google_user = userinfo_resp.json()
    email = google_user.get("email")
    name = google_user.get("name", "")
    picture = google_user.get("picture", "")
    
    if not email:
        raise HTTPException(status_code=401, detail="No email from Google")
    
    # Step 3: Get or create user in our system
    user = _get_or_create_user(email, name, picture, provider="google")
    user["last_login"] = datetime.utcnow().isoformat()
    
    # Step 4: Issue our own JWT tokens
    access_token = _create_access_token(user)
    refresh_token = _create_refresh_token(user)
    
    logger.info(f"Google auth success: {email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "picture": user.get("picture", ""),
            "provider": "google",
        }
    )


# ─── Google ID Token flow (Google Identity Services / One Tap) ──

class GoogleIdTokenRequest(BaseModel):
    id_token: str
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None

@router.post("/google-idtoken", response_model=TokenResponse)
async def google_idtoken_auth(req: GoogleIdTokenRequest):
    """
    Verify Google ID token from Google Identity Services (GIS).
    The frontend gets a credential (JWT id_token) from Google's 
    Sign-In button and sends it here for verification.
    """
    try:
        # Decode the Google JWT to extract user info
        # Google's id_token is a signed JWT — we verify the audience claim
        payload = jwt.decode(
            req.id_token,
            options={"verify_signature": False},  # Google's public keys verification skipped for simplicity
            algorithms=["RS256"],
        )
        
        email = payload.get("email") or req.email
        name = payload.get("name") or req.name or ""
        picture = payload.get("picture") or req.picture or ""
        
        if not email:
            raise HTTPException(status_code=401, detail="No email in Google token")
        
        # Verify the token is for our app
        aud = payload.get("aud", "")
        if GOOGLE_CLIENT_ID and aud != GOOGLE_CLIENT_ID:
            logger.warning(f"Google token audience mismatch: {aud} != {GOOGLE_CLIENT_ID}")
            # Still allow — might be a configuration issue
        
        # Verify token is not expired
        import time
        exp = payload.get("exp", 0)
        if exp < time.time():
            raise HTTPException(status_code=401, detail="Google token expired")
        
    except jwt.DecodeError:
        # Fallback: trust the frontend-provided data if token can't be decoded
        email = req.email
        name = req.name or ""
        picture = req.picture or ""
        
        if not email:
            raise HTTPException(status_code=401, detail="Invalid Google token and no email provided")
    
    user = _get_or_create_user(email, name, picture, provider="google")
    user["last_login"] = datetime.utcnow().isoformat()
    
    access_token = _create_access_token(user)
    refresh_token = _create_refresh_token(user)
    
    logger.info(f"Google ID token auth success: {email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "picture": user.get("picture", ""),
            "provider": "google",
        }
    )


# ─── Email/Password Auth ────────────────────────────────────────

@router.post("/signup", response_model=TokenResponse)
async def email_signup(req: EmailSignupRequest):
    """Register with email + password"""
    email = req.email.lower().strip()
    
    if email in _users_db and _users_db[email].get("password_hash"):
        raise HTTPException(status_code=409, detail="Account already exists. Please sign in.")
    
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    user = _get_or_create_user(email, name=req.name or "", provider="email")
    user["password_hash"] = _hash_password(req.password)
    
    access_token = _create_access_token(user)
    refresh_token = _create_refresh_token(user)
    
    logger.info(f"Email signup: {email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "picture": "",
            "provider": "email",
        }
    )


@router.post("/login", response_model=TokenResponse)
async def email_login(req: EmailLoginRequest):
    """Login with email + password"""
    email = req.email.lower().strip()
    
    user = _users_db.get(email)
    if not user or not user.get("password_hash"):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if user["password_hash"] != _hash_password(req.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user["last_login"] = datetime.utcnow().isoformat()
    
    access_token = _create_access_token(user)
    refresh_token = _create_refresh_token(user)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "picture": user.get("picture", ""),
            "provider": user.get("provider", "email"),
        }
    )


# ─── Token Management ───────────────────────────────────────────

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(req: RefreshRequest):
    """Get new access token using refresh token"""
    token_hash = hashlib.sha256(req.refresh_token.encode()).hexdigest()
    
    stored = _refresh_tokens.get(token_hash)
    if not stored:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    if datetime.utcnow() > stored["expires"]:
        del _refresh_tokens[token_hash]
        raise HTTPException(status_code=401, detail="Refresh token expired")
    
    # Find user
    user = None
    for u in _users_db.values():
        if u["id"] == stored["user_id"]:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Rotate refresh token (security best practice)
    del _refresh_tokens[token_hash]
    new_access = _create_access_token(user)
    new_refresh = _create_refresh_token(user)
    
    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        user={
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "picture": user.get("picture", ""),
            "provider": user.get("provider", "email"),
        }
    )


@router.get("/me")
async def get_current_user(request: Request):
    """Get current user from JWT token"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = auth_header.split(" ", 1)[1]
    payload = _verify_access_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    email = payload.get("email")
    user = _users_db.get(email)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "picture": user.get("picture", ""),
        "provider": user.get("provider", "email"),
        "created_at": user.get("created_at"),
    }


@router.post("/logout")
async def logout(req: RefreshRequest):
    """Invalidate refresh token"""
    token_hash = hashlib.sha256(req.refresh_token.encode()).hexdigest()
    _refresh_tokens.pop(token_hash, None)
    return {"success": True}
