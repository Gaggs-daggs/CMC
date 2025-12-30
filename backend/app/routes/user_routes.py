from fastapi import APIRouter, HTTPException
from typing import List
import logging
from datetime import datetime

from app.models.schemas import (
    UserProfile,
    LanguageCode
)
from app.config import settings
from app.utils.database import db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/users", response_model=UserProfile)
async def create_user(user: UserProfile):
    """Create a new user profile"""
    try:
        database = db.get_db(settings.MONGODB_DB_NAME)
        
        # Check if user already exists
        existing_user = await database.users.find_one({"phone": user.phone})
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Insert user
        user_dict = user.model_dump()
        result = await database.users.insert_one(user_dict)
        
        logger.info(f"Created user: {user.phone}")
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}", response_model=UserProfile)
async def get_user(user_id: str):
    """Get user profile by ID"""
    try:
        database = db.get_db(settings.MONGODB_DB_NAME)
        
        # For simplicity, using phone as user_id
        user = await database.users.find_one({"phone": user_id})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Remove MongoDB _id field
        user.pop('_id', None)
        
        return UserProfile(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/users/{user_id}")
async def update_user(user_id: str, preferred_language: LanguageCode = None, age: int = None, gender: str = None):
    """Update user preferences"""
    try:
        database = db.get_db(settings.MONGODB_DB_NAME)
        
        # Build update dict
        update_fields = {}
        if preferred_language:
            update_fields["preferred_language"] = preferred_language
        if age:
            update_fields["age"] = age
        if gender:
            update_fields["gender"] = gender
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Update user
        result = await database.users.update_one(
            {"phone": user_id},
            {"$set": update_fields}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"Updated user: {user_id}")
        
        return {"status": "updated", "user_id": user_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))
