"""
Medical Image Analysis Service using LLaVA Vision Model
Analyzes skin conditions, wounds, rashes, and other visible symptoms
"""
import ollama
import base64
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

VISION_MODEL = "llava:7b"

# Specialized prompts for different image types
IMAGE_PROMPTS = {
    "scan": """You are an expert medical imaging AI assistant. Analyze this medical scan (MRI, CT, X-ray, or ultrasound) carefully.

Provide your analysis in this EXACT format:

🔬 **IMAGE TYPE & REGION**
- Identify the type of scan (MRI, CT scan, X-ray, ultrasound, PET scan)
- Identify the body region being scanned (brain, chest, abdomen, spine, limb, etc.)
- Note the imaging plane if applicable (axial, sagittal, coronal)

📋 **DETAILED OBSERVATIONS**
- Describe all visible structures and their appearance
- Note any abnormalities, lesions, masses, or unusual findings
- Describe location, size estimates, and characteristics of any findings
- Compare to expected normal anatomy

⚠️ **POTENTIAL FINDINGS**
List possible conditions that could explain the observations:
- Finding 1: [condition] - [brief explanation]
- Finding 2: [condition] - [brief explanation]
- Finding 3: [condition] - [brief explanation]

🎯 **CLINICAL SIGNIFICANCE**
- Rate urgency: ROUTINE / URGENT / CRITICAL
- Explain why this rating was given

👨‍⚕️ **RECOMMENDED NEXT STEPS**
- What specialist should review this (neurologist, oncologist, radiologist, etc.)
- Any additional tests or imaging recommended
- Timeline for follow-up

⚠️ **IMPORTANT DISCLAIMER**: This is AI-assisted preliminary analysis ONLY. This is NOT a diagnosis. All medical imaging MUST be interpreted by a qualified radiologist or specialist physician. Do not make treatment decisions based on this analysis alone.""",

    "skin": """You are a dermatology AI assistant. Analyze this skin image carefully.

Provide your analysis in this EXACT format:

🔍 **VISUAL OBSERVATION**
- Location on body (if visible)
- Size, shape, and color of the condition
- Texture, borders, and distribution pattern
- Any secondary features (swelling, discharge, scaling)

📋 **POSSIBLE CONDITIONS** (list top 3-5)
- Condition 1: [name] - [likelihood: High/Medium/Low] - [key matching features]
- Condition 2: [name] - [likelihood: High/Medium/Low] - [key matching features]
- Condition 3: [name] - [likelihood: High/Medium/Low] - [key matching features]

⚠️ **SEVERITY ASSESSMENT**
- Rating: MILD / MODERATE / SEVERE
- Reasoning for this rating

💊 **RECOMMENDED ACTION**
- [ ] Self-care at home (if mild)
- [ ] See a dermatologist within 1-2 weeks
- [ ] See a doctor within a few days
- [ ] Seek immediate medical attention

🏠 **HOME CARE TIPS** (if applicable)
- Tip 1
- Tip 2
- Tip 3

⚠️ **DISCLAIMER**: This is AI analysis, NOT a diagnosis. Consult a dermatologist for proper evaluation.""",

    "wound": """You are a wound care AI assistant. Analyze this wound image carefully.

Provide your analysis in this EXACT format:

🔍 **WOUND ASSESSMENT**
- Type: Cut, Laceration, Burn, Abrasion, Puncture, Ulcer, Bite
- Location and estimated size
- Depth assessment: Superficial / Partial thickness / Full thickness
- Wound edges and surrounding tissue condition

📋 **OBSERVATIONS**
- Color of wound bed (pink, red, yellow, black, mixed)
- Signs of infection: Redness, swelling, pus, odor, warmth
- Bleeding status
- Tissue viability

⚠️ **SEVERITY ASSESSMENT**
- Rating: MINOR / MODERATE / SEVERE / CRITICAL
- Reasoning

🚨 **IMMEDIATE ACTION NEEDED**
- [ ] Can be treated at home
- [ ] Needs medical attention within 24 hours  
- [ ] Needs urgent care today
- [ ] EMERGENCY - Seek immediate care

💊 **WOUND CARE INSTRUCTIONS**
- Cleaning recommendations
- Dressing type suggested
- Signs to watch for

⚠️ **DISCLAIMER**: Serious wounds require professional medical evaluation. If in doubt, seek medical care.""",

    "general": """You are a medical AI assistant analyzing a health-related image.

Analyze this image carefully and provide your findings in this format:

🔍 **WHAT I SEE**
- Detailed description of the image
- Type of medical content (body part, condition, scan, etc.)
- All visible abnormalities or points of interest

📋 **ANALYSIS**
- Possible conditions or findings
- Key observations supporting each possibility
- Confidence level for each (High/Medium/Low)

⚠️ **SEVERITY**
- MILD / MODERATE / SEVERE / REQUIRES SPECIALIST
- Explanation

👨‍⚕️ **RECOMMENDATION**
- Self-care guidance if appropriate
- When to see a doctor
- What type of specialist if needed

⚠️ **DISCLAIMER**: This is AI analysis only. Always consult healthcare professionals for medical decisions."""
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
                prompt += f"\n\n📝 **Patient's Description**: {context}"
            
            prompt += "\n\nAnalyze this image now:"
            
            # Call LLaVA model
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
                    "temperature": 0.2,  # Lower temperature for medical accuracy
                    "top_p": 0.9,
                    "num_predict": 2000  # Allow longer responses for detailed analysis
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
