"""
Medical Image Analysis Service using LLaVA Vision Model
Analyzes skin conditions, wounds, rashes, and other visible symptoms
"""
import ollama
import base64
import logging
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

VISION_MODEL = "llava:7b"

# Thread pool for running sync ollama calls
_executor = ThreadPoolExecutor(max_workers=2)

# OPTIMIZED: Shorter, more focused prompts for faster analysis
IMAGE_PROMPTS = {
    "scan": """Analyze this medical scan briefly:
1. Scan type (MRI/CT/X-ray)
2. Body region 
3. Key findings (normal or abnormal)
4. Urgency: ROUTINE/URGENT/CRITICAL
5. Recommended specialist

Keep response under 200 words. This is preliminary AI analysis only.""",

    "skin": """Analyze this skin condition briefly:
1. Describe appearance (size, color, texture)
2. Top 3 possible conditions
3. Severity: MILD/MODERATE/SEVERE
4. Action: HOME CARE / SEE DOCTOR / URGENT

Keep response under 150 words. Consult dermatologist for diagnosis.""",

    "wound": """Assess this wound briefly:
1. Wound type and size estimate
2. Signs of infection (yes/no)
3. Severity: MINOR/MODERATE/SEVERE
4. Care needed: HOME / CLINIC / EMERGENCY

Keep response under 150 words. Serious wounds need professional care.""",

    "general": """Analyze this health-related image briefly:
1. What you see
2. Possible conditions (top 2-3)
3. Severity level
4. Recommended action

Keep response under 150 words. This is AI analysis only - consult healthcare professionals."""
}

# Default fallback prompt
MEDICAL_IMAGE_PROMPT = IMAGE_PROMPTS["general"]


class ImageAnalysisService:
    def __init__(self, model: str = VISION_MODEL):
        self.model = model
    
    def _detect_image_type(self, context: str, image_type: str) -> str:
        """Auto-detect the best prompt type based on context"""
        context_lower = context.lower() if context else ""
        type_lower = image_type.lower() if image_type else ""
        
        # Check for medical scans
        scan_keywords = ["mri", "ct", "x-ray", "xray", "scan", "ultrasound", "pet", 
                        "brain", "tumor", "tumour", "cancer", "radiology", "imaging"]
        if any(word in context_lower or word in type_lower for word in scan_keywords):
            return "scan"
        
        # Check for wounds
        wound_keywords = ["wound", "cut", "burn", "laceration", "injury", "bleeding", 
                         "bite", "stitches", "healing"]
        if any(word in context_lower or word in type_lower for word in wound_keywords):
            return "wound"
        
        # Check for skin conditions
        skin_keywords = ["skin", "rash", "acne", "eczema", "psoriasis", "mole", 
                        "bump", "spot", "itchy", "dermatitis"]
        if any(word in context_lower or word in type_lower for word in skin_keywords):
            return "skin"
        
        # Default based on provided type
        if type_lower in IMAGE_PROMPTS:
            return type_lower
        
        return "general"
    
    async def analyze_image(
        self, 
        image_data: bytes, 
        context: str = "",
        image_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Analyze a medical image using LLaVA vision model
        
        Args:
            image_data: Raw image bytes
            context: Additional context from user (e.g., "this rash appeared 2 days ago")
            image_type: Type of image (skin, wound, scan, general)
        
        Returns:
            Analysis results with observations, possible conditions, and recommendations
        """
        try:
            # Convert image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Auto-detect the best prompt type
            detected_type = self._detect_image_type(context, image_type)
            prompt = IMAGE_PROMPTS.get(detected_type, IMAGE_PROMPTS["general"])
            
            logger.info(f"Using {detected_type} prompt for image analysis")
            
            # Add user context if provided
            if context:
                prompt += f"\n\nPatient notes: {context}"
            
            prompt += "\n\nAnalyze now:"
            
            # Call LLaVA model - OPTIMIZED for speed
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [image_base64]
                    }
                ],
                options={
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 400  # Reduced for faster response
                }
            )
            
            analysis_text = response['message']['content']
            
            # Parse the response to extract structured data
            result = self._parse_analysis(analysis_text, detected_type)
            result["raw_analysis"] = analysis_text
            result["success"] = True
            result["detected_type"] = detected_type
            
            logger.info(f"Image analysis completed successfully (type: {detected_type})")
            return result
            
        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "raw_analysis": "Unable to analyze image. Please try again.",
                "severity": "unknown",
                "action": "consult_doctor"
            }
    
    def _parse_analysis(self, text: str, detected_type: str = "general") -> Dict[str, Any]:
        """Parse the AI response to extract structured information"""
        result = {
            "observations": "",
            "possible_conditions": [],
            "severity": "unknown",
            "recommended_action": "consult_doctor",
            "home_care_tips": [],
            "image_type": detected_type
        }
        
        text_lower = text.lower()
        
        # Determine severity based on keywords
        if any(word in text_lower for word in ["critical", "emergency", "immediate", "life-threatening", "urgent care"]):
            result["severity"] = "critical"
            result["recommended_action"] = "emergency"
        elif any(word in text_lower for word in ["severe", "serious", "urgent", "tumor", "tumour", "cancer", "malignant"]):
            result["severity"] = "severe"
            result["recommended_action"] = "see_specialist"
        elif any(word in text_lower for word in ["moderate", "concerning", "doctor", "medical attention", "abnormal"]):
            result["severity"] = "moderate"
            result["recommended_action"] = "see_doctor"
        elif any(word in text_lower for word in ["mild", "minor", "home care", "self-care", "routine"]):
            result["severity"] = "mild"
            result["recommended_action"] = "self_care"
        
        # For scans, default to specialist recommendation
        if detected_type == "scan" and result["severity"] == "unknown":
            result["severity"] = "requires_specialist"
            result["recommended_action"] = "see_specialist"
        
        # Extract first meaningful observation
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 20 and not line.startswith('*') and not line.startswith('#') and not line.startswith('⚠️'):
                result["observations"] = line
                break
        
        return result
    
    async def analyze_from_file(self, file_path: str, context: str = "") -> Dict[str, Any]:
        """Analyze image from a file path"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"success": False, "error": "File not found"}
            
            image_data = path.read_bytes()
            
            # Determine image type from filename or extension
            image_type = "general"
            filename_lower = path.name.lower()
            if any(word in filename_lower for word in ["skin", "rash", "acne"]):
                image_type = "skin"
            elif any(word in filename_lower for word in ["wound", "cut", "burn"]):
                image_type = "wound"
            elif any(word in filename_lower for word in ["eye"]):
                image_type = "eye"
            
            return await self.analyze_image(image_data, context, image_type)
            
        except Exception as e:
            logger.error(f"File analysis error: {e}")
            return {"success": False, "error": str(e)}


# Global instance
image_analyzer = ImageAnalysisService()
