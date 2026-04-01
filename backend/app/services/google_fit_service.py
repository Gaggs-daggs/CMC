"""
Google Fit Integration Service
Fetches real health data from Google Fit API (heart rate, steps, sleep, calories, etc.)
Works with any smartwatch that syncs to Google Fit (via Apple Health, Samsung Health, Mi Fitness, etc.)
"""

import httpx
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import json

logger = logging.getLogger(__name__)

# Google Fit data source types
GOOGLE_FIT_DATA_TYPES = {
    "heart_rate": "com.google.heart_rate.bpm",
    "steps": "com.google.step_count.delta",
    "calories": "com.google.calories.expended",
    "distance": "com.google.distance.delta",
    "sleep": "com.google.sleep.segment",
    "weight": "com.google.weight",
    "blood_pressure": "com.google.blood_pressure",
    "oxygen_saturation": "com.google.oxygen_saturation",
    "body_temperature": "com.google.body.temperature",
    "active_minutes": "com.google.active_minutes",
    "heart_minutes": "com.google.heart_minutes",
}

# Sleep stage mapping
SLEEP_STAGES = {
    1: "Awake (during sleep)",
    2: "Sleep",
    3: "Out-of-bed",
    4: "Light sleep",
    5: "Deep sleep",
    6: "REM sleep",
}


class GoogleFitService:
    """Service to interact with Google Fit REST API"""

    TOKEN_URL = "https://oauth2.googleapis.com/token"
    FIT_BASE_URL = "https://www.googleapis.com/fitness/v1/users/me"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    async def exchange_code_for_tokens(self, code: str, redirect_uri: str) -> Dict:
        """Exchange authorization code for access + refresh tokens"""
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.TOKEN_URL, data={
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            })
            if resp.status_code != 200:
                logger.error(f"Token exchange failed: {resp.text}")
                raise Exception(f"Token exchange failed: {resp.text}")
            return resp.json()

    async def refresh_access_token(self, refresh_token: str) -> Dict:
        """Refresh an expired access token"""
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.TOKEN_URL, data={
                "refresh_token": refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
            })
            if resp.status_code != 200:
                logger.error(f"Token refresh failed: {resp.text}")
                raise Exception(f"Token refresh failed: {resp.text}")
            return resp.json()

    def _time_millis(self, dt: datetime) -> int:
        """Convert datetime to milliseconds since epoch"""
        return int(dt.timestamp() * 1000)

    def _nanos(self, dt: datetime) -> int:
        """Convert datetime to nanoseconds since epoch"""
        return int(dt.timestamp() * 1_000_000_000)

    async def _fetch_dataset(
        self,
        access_token: str,
        data_type: str,
        start_time: datetime,
        end_time: datetime,
        data_source_id: str = None,
    ) -> Dict:
        """Fetch a dataset from Google Fit for a given data type and time range.
        If data_source_id is provided, it filters to that specific source (for deduplication)."""
        start_ns = self._nanos(start_time)
        end_ns = self._nanos(end_time)

        # Use the aggregate endpoint for better data
        url = f"{self.FIT_BASE_URL}/dataset:aggregate"
        aggregate_spec = {"dataTypeName": data_type}
        if data_source_id:
            aggregate_spec["dataSourceId"] = data_source_id

        body = {
            "aggregateBy": [aggregate_spec],
            "bucketByTime": {"durationMillis": 86400000},  # 1 day buckets
            "startTimeMillis": self._time_millis(start_time),
            "endTimeMillis": self._time_millis(end_time),
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                json=body,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=15.0,
            )
            if resp.status_code == 401:
                raise Exception("TOKEN_EXPIRED")
            if resp.status_code != 200:
                logger.error(f"Google Fit API error ({data_type}): {resp.status_code} {resp.text}")
                return {"bucket": []}
            return resp.json()

    async def _fetch_raw_dataset(
        self,
        access_token: str,
        data_type: str,
        start_time: datetime,
        end_time: datetime,
    ) -> Dict:
        """Fetch raw (non-aggregated) data points — useful for heart rate timeline"""
        url = f"{self.FIT_BASE_URL}/dataset:aggregate"
        # Use 15-minute buckets for detailed data
        body = {
            "aggregateBy": [{"dataTypeName": data_type}],
            "bucketByTime": {"durationMillis": 900000},  # 15 min buckets
            "startTimeMillis": self._time_millis(start_time),
            "endTimeMillis": self._time_millis(end_time),
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                json=body,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=15.0,
            )
            if resp.status_code != 200:
                return {"bucket": []}
            return resp.json()

    # ─── Public Data Methods ─────────────────────────────────────────

    async def get_heart_rate(
        self, access_token: str, days: int = 1
    ) -> Dict:
        """Get heart rate data (avg, min, max, timeline)"""
        end = datetime.utcnow()
        start = end - timedelta(days=days)

        # Get daily aggregate
        data = await self._fetch_dataset(
            access_token, GOOGLE_FIT_DATA_TYPES["heart_rate"], start, end
        )

        # Get detailed timeline (15-min buckets for today)
        today_start = end.replace(hour=0, minute=0, second=0, microsecond=0)
        timeline_data = await self._fetch_raw_dataset(
            access_token, GOOGLE_FIT_DATA_TYPES["heart_rate"], today_start, end
        )

        # Parse aggregate
        hr_values = []
        for bucket in data.get("bucket", []):
            for dataset in bucket.get("dataset", []):
                for point in dataset.get("point", []):
                    for val in point.get("value", []):
                        if "fpVal" in val:
                            hr_values.append(val["fpVal"])

        # Parse timeline
        timeline = []
        for bucket in timeline_data.get("bucket", []):
            bucket_start = int(bucket.get("startTimeMillis", 0))
            for dataset in bucket.get("dataset", []):
                for point in dataset.get("point", []):
                    for val in point.get("value", []):
                        if "fpVal" in val:
                            timeline.append({
                                "time": datetime.fromtimestamp(bucket_start / 1000).strftime("%H:%M"),
                                "value": round(val["fpVal"])
                            })

        result = {
            "current": round(hr_values[-1]) if hr_values else None,
            "average": round(sum(hr_values) / len(hr_values)) if hr_values else None,
            "min": round(min(hr_values)) if hr_values else None,
            "max": round(max(hr_values)) if hr_values else None,
            "resting": round(min(hr_values)) if hr_values else None,  # Approximate
            "timeline": timeline[-24:],  # Last 24 data points
            "unit": "bpm",
            "data_points": len(hr_values),
        }
        return result

    async def get_steps(self, access_token: str, days: int = 7) -> Dict:
        """Get step count data using Google's merged/estimated source to avoid double-counting.
        
        Google Fit can have multiple step sources (phone accelerometer, watch, etc.).
        The aggregate API with estimated_steps or merge_step_deltas gives the deduplicated total
        matching what the Google Fit app shows.
        """
        end = datetime.utcnow()
        start = end - timedelta(days=days)

        # Try estimated_steps first (Google's best dedup), fall back to merge
        data = await self._fetch_dataset(
            access_token,
            GOOGLE_FIT_DATA_TYPES["steps"],
            start,
            end,
            data_source_id="derived:com.google.step_count.delta:com.google.android.gms:estimated_steps",
        )

        # Check if we got any data
        has_data = False
        for bucket in data.get("bucket", []):
            for dataset in bucket.get("dataset", []):
                if dataset.get("point"):
                    has_data = True
                    break

        if not has_data:
            # Fallback: use merge_step_deltas 
            logger.info("estimated_steps returned no data, trying merge_step_deltas")
            data = await self._fetch_dataset(
                access_token,
                GOOGLE_FIT_DATA_TYPES["steps"],
                start,
                end,
                data_source_id="derived:com.google.step_count.delta:com.google.android.gms:merge_step_deltas",
            )

        daily_steps = []
        total_steps = 0
        for bucket in data.get("bucket", []):
            bucket_start = int(bucket.get("startTimeMillis", 0))
            day_steps = 0
            for dataset in bucket.get("dataset", []):
                for point in dataset.get("point", []):
                    for val in point.get("value", []):
                        if "intVal" in val:
                            day_steps += val["intVal"]
                        elif "fpVal" in val:
                            day_steps += int(val["fpVal"])
            daily_steps.append({
                "date": datetime.fromtimestamp(bucket_start / 1000).strftime("%Y-%m-%d"),
                "day": datetime.fromtimestamp(bucket_start / 1000).strftime("%a"),
                "steps": day_steps,
            })
            total_steps += day_steps

        today_steps = daily_steps[-1]["steps"] if daily_steps else 0

        return {
            "today": today_steps,
            "total_week": total_steps,
            "average": round(total_steps / max(len(daily_steps), 1)),
            "daily": daily_steps,
            "goal": 10000,
            "goal_percent": min(round((today_steps / 10000) * 100), 100),
        }

    async def get_calories(self, access_token: str, days: int = 7) -> Dict:
        """Get calories burned data. 
        Google Fit API returns TOTAL calories (BMR + active). 
        Google Fit app shows only active calories, so we fetch BMR separately and subtract."""
        end = datetime.utcnow()
        start = end - timedelta(days=days)

        # Fetch total calories (includes BMR + active)
        total_data = await self._fetch_dataset(
            access_token,
            GOOGLE_FIT_DATA_TYPES["calories"],
            start,
            end,
            data_source_id="derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended",
        )

        # Fetch BMR calories separately
        bmr_data = await self._fetch_dataset(
            access_token,
            "com.google.calories.bmr",
            start,
            end,
            data_source_id="derived:com.google.calories.bmr:com.google.android.gms:merged",
        )

        # Parse BMR per day
        bmr_per_day = {}
        for bucket in bmr_data.get("bucket", []):
            bucket_start = int(bucket.get("startTimeMillis", 0))
            day_key = datetime.fromtimestamp(bucket_start / 1000).strftime("%Y-%m-%d")
            day_bmr = 0
            for dataset in bucket.get("dataset", []):
                for point in dataset.get("point", []):
                    for val in point.get("value", []):
                        if "fpVal" in val:
                            day_bmr += val["fpVal"]
            bmr_per_day[day_key] = day_bmr

        daily_calories = []
        total = 0
        for bucket in total_data.get("bucket", []):
            bucket_start = int(bucket.get("startTimeMillis", 0))
            day_key = datetime.fromtimestamp(bucket_start / 1000).strftime("%Y-%m-%d")
            day_cal = 0
            for dataset in bucket.get("dataset", []):
                for point in dataset.get("point", []):
                    for val in point.get("value", []):
                        if "fpVal" in val:
                            day_cal += val["fpVal"]
            
            # Subtract BMR to get active-only calories (matching Google Fit app)
            bmr = bmr_per_day.get(day_key, 0)
            active_cal = max(0, day_cal - bmr)
            
            daily_calories.append({
                "date": day_key,
                "day": datetime.fromtimestamp(bucket_start / 1000).strftime("%a"),
                "calories": round(active_cal),
            })
            total += active_cal

        return {
            "today": daily_calories[-1]["calories"] if daily_calories else 0,
            "total_week": round(total),
            "average": round(total / max(len(daily_calories), 1)),
            "daily": daily_calories,
        }

    async def get_sleep(self, access_token: str, days: int = 7) -> Dict:
        """Get sleep data using the Sessions API (more reliable for sleep than aggregate)"""
        end = datetime.utcnow()
        start = end - timedelta(days=days)

        # Try Sessions API first (activity type 72 = sleep)
        sessions_url = (
            f"{self.FIT_BASE_URL}/sessions"
            f"?startTime={start.strftime('%Y-%m-%dT%H:%M:%S.000Z')}"
            f"&endTime={end.strftime('%Y-%m-%dT%H:%M:%S.000Z')}"
            f"&activityType=72"
        )

        sleep_sessions = []
        total_sleep_mins = 0
        deep_sleep_mins = 0
        rem_sleep_mins = 0
        light_sleep_mins = 0

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                sessions_url,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=15.0,
            )
            if resp.status_code == 200:
                sessions = resp.json().get("session", [])
                for session in sessions:
                    start_ms = int(session.get("startTimeMillis", 0))
                    end_ms = int(session.get("endTimeMillis", 0))
                    duration_mins = (end_ms - start_ms) / (1000 * 60)
                    total_sleep_mins += duration_mins
                    sleep_sessions.append({
                        "stage": "Sleep",
                        "stage_code": 2,
                        "duration_minutes": round(duration_mins),
                        "start": datetime.fromtimestamp(start_ms / 1000).isoformat(),
                        "end": datetime.fromtimestamp(end_ms / 1000).isoformat(),
                    })

        # Also try the aggregate API for sleep segment details (deep/rem/light)
        data = await self._fetch_dataset(
            access_token, GOOGLE_FIT_DATA_TYPES["sleep"], start, end
        )

        segment_total = 0
        for bucket in data.get("bucket", []):
            for dataset in bucket.get("dataset", []):
                for point in dataset.get("point", []):
                    start_ns = int(point.get("startTimeNanos", 0))
                    end_ns = int(point.get("endTimeNanos", 0))
                    stage = point.get("value", [{}])[0].get("intVal", 2)
                    duration_mins = (end_ns - start_ns) / (1_000_000_000 * 60)

                    if stage == 5:
                        deep_sleep_mins += duration_mins
                    elif stage == 6:
                        rem_sleep_mins += duration_mins
                    elif stage == 4:
                        light_sleep_mins += duration_mins

                    if stage in [2, 4, 5, 6]:
                        segment_total += duration_mins

        # Use the larger value between sessions and segments
        if segment_total > total_sleep_mins:
            total_sleep_mins = segment_total

        return {
            "last_night_hours": round(total_sleep_mins / 60, 1) if total_sleep_mins else None,
            "last_night_minutes": total_sleep_mins,
            "deep_sleep_minutes": deep_sleep_mins,
            "rem_sleep_minutes": rem_sleep_mins,
            "light_sleep_minutes": light_sleep_mins,
            "sleep_score": min(100, round((total_sleep_mins / 480) * 100)) if total_sleep_mins else None,  # 8hr = 100%
            "sessions": sleep_sessions[-20:],  # Last 20 segments
        }

    async def get_oxygen_saturation(self, access_token: str, days: int = 1) -> Dict:
        """Get SpO2 data (if available from watch)"""
        end = datetime.utcnow()
        start = end - timedelta(days=days)

        data = await self._fetch_dataset(
            access_token, GOOGLE_FIT_DATA_TYPES["oxygen_saturation"], start, end
        )

        spo2_values = []
        for bucket in data.get("bucket", []):
            for dataset in bucket.get("dataset", []):
                for point in dataset.get("point", []):
                    for val in point.get("value", []):
                        if "fpVal" in val:
                            spo2_values.append(val["fpVal"])

        return {
            "current": round(spo2_values[-1], 1) if spo2_values else None,
            "average": round(sum(spo2_values) / len(spo2_values), 1) if spo2_values else None,
            "min": round(min(spo2_values), 1) if spo2_values else None,
            "available": len(spo2_values) > 0,
            "unit": "%",
        }

    async def get_all_vitals(self, access_token: str) -> Dict:
        """Fetch all vitals in one call — used by the dashboard"""
        try:
            # Fetch all data types in parallel-ish (sequential for simplicity)
            heart_rate = await self.get_heart_rate(access_token, days=1)
            steps = await self.get_steps(access_token, days=7)
            calories = await self.get_calories(access_token, days=7)
            sleep = await self.get_sleep(access_token, days=7)
            spo2 = await self.get_oxygen_saturation(access_token, days=1)

            # Health analysis
            alerts = []
            if heart_rate.get("current"):
                if heart_rate["current"] < 50:
                    alerts.append({"type": "warning", "message": "Low heart rate detected (bradycardia)", "vital": "heart_rate"})
                elif heart_rate["current"] > 100:
                    alerts.append({"type": "warning", "message": "High heart rate detected (tachycardia)", "vital": "heart_rate"})

            if spo2.get("current") and spo2["current"] < 95:
                alerts.append({"type": "critical", "message": "Low blood oxygen - consult a doctor", "vital": "spo2"})

            if sleep.get("last_night_hours") and sleep["last_night_hours"] < 5:
                alerts.append({"type": "info", "message": "You slept less than 5 hours - try to rest more", "vital": "sleep"})

            return {
                "heart_rate": heart_rate,
                "steps": steps,
                "calories": calories,
                "sleep": sleep,
                "spo2": spo2,
                "alerts": alerts,
                "last_synced": datetime.utcnow().isoformat(),
                "source": "Google Fit",
            }

        except Exception as e:
            if "TOKEN_EXPIRED" in str(e):
                raise
            logger.error(f"Error fetching all vitals: {e}")
            raise


# Singleton instance (initialized when config is available)
google_fit_service: Optional[GoogleFitService] = None


def init_google_fit_service(client_id: str, client_secret: str):
    """Initialize the Google Fit service with credentials"""
    global google_fit_service
    if client_id and client_secret:
        google_fit_service = GoogleFitService(client_id, client_secret)
        logger.info("Google Fit service initialized")
    else:
        logger.warning("Google Fit credentials not configured — service disabled")
