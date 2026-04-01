"""
Google Fit API Routes
Handles OAuth2 flow and vitals data fetching from Google Fit
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from typing import Optional
import logging
import json
import os
from datetime import datetime
from pathlib import Path

# Ensure .env is loaded regardless of CWD
from dotenv import load_dotenv
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_env_path, override=False)

from app.utils.database import db
from app.config import settings
from app.services.google_fit_service import google_fit_service, init_google_fit_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Google Fit OAuth2 scopes
SCOPES = [
    "https://www.googleapis.com/auth/fitness.heart_rate.read",
    "https://www.googleapis.com/auth/fitness.activity.read",
    "https://www.googleapis.com/auth/fitness.body.read",
    "https://www.googleapis.com/auth/fitness.sleep.read",
    "https://www.googleapis.com/auth/fitness.oxygen_saturation.read",
    "https://www.googleapis.com/auth/fitness.blood_pressure.read",
    "https://www.googleapis.com/auth/fitness.body_temperature.read",
]

# In-memory token storage (per user_id)
# In production, store encrypted tokens in database
_user_tokens = {}


def _get_client_id():
    return settings.GOOGLE_FIT_CLIENT_ID or os.getenv("GOOGLE_FIT_CLIENT_ID", "")

def _get_client_secret():
    return settings.GOOGLE_FIT_CLIENT_SECRET or os.getenv("GOOGLE_FIT_CLIENT_SECRET", "")

def _get_redirect_uri():
    return settings.GOOGLE_FIT_REDIRECT_URI or os.getenv("GOOGLE_FIT_REDIRECT_URI", "http://localhost:8000/api/v1/googlefit/callback")


def _ensure_service():
    """Ensure Google Fit service is initialized"""
    global google_fit_service
    cid = _get_client_id()
    csecret = _get_client_secret()
    logger.info(f"Google Fit _ensure_service: client_id={'SET' if cid else 'EMPTY'}, client_secret={'SET' if csecret else 'EMPTY'}, service={'EXISTS' if google_fit_service else 'NONE'}")
    if google_fit_service is None:
        init_google_fit_service(cid, csecret)
        # Re-import the singleton after initialization (init sets it in the service module's namespace)
        from app.services.google_fit_service import google_fit_service as _svc
        google_fit_service = _svc
    if google_fit_service is None:
        raise HTTPException(
            status_code=503,
            detail="Google Fit not configured. Set GOOGLE_FIT_CLIENT_ID and GOOGLE_FIT_CLIENT_SECRET environment variables."
        )


# ─── OAuth2 Flow ─────────────────────────────────────────────────

@router.get("/googlefit/auth-url")
async def get_auth_url(user_id: str, redirect_after: Optional[str] = None):
    """
    Get the Google OAuth2 authorization URL.
    Frontend calls this, then redirects the user to the returned URL.
    """
    if not _get_client_id():
        raise HTTPException(
            status_code=503,
            detail="Google Fit not configured. Please set up Google Cloud credentials."
        )

    # Build state parameter (includes user_id so we know who authorized)
    state = json.dumps({"user_id": user_id, "redirect": redirect_after or ""})

    scope_str = " ".join(SCOPES)
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={_get_client_id()}"
        f"&redirect_uri={_get_redirect_uri()}"
        f"&response_type=code"
        f"&scope={scope_str}"
        f"&access_type=offline"
        f"&prompt=consent"
        f"&state={state}"
    )

    return {"auth_url": auth_url, "configured": True}


@router.get("/googlefit/callback")
async def oauth_callback(code: str, state: Optional[str] = None):
    """
    Google OAuth2 callback — exchanges the code for tokens.
    After success, redirects back to the frontend.
    """
    _ensure_service()

    try:
        # Parse state
        state_data = json.loads(state) if state else {}
        user_id = state_data.get("user_id", "unknown")
        redirect_after = state_data.get("redirect", "")

        # Exchange code for tokens
        tokens = await google_fit_service.exchange_code_for_tokens(code, _get_redirect_uri())

        # Store tokens for this user
        _user_tokens[user_id] = {
            "access_token": tokens["access_token"],
            "refresh_token": tokens.get("refresh_token"),
            "expires_in": tokens.get("expires_in", 3600),
            "token_type": tokens.get("token_type", "Bearer"),
            "connected_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"Google Fit connected for user: {user_id}")

        # Redirect back to frontend
        frontend_url = redirect_after or "http://localhost:5173"
        return RedirectResponse(url=f"{frontend_url}?googlefit=connected&user_id={user_id}")

    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        frontend_url = "http://localhost:5173"
        return RedirectResponse(url=f"{frontend_url}?googlefit=error&message={str(e)}")


@router.get("/googlefit/status")
async def get_connection_status(user_id: str):
    """Check if a user has connected Google Fit"""
    is_connected = user_id in _user_tokens and _user_tokens[user_id].get("access_token")
    return {
        "connected": bool(is_connected),
        "connected_at": _user_tokens.get(user_id, {}).get("connected_at") if is_connected else None,
        "source": "Google Fit",
    }


@router.post("/googlefit/disconnect")
async def disconnect_google_fit(user_id: str):
    """Disconnect Google Fit for a user"""
    if user_id in _user_tokens:
        del _user_tokens[user_id]
        logger.info(f"Google Fit disconnected for user: {user_id}")
    return {"status": "disconnected"}


# ─── Data Endpoints ──────────────────────────────────────────────

async def _get_valid_token(user_id: str) -> str:
    """Get a valid access token for a user, refreshing if needed"""
    _ensure_service()

    if user_id not in _user_tokens:
        raise HTTPException(status_code=401, detail="Google Fit not connected. Please connect first.")

    token_data = _user_tokens[user_id]
    access_token = token_data["access_token"]

    return access_token


async def _handle_token_refresh(user_id: str) -> str:
    """Refresh the access token if expired"""
    _ensure_service()

    token_data = _user_tokens.get(user_id)
    if not token_data or not token_data.get("refresh_token"):
        raise HTTPException(status_code=401, detail="Google Fit session expired. Please reconnect.")

    try:
        new_tokens = await google_fit_service.refresh_access_token(token_data["refresh_token"])
        _user_tokens[user_id]["access_token"] = new_tokens["access_token"]
        if "refresh_token" in new_tokens:
            _user_tokens[user_id]["refresh_token"] = new_tokens["refresh_token"]
        return new_tokens["access_token"]
    except Exception as e:
        logger.error(f"Token refresh failed for {user_id}: {e}")
        del _user_tokens[user_id]
        raise HTTPException(status_code=401, detail="Google Fit session expired. Please reconnect.")


@router.get("/googlefit/vitals")
async def get_all_vitals(user_id: str):
    """
    Get all vitals from Google Fit — the main endpoint used by the dashboard.
    Returns heart rate, steps, calories, sleep, SpO2, and health alerts.
    """
    access_token = await _get_valid_token(user_id)

    try:
        vitals = await google_fit_service.get_all_vitals(access_token)
        return vitals
    except Exception as e:
        if "TOKEN_EXPIRED" in str(e):
            # Try refreshing
            new_token = await _handle_token_refresh(user_id)
            vitals = await google_fit_service.get_all_vitals(new_token)
            return vitals
        logger.error(f"Error fetching vitals for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch vitals: {str(e)}")


@router.get("/googlefit/heart-rate")
async def get_heart_rate(user_id: str, days: int = 1):
    """Get heart rate data"""
    access_token = await _get_valid_token(user_id)
    try:
        data = await google_fit_service.get_heart_rate(access_token, days)
        return data
    except Exception as e:
        if "TOKEN_EXPIRED" in str(e):
            new_token = await _handle_token_refresh(user_id)
            return await google_fit_service.get_heart_rate(new_token, days)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/googlefit/steps")
async def get_steps(user_id: str, days: int = 7):
    """Get steps data"""
    access_token = await _get_valid_token(user_id)
    try:
        data = await google_fit_service.get_steps(access_token, days)
        return data
    except Exception as e:
        if "TOKEN_EXPIRED" in str(e):
            new_token = await _handle_token_refresh(user_id)
            return await google_fit_service.get_steps(new_token, days)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/googlefit/sleep")
async def get_sleep(user_id: str, days: int = 7):
    """Get sleep data"""
    access_token = await _get_valid_token(user_id)
    try:
        data = await google_fit_service.get_sleep(access_token, days)
        return data
    except Exception as e:
        if "TOKEN_EXPIRED" in str(e):
            new_token = await _handle_token_refresh(user_id)
            return await google_fit_service.get_sleep(new_token, days)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/googlefit/calories")
async def get_calories(user_id: str, days: int = 7):
    """Get calories data"""
    access_token = await _get_valid_token(user_id)
    try:
        data = await google_fit_service.get_calories(access_token, days)
        return data
    except Exception as e:
        if "TOKEN_EXPIRED" in str(e):
            new_token = await _handle_token_refresh(user_id)
            return await google_fit_service.get_calories(new_token, days)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/googlefit/debug-sources")
async def debug_data_sources(user_id: str):
    """Debug endpoint: list all available data sources to understand what's syncing"""
    access_token = await _get_valid_token(user_id)
    _ensure_service()

    import httpx
    url = f"https://www.googleapis.com/fitness/v1/users/me/dataSources"
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            url,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=15.0,
        )
        if resp.status_code != 200:
            return {"error": resp.text}

        sources = resp.json().get("dataSource", [])
        # Summarize: show data type, device info, and stream name
        summary = []
        for src in sources:
            summary.append({
                "dataStreamId": src.get("dataStreamId", ""),
                "dataType": src.get("dataType", {}).get("name", ""),
                "device": src.get("device", {}).get("model", "unknown"),
                "manufacturer": src.get("device", {}).get("manufacturer", ""),
                "type": src.get("type", ""),
            })
        # Group by data type
        by_type = {}
        for s in summary:
            dt = s["dataType"]
            if dt not in by_type:
                by_type[dt] = []
            by_type[dt].append(s)

        return {
            "total_sources": len(summary),
            "by_type": by_type,
        }
