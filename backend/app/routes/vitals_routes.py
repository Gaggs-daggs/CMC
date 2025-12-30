from fastapi import APIRouter, HTTPException
from typing import List, Optional
import logging
from datetime import datetime

from app.models.schemas import (
    VitalsReading,
    SubmitVitalsRequest
)
from app.config import settings
from app.utils.database import db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/vitals")
async def submit_vitals(request: SubmitVitalsRequest):
    """Submit vitals reading from IoT sensors"""
    try:
        database = db.get_db(settings.MONGODB_DB_NAME)
        
        # Prepare vitals document
        vitals_doc = {
            "user_id": request.user_id,
            "heart_rate": request.vitals.heart_rate,
            "spo2": request.vitals.spo2,
            "temperature": request.vitals.temperature,
            "timestamp": request.vitals.timestamp,
            "device_id": request.vitals.device_id
        }
        
        # Insert into time-series collection
        await database.vitals_timeseries.insert_one(vitals_doc)
        
        logger.info(f"Stored vitals for user: {request.user_id}")
        
        # Analyze vitals for abnormalities
        alerts = analyze_vitals(request.vitals)
        
        return {
            "status": "success",
            "timestamp": request.vitals.timestamp,
            "alerts": alerts
        }
        
    except Exception as e:
        logger.error(f"Error storing vitals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vitals/{user_id}/latest")
async def get_latest_vitals(user_id: str) -> VitalsReading:
    """Get latest vitals reading for a user"""
    try:
        database = db.get_db(settings.MONGODB_DB_NAME)
        
        # Find most recent vitals
        vitals = await database.vitals_timeseries.find_one(
            {"user_id": user_id},
            sort=[("timestamp", -1)]
        )
        
        if not vitals:
            raise HTTPException(status_code=404, detail="No vitals found for user")
        
        # Remove MongoDB _id
        vitals.pop('_id', None)
        vitals.pop('user_id', None)
        
        return VitalsReading(**vitals)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching vitals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vitals/{user_id}/history")
async def get_vitals_history(user_id: str, limit: int = 100):
    """Get vitals history for a user"""
    try:
        database = db.get_db(settings.MONGODB_DB_NAME)
        
        # Find recent vitals
        cursor = database.vitals_timeseries.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit)
        
        vitals_list = []
        async for vitals in cursor:
            vitals.pop('_id', None)
            vitals.pop('user_id', None)
            vitals_list.append(VitalsReading(**vitals))
        
        return {"vitals": vitals_list, "count": len(vitals_list)}
        
    except Exception as e:
        logger.error(f"Error fetching vitals history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def analyze_vitals(vitals: VitalsReading) -> List[str]:
    """Analyze vitals for abnormalities"""
    alerts = []
    
    # Heart rate checks
    if vitals.heart_rate:
        if vitals.heart_rate < 60:
            alerts.append("Low heart rate detected (bradycardia)")
        elif vitals.heart_rate > 100:
            alerts.append("High heart rate detected (tachycardia)")
    
    # SpO2 checks
    if vitals.spo2:
        if vitals.spo2 < 95:
            alerts.append("Low blood oxygen level - seek medical attention")
        if vitals.spo2 < 90:
            alerts.append("⚠️ CRITICAL: Severe hypoxemia - emergency care needed")
    
    # Temperature checks
    if vitals.temperature:
        if vitals.temperature > 100.4:
            alerts.append("Fever detected")
        if vitals.temperature > 103:
            alerts.append("⚠️ High fever - medical attention recommended")
        if vitals.temperature < 95:
            alerts.append("⚠️ Low body temperature (hypothermia)")
    
    return alerts
