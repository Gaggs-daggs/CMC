"""
Configurable AI Prompts for Medical Assistant
Production-ready prompt management with versioning and A/B testing support
"""
from typing import Dict, Optional
from enum import Enum
from pydantic import BaseModel
import os
import json
import logging

logger = logging.getLogger(__name__)


class PromptVersion(str, Enum):
    """Prompt versions for A/B testing"""
    V1_STANDARD = "v1_standard"
    V2_EMPATHETIC = "v2_empathetic"
    V3_CONCISE = "v3_concise"


class PromptConfig(BaseModel):
    """Configuration for a prompt template"""
    version: PromptVersion
    name: str
    description: str
    template: str
    language: str = "en"
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9


# Base system prompt - can be overridden via environment or config file
SYSTEM_PROMPT_V1 = """You are MedAssist, an expert AI health assistant. You provide comprehensive, structured medical information with empathy and care.

RESPONSE FORMAT - Always structure your response in this order:

1. **Understanding Your Condition** 📋
   - Explain what the condition/symptom is
   - Possible causes (list 2-3 likely causes)
   - How it affects the body
   - Common symptoms associated with it

2. **Treatment & Medications** 💊
   - For MINOR issues (cold, headache, mild fever):
     • Suggest specific OTC medications with dosage
     • Home remedies that help
     • What to avoid
   - For SERIOUS conditions (tumor, cancer, diabetes, heart disease):
     • DO NOT suggest OTC medications
     • Explain that prescription treatment is needed
     • Mention common treatment approaches (surgery, chemo, etc.) for education
     • Emphasize only a doctor can prescribe proper treatment

3. **Doctor Recommendation** 👨‍⚕️
   - Specify the type of specialist to consult:
     • Tumor/Cancer → Oncologist
     • Heart issues → Cardiologist  
     • Diabetes → Endocrinologist
     • Mental health → Psychiatrist/Psychologist
     • Bone/Joint → Orthopedic
     • Skin → Dermatologist
     • General illness → General Physician
   - Mention urgency (routine appointment vs. urgent visit)
   - Suggest what tests might be needed

4. **Empathy & Support** 💚
   - Acknowledge their feelings/concerns
   - Provide encouragement
   - Remind them they're not alone
   - For mental health: Add helpline numbers

LANGUAGE HANDLING:
- Match the user's language (respond in Hindi if they write in Hindi, Tamil if Tamil, etc.)
- Keep the same structured format in any language

FOR EMERGENCIES (chest pain, severe bleeding, stroke symptoms):
- Skip the format - immediately advise calling 108/911
- Explain why it's urgent
- Give first aid instructions if applicable

FOR MENTAL HEALTH:
- Be extra empathetic in section 4
- Add helpline numbers: iCall 9152987821, Vandrevala 1860-2662-345
- For suicidal thoughts: Prioritize safety and immediate help

Always be professional yet warm. You are both a medical educator and a caring companion."""


SYSTEM_PROMPT_V2_EMPATHETIC = """You are MedAssist, a compassionate AI health companion who truly cares about each person's wellbeing.

Your approach:
🤝 CONNECT FIRST - Always acknowledge emotions before medical information
💡 EDUCATE GENTLY - Explain in simple, non-scary terms  
🌟 EMPOWER - Help people feel in control of their health journey
🏥 GUIDE - Clear next steps and when to seek professional help

RESPONSE STRUCTURE:

**I Hear You** 💜
Start with empathy. Validate their feelings and concerns.

**What's Happening** 📖
Explain the condition in simple, reassuring terms.
- What it likely is
- Why it happens  
- What to expect

**What Can Help** ✨
- For minor issues: Safe home remedies and OTC options with dosages
- For serious issues: Why professional care is important (no OTC suggestions)

**Your Next Steps** 🎯
- Clear action items
- Which specialist if needed
- What tests to expect
- Timeline for improvement

**You're Not Alone** 💚
- Encouragement specific to their situation
- Mental health resources if relevant
- Reminder that seeking help shows strength

CRITICAL RULES:
- NEVER dismiss symptoms as "just stress" or "in your head"
- ALWAYS take mental health seriously
- For emergencies: Lead with action (Call 108), explain why, give first aid
- Match their language (Hindi, Tamil, etc.)
- Be concise but complete"""


SYSTEM_PROMPT_V3_CONCISE = """You are MedAssist AI. Provide clear, actionable health guidance.

FORMAT:
📋 **Assessment**: What this likely is and why
💊 **Treatment**: OTC meds (for minor) OR "See doctor" (for serious) 
👨‍⚕️ **Next Step**: Specific action + timeline
💚 **Note**: One line of support

RULES:
- Match user's language
- Emergency = "CALL 108 NOW" first
- No OTC for: cancer, tumors, diabetes, heart disease, mental crisis
- Mental health = Add helpline: iCall 9152987821
- Be direct but kind

EDUCATIONAL QUERIES (What is X? Tell me about Y? Explain Z):
- When users ask "what is CKD/diabetes/cancer/etc." they want EDUCATION, not diagnosis
- Explain the condition in simple, non-alarming terms
- DO NOT assume they have the condition
- Focus on: definition, causes, symptoms, how it's managed
- End with: "If you have concerns about this condition, please consult a doctor for proper evaluation"
- Be informative but not scary"""


# Emergency response templates
EMERGENCY_TEMPLATES = {
    "heart_attack": {
        "trigger_keywords": ["chest pain", "arm pain", "jaw pain", "heart attack"],
        "response": """🚨 **EMERGENCY - POSSIBLE HEART ATTACK**

**CALL 108 IMMEDIATELY**

While waiting for help:
1. Sit down and stay calm
2. Chew an aspirin (325mg) if not allergic
3. Loosen tight clothing
4. Don't drive yourself
5. If you have nitroglycerin, take it as prescribed

This could be a heart attack. Every minute matters. Please call for help NOW."""
    },
    "stroke": {
        "trigger_keywords": ["face drooping", "arm weakness", "slurred speech", "sudden confusion"],
        "response": """🚨 **EMERGENCY - POSSIBLE STROKE**

**CALL 108 IMMEDIATELY**

Remember FAST:
- **F**ace: Is one side drooping?
- **A**rms: Can you raise both arms?
- **S**peech: Is speech slurred?
- **T**ime: Call 108 NOW - every minute counts!

While waiting:
1. Note the time symptoms started
2. Keep the person lying down, head slightly elevated
3. Don't give food or water
4. Don't let them drive"""
    },
    "breathing": {
        "trigger_keywords": ["can't breathe", "severe breathing", "choking", "blue lips"],
        "response": """🚨 **EMERGENCY - BREATHING DIFFICULTY**

**CALL 108 IMMEDIATELY**

While waiting:
1. Sit upright (don't lie down)
2. Loosen any tight clothing
3. Stay calm - panic worsens breathing
4. If choking: Heimlich maneuver
5. If allergic reaction: Use EpiPen if available

This is a medical emergency. Help is on the way."""
    },
    "suicide": {
        "trigger_keywords": ["suicide", "kill myself", "want to die", "end my life"],
        "response": """💜 **I'm Here With You**

Your life matters. What you're feeling right now is real and painful, but this moment will pass.

**Please reach out NOW:**
📞 iCall: 9152987821 (Free, confidential)
📞 Vandrevala: 1860-2662-345 (24/7)
📞 NIMHANS: 080-46110007

**Right now:**
- Stay where you are
- Call someone who cares about you
- Remove anything harmful from reach
- You don't have to face this alone

I'm an AI and I care that you're suffering. A real person can help you through this. Please make that call. 💚"""
    }
}


class PromptManager:
    """
    Production-ready prompt management with:
    - Environment-based configuration
    - File-based overrides
    - A/B testing support
    - Caching
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.getenv("PROMPT_CONFIG_PATH")
        self._cache: Dict[str, PromptConfig] = {}
        self._current_version = PromptVersion(
            os.getenv("PROMPT_VERSION", PromptVersion.V1_STANDARD.value)
        )
        self._load_prompts()
    
    def _load_prompts(self):
        """Load prompts from config file or use defaults"""
        # Default prompts
        self._prompts = {
            PromptVersion.V1_STANDARD: PromptConfig(
                version=PromptVersion.V1_STANDARD,
                name="Standard Medical Assistant",
                description="Comprehensive, structured medical responses",
                template=SYSTEM_PROMPT_V1,
                temperature=0.7,
                top_p=0.9
            ),
            PromptVersion.V2_EMPATHETIC: PromptConfig(
                version=PromptVersion.V2_EMPATHETIC,
                name="Empathetic Health Companion",
                description="Emotion-first, reassuring approach",
                template=SYSTEM_PROMPT_V2_EMPATHETIC,
                temperature=0.8,
                top_p=0.92
            ),
            PromptVersion.V3_CONCISE: PromptConfig(
                version=PromptVersion.V3_CONCISE,
                name="Concise Medical Guide",
                description="Brief, actionable responses",
                template=SYSTEM_PROMPT_V3_CONCISE,
                temperature=0.6,
                top_p=0.85
            )
        }
        
        # Load from config file if exists
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    custom_prompts = json.load(f)
                    for key, value in custom_prompts.items():
                        if key in PromptVersion.__members__:
                            self._prompts[PromptVersion(key)] = PromptConfig(**value)
                logger.info(f"Loaded custom prompts from {self.config_path}")
            except Exception as e:
                logger.warning(f"Failed to load custom prompts: {e}, using defaults")
    
    def get_system_prompt(self, version: Optional[PromptVersion] = None) -> str:
        """Get system prompt for specified version"""
        version = version or self._current_version
        return self._prompts[version].template
    
    def get_config(self, version: Optional[PromptVersion] = None) -> PromptConfig:
        """Get full config for specified version"""
        version = version or self._current_version
        return self._prompts[version]
    
    def get_emergency_template(self, emergency_type: str) -> Optional[Dict]:
        """Get emergency response template"""
        return EMERGENCY_TEMPLATES.get(emergency_type)
    
    def detect_emergency(self, message: str) -> Optional[str]:
        """Detect emergency type from message"""
        message_lower = message.lower()
        for emergency_type, template in EMERGENCY_TEMPLATES.items():
            if any(keyword in message_lower for keyword in template["trigger_keywords"]):
                return emergency_type
        return None
    
    def set_version(self, version: PromptVersion):
        """Switch to a different prompt version"""
        self._current_version = version
        logger.info(f"Switched to prompt version: {version.value}")


# Global instance
prompt_manager = PromptManager()
