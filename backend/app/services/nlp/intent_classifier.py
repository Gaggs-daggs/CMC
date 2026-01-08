"""
Intelligent Intent Classifier for Medical AI
Detects user intent and selects appropriate response strategy

Intent Categories:
1. SYMPTOM_REPORT - User describing symptoms they have
2. EDUCATIONAL - User asking what something is (what is CKD?)
3. MEDICATION_QUERY - Questions about medications
4. EMERGENCY - Crisis/emergency situations
5. FOLLOWUP - Follow-up questions in conversation
6. LIFESTYLE - Diet, exercise, prevention questions
7. MENTAL_HEALTH - Emotional/psychological concerns
8. GREETING - Hello, hi, thanks
9. CLARIFICATION - User asking to explain more
10. SECOND_OPINION - User questioning previous advice
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class UserIntent(Enum):
    """Types of user intents"""
    SYMPTOM_REPORT = "symptom_report"      # "I have headache"
    EDUCATIONAL = "educational"             # "What is diabetes?"
    MEDICATION_QUERY = "medication_query"   # "Can I take paracetamol?"
    EMERGENCY = "emergency"                 # "I'm having chest pain"
    FOLLOWUP = "followup"                   # "What about the dosage?"
    LIFESTYLE = "lifestyle"                 # "What foods should I avoid?"
    MENTAL_HEALTH = "mental_health"         # "I feel depressed"
    GREETING = "greeting"                   # "Hello", "Thank you"
    CLARIFICATION = "clarification"         # "Can you explain more?"
    SECOND_OPINION = "second_opinion"       # "Are you sure?"
    DIAGNOSIS_REQUEST = "diagnosis_request" # "Do I have cancer?"
    TEST_QUERY = "test_query"               # "What tests should I do?"
    PREVENTION = "prevention"               # "How to prevent diabetes?"
    SIDE_EFFECTS = "side_effects"           # "Side effects of aspirin?"
    UNKNOWN = "unknown"


@dataclass
class IntentResult:
    """Result of intent classification"""
    primary_intent: UserIntent
    confidence: float
    secondary_intent: Optional[UserIntent] = None
    detected_entities: Dict = None
    is_question: bool = False
    language_detected: str = "en"
    prompt_strategy: str = "standard"
    response_tone: str = "professional"
    should_ask_followup: bool = True
    medical_entities: List[str] = None


class IntelligentIntentClassifier:
    """
    Smart intent classifier that understands medical conversations
    Works with multiple languages (English, Hindi, Tamil, Telugu, etc.)
    """
    
    def __init__(self):
        # Question patterns in multiple languages
        self.question_patterns = {
            "en": [
                r"\bwhat\s+is\b", r"\bwhat\'s\b", r"\bwhat\s+are\b",
                r"\bhow\s+to\b", r"\bhow\s+do\b", r"\bhow\s+can\b",
                r"\bwhy\s+is\b", r"\bwhy\s+do\b", r"\bwhy\s+does\b",
                r"\bcan\s+i\b", r"\bshould\s+i\b", r"\bwill\s+it\b",
                r"\bis\s+it\b", r"\bare\s+there\b", r"\bdo\s+i\b",
                r"\btell\s+me\s+about\b", r"\bexplain\b", r"\bdescribe\b",
                r"\?$"
            ],
            "hi": [
                r"\bक्या\s+है\b", r"\bकैसे\b", r"\bक्यों\b", r"\bकब\b",
                r"\bकौन\b", r"\bकहाँ\b", r"\bबताओ\b", r"\bबताइए\b",
                r"\?$"
            ],
            "ta": [
                r"\bஎன்ன\b", r"\bஎப்படி\b", r"\bஏன்\b", r"\bஎங்கே\b",
                r"\bயார்\b", r"\bஎப்போது\b", r"\bசொல்லுங்கள்\b",
                r"என்றால்\s+என்ன", r"endral\s+enna", r"enna\b",
                r"\?$"
            ],
            "te": [
                r"\bఏమిటి\b", r"\bఎలా\b", r"\bఎందుకు\b", r"\bఎక్కడ\b",
                r"\bఎవరు\b", r"\bఎప్పుడు\b", r"\bచెప్పండి\b",
                r"\?$"
            ]
        }
        
        # Educational query patterns
        self.educational_patterns = [
            # English
            r"what\s+is\s+(\w+)", r"what\'s\s+(\w+)", r"tell\s+me\s+about\s+(\w+)",
            r"explain\s+(\w+)", r"meaning\s+of\s+(\w+)", r"define\s+(\w+)",
            r"(\w+)\s+means?\s+what", r"about\s+(\w+)",
            # Tamil transliteration
            r"(\w+)\s+endral\s+enna", r"(\w+)\s+enna", r"(\w+)\s+பற்றி",
            # Hindi transliteration  
            r"(\w+)\s+kya\s+hai", r"(\w+)\s+kya\s+hota\s+hai",
            # General
            r"information\s+(?:about|on)\s+(\w+)", r"details\s+(?:about|of)\s+(\w+)"
        ]
        
        # Symptom reporting patterns
        self.symptom_patterns = [
            # English
            r"\bi\s+have\b", r"\bi\'m\s+having\b", r"\bi\s+feel\b", r"\bi\'m\s+feeling\b",
            r"\bmy\s+(\w+)\s+(?:is|are|hurts?|aches?|pains?)\b",
            r"\bsuffering\s+from\b", r"\bexperiencing\b", r"\bgot\s+(?:a|the)?\b",
            r"\bthere\s+is\s+pain\b", r"\bpain\s+in\s+(?:my)?\b",
            # Tamil
            r"\bவலி\b", r"\bகஷ்டம்\b", r"\bதொந்தரவு\b",
            # Hindi
            r"\bदर्द\b", r"\bतकलीफ\b", r"\bपरेशानी\b",
            r"\bmujhe\b", r"\bमुझे\b"
        ]
        
        # Emergency patterns
        self.emergency_patterns = [
            r"\bchest\s+pain\b", r"\bcan\'?t\s+breathe\b", r"\bsevere\s+bleeding\b",
            r"\bunconscious\b", r"\bheart\s+attack\b", r"\bstroke\b",
            r"\bsuicid", r"\bkill\s+(?:my)?self\b", r"\bwant\s+to\s+die\b",
            r"\boverdose\b", r"\bpoisoning\b", r"\bchoking\b",
            r"\bसीने\s+में\s+दर्द\b", r"\bसांस\s+नहीं\b"
        ]
        
        # Medication query patterns
        self.medication_patterns = [
            r"\bcan\s+i\s+take\b", r"\bshould\s+i\s+take\b",
            r"\bdosage\b", r"\bhow\s+much\b", r"\bhow\s+many\b",
            r"\bside\s+effects?\b", r"\balternative\s+(?:to|for)\b",
            r"\bmedicine\s+for\b", r"\bdrug\s+for\b", r"\btablet\s+for\b",
            r"\bसाइड\s+इफेक्ट\b", r"\bदवाई\b", r"\bமருந்து\b"
        ]
        
        # Mental health patterns
        self.mental_health_patterns = [
            r"\bdepressed\b", r"\banxious\b", r"\bstressed\b", r"\bworried\b",
            r"\bpanic\b", r"\blonely\b", r"\bhopeless\b", r"\bsad\b",
            r"\bcan\'?t\s+sleep\b", r"\binsomnia\b", r"\bनींद\s+नहीं\b",
            r"\boverthinking\b", r"\bmental\s+health\b", r"\bதனிமை\b"
        ]
        
        # Lifestyle/prevention patterns
        self.lifestyle_patterns = [
            r"\bdiet\b", r"\bfood\s+(?:to|for)\b", r"\bexercise\b",
            r"\bprevent\b", r"\bavoid\b", r"\bhealthy\b",
            r"\bwhat\s+(?:to|should\s+i)\s+eat\b", r"\blifestyle\b",
            r"\bआहार\b", r"\bव्यायाम\b", r"\bஉணவு\b"
        ]
        
        # Greeting patterns (includes romanized and native script)
        self.greeting_patterns = [
            r"^(?:hi|hello|hey|good\s+(?:morning|afternoon|evening))[\s\!\.\,]*$",
            r"^(?:thanks?|thank\s+you|धन्यवाद|நன்றி|nandri|dhanyavaad)[\s\!\.\,]*$",
            r"^(?:bye|goodbye|ok|okay)[\s\!\.\,]*$",
            r"^(?:नमस्ते|namaste|வணக்கம்|vanakkam|vanakam)[\s\!\.\,]*$"
        ]
        
        # Medical condition entities (for educational queries)
        self.medical_conditions = [
            "ckd", "chronic kidney disease", "diabetes", "cancer", "tumor",
            "hypertension", "high blood pressure", "asthma", "copd",
            "arthritis", "thyroid", "cholesterol", "anemia", "migraine",
            "epilepsy", "parkinsons", "alzheimers", "hepatitis", "cirrhosis",
            "pneumonia", "tuberculosis", "tb", "hiv", "aids", "covid",
            "dengue", "malaria", "typhoid", "jaundice", "kidney stone",
            "gallstone", "hernia", "ulcer", "gastritis", "ibs", "crohns",
            "pcod", "pcos", "endometriosis", "fibroids"
        ]
        
        logger.info("✅ Intelligent Intent Classifier initialized")
    
    def classify(self, message: str, conversation_history: List[Dict] = None) -> IntentResult:
        """
        Classify user intent from message
        
        Args:
            message: User's message
            conversation_history: Previous messages for context
            
        Returns:
            IntentResult with detected intent and metadata
        """
        message_lower = message.lower().strip()
        
        # Detect language
        language = self._detect_language(message)
        
        # Check if it's a question
        is_question = self._is_question(message_lower, language)
        
        # Extract medical entities
        medical_entities = self._extract_medical_entities(message_lower)
        
        # Score each intent
        intent_scores = {
            UserIntent.EMERGENCY: self._score_emergency(message_lower),
            UserIntent.GREETING: self._score_greeting(message_lower),
            UserIntent.EDUCATIONAL: self._score_educational(message_lower, is_question, medical_entities),
            UserIntent.SYMPTOM_REPORT: self._score_symptom_report(message_lower),
            UserIntent.MEDICATION_QUERY: self._score_medication_query(message_lower),
            UserIntent.MENTAL_HEALTH: self._score_mental_health(message_lower),
            UserIntent.LIFESTYLE: self._score_lifestyle(message_lower),
            UserIntent.SIDE_EFFECTS: self._score_side_effects(message_lower),
            UserIntent.PREVENTION: self._score_prevention(message_lower),
        }
        
        # Get primary intent (highest score)
        primary_intent = max(intent_scores, key=intent_scores.get)
        primary_score = intent_scores[primary_intent]
        
        # If no strong match, check for followup or unknown
        if primary_score < 0.3:
            if conversation_history and len(conversation_history) > 0:
                primary_intent = UserIntent.FOLLOWUP
                primary_score = 0.5
            else:
                primary_intent = UserIntent.UNKNOWN
                primary_score = 0.3
        
        # Get secondary intent
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
        secondary_intent = sorted_intents[1][0] if len(sorted_intents) > 1 and sorted_intents[1][1] > 0.2 else None
        
        # Determine prompt strategy and tone
        prompt_strategy, response_tone = self._get_response_strategy(primary_intent, medical_entities)
        
        # Determine if we should ask follow-up
        should_ask_followup = primary_intent not in [UserIntent.GREETING, UserIntent.EMERGENCY, UserIntent.EDUCATIONAL]
        
        result = IntentResult(
            primary_intent=primary_intent,
            confidence=primary_score,
            secondary_intent=secondary_intent,
            detected_entities={"medical_terms": medical_entities},
            is_question=is_question,
            language_detected=language,
            prompt_strategy=prompt_strategy,
            response_tone=response_tone,
            should_ask_followup=should_ask_followup,
            medical_entities=medical_entities
        )
        
        logger.info(f"🎯 Intent: {primary_intent.value} ({primary_score:.2f}) | Strategy: {prompt_strategy} | Entities: {medical_entities}")
        
        return result
    
    def _detect_language(self, message: str) -> str:
        """Detect message language"""
        # Tamil characters
        if re.search(r'[\u0B80-\u0BFF]', message):
            return "ta"
        # Hindi/Devanagari characters
        if re.search(r'[\u0900-\u097F]', message):
            return "hi"
        # Telugu characters
        if re.search(r'[\u0C00-\u0C7F]', message):
            return "te"
        # Kannada characters
        if re.search(r'[\u0C80-\u0CFF]', message):
            return "kn"
        # Malayalam characters
        if re.search(r'[\u0D00-\u0D7F]', message):
            return "ml"
        # Bengali characters
        if re.search(r'[\u0980-\u09FF]', message):
            return "bn"
        return "en"
    
    def _is_question(self, message: str, language: str) -> bool:
        """Check if message is a question"""
        patterns = self.question_patterns.get(language, []) + self.question_patterns.get("en", [])
        for pattern in patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        return message.strip().endswith("?")
    
    def _extract_medical_entities(self, message: str) -> List[str]:
        """Extract medical condition names from message"""
        found = []
        for condition in self.medical_conditions:
            if condition in message:
                found.append(condition)
        return found
    
    def _score_emergency(self, message: str) -> float:
        """Score emergency intent"""
        for pattern in self.emergency_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return 1.0  # Emergency always takes priority
        return 0.0
    
    def _score_greeting(self, message: str) -> float:
        """Score greeting intent"""
        for pattern in self.greeting_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return 0.9
        return 0.0
    
    def _score_educational(self, message: str, is_question: bool, medical_entities: List[str]) -> float:
        """Score educational/informational intent"""
        score = 0.0
        
        # Strong educational patterns
        for pattern in self.educational_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                score = max(score, 0.8)
        
        # Questions about medical conditions
        if is_question and medical_entities:
            score = max(score, 0.7)
        
        # "What is X" pattern
        if re.search(r"what\s+(?:is|are)\s+\w+", message, re.IGNORECASE):
            score = max(score, 0.85)
        
        # Tamil "X endral enna" pattern
        if re.search(r"\w+\s+endral\s+enna", message, re.IGNORECASE):
            score = max(score, 0.9)
        
        return score
    
    def _score_symptom_report(self, message: str) -> float:
        """Score symptom reporting intent"""
        score = 0.0
        matches = 0
        
        for pattern in self.symptom_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                matches += 1
        
        if matches > 0:
            score = min(0.9, 0.4 + (matches * 0.15))
        
        return score
    
    def _score_medication_query(self, message: str) -> float:
        """Score medication query intent"""
        for pattern in self.medication_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return 0.8
        return 0.0
    
    def _score_mental_health(self, message: str) -> float:
        """Score mental health intent"""
        matches = 0
        for pattern in self.mental_health_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                matches += 1
        
        if matches > 0:
            return min(0.9, 0.5 + (matches * 0.15))
        return 0.0
    
    def _score_lifestyle(self, message: str) -> float:
        """Score lifestyle/prevention intent"""
        for pattern in self.lifestyle_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return 0.7
        return 0.0
    
    def _score_side_effects(self, message: str) -> float:
        """Score side effects query intent"""
        if re.search(r"side\s+effects?", message, re.IGNORECASE):
            return 0.85
        return 0.0
    
    def _score_prevention(self, message: str) -> float:
        """Score prevention query intent"""
        if re.search(r"\b(?:prevent|avoid|stop)\b.*\b(?:disease|condition|illness)\b", message, re.IGNORECASE):
            return 0.75
        if re.search(r"how\s+to\s+(?:prevent|avoid)", message, re.IGNORECASE):
            return 0.8
        return 0.0
    
    def _get_response_strategy(self, intent: UserIntent, medical_entities: List[str]) -> Tuple[str, str]:
        """Get appropriate response strategy and tone for intent"""
        
        strategies = {
            UserIntent.EMERGENCY: ("emergency_protocol", "urgent"),
            UserIntent.GREETING: ("friendly_greeting", "warm"),
            UserIntent.EDUCATIONAL: ("educational_explainer", "informative"),
            UserIntent.SYMPTOM_REPORT: ("symptom_assessment", "professional"),
            UserIntent.MEDICATION_QUERY: ("medication_advisor", "cautious"),
            UserIntent.MENTAL_HEALTH: ("mental_health_support", "empathetic"),
            UserIntent.LIFESTYLE: ("lifestyle_coach", "encouraging"),
            UserIntent.SIDE_EFFECTS: ("medication_info", "informative"),
            UserIntent.PREVENTION: ("prevention_educator", "motivational"),
            UserIntent.FOLLOWUP: ("contextual_followup", "helpful"),
            UserIntent.UNKNOWN: ("general_assistant", "friendly"),
        }
        
        return strategies.get(intent, ("general_assistant", "professional"))
    
    def get_prompt_for_intent(self, intent_result: IntentResult) -> str:
        """Generate appropriate system prompt based on intent"""
        
        prompts = {
            "emergency_protocol": """You are an EMERGENCY medical responder. 
The user may be in a crisis. Your ONLY job is to:
1. Tell them to CALL 108 (ambulance) IMMEDIATELY
2. Give brief first-aid instructions while waiting
3. Stay calm and reassuring
DO NOT ask questions. DO NOT delay with explanations. EMERGENCY FIRST.""",

            "friendly_greeting": """You are a friendly health assistant. 
The user is greeting you. Respond warmly and ask how you can help with their health today.
Keep it brief and welcoming. Ask what symptoms or health questions they have.""",

            "educational_explainer": f"""You are a medical EDUCATOR providing information.
The user is asking an EDUCATIONAL question about a medical topic. They want to LEARN, not get diagnosed.

IMPORTANT: The user is NOT saying they have this condition. They just want information.

Provide a clear, simple explanation that includes:
1. **What it is**: Simple definition in plain language
2. **Causes**: Common causes (briefly)
3. **Symptoms**: What someone with this might experience
4. **Treatment**: How it's generally managed (don't prescribe)
5. **When to see a doctor**: General guidance

Tone: Informative, educational, NOT alarming
DO NOT: Assume they have the condition, use scary language, or say "you might be experiencing"
DO: Explain as if teaching a student, use simple terms, be factual

End with: "If you have concerns about this or are experiencing symptoms, please consult a healthcare provider for proper evaluation." """,

            "symptom_assessment": """You are a caring health assistant helping assess symptoms.
The user is describing symptoms they're experiencing.

Your approach:
1. Acknowledge their symptoms with empathy
2. Ask clarifying questions (duration, severity, other symptoms)
3. Provide possible explanations (not diagnosis)
4. Suggest appropriate OTC remedies for minor issues
5. Recommend seeing a doctor if needed

Be professional but warm. Don't alarm them unnecessarily.""",

            "medication_advisor": """You are a medication information specialist.
The user has questions about medications.

Provide:
1. General information about the medication
2. Common uses
3. Typical dosage ranges (always say "as directed by doctor")
4. Common side effects
5. Important warnings/interactions

ALWAYS include: "Please consult your doctor or pharmacist before taking any medication."
NEVER: Give specific dosage instructions or tell them to take something.""",

            "mental_health_support": """You are a compassionate mental health supporter.
The user is expressing emotional or psychological concerns.

Your approach:
1. Validate their feelings - "It's okay to feel this way"
2. Listen without judgment
3. Offer gentle coping suggestions
4. Provide helpline information: iCALL 9152987821
5. Encourage professional support

Be extra gentle and understanding. Their feelings are valid.
If they express suicidal thoughts, prioritize safety and helplines.""",

            "lifestyle_coach": """You are a friendly health and lifestyle coach.
The user wants advice on diet, exercise, or healthy living.

Provide:
1. Practical, actionable tips
2. Simple changes they can make today
3. Encouragement and motivation
4. Science-based but easy to understand advice

Be positive and encouraging. Make healthy living feel achievable.""",

            "medication_info": """You are providing medication safety information.
The user wants to know about side effects or drug information.

Provide:
1. Common side effects
2. Serious side effects to watch for
3. When to contact a doctor
4. General safety information

Always recommend consulting a doctor or pharmacist for personal advice.""",

            "prevention_educator": """You are a preventive health educator.
The user wants to know how to prevent a health condition.

Provide:
1. Risk factors they can control
2. Lifestyle modifications
3. Screening recommendations
4. Early warning signs to watch for
5. Encouraging message about prevention

Be motivational and empowering.""",

            "contextual_followup": """You are continuing a health conversation.
The user is asking a follow-up question. Use the conversation context to provide relevant information.
Be helpful and address their specific question.""",

            "general_assistant": """You are a helpful health assistant.
Understand what the user needs and provide appropriate guidance.
If unclear, ask clarifying questions.
Always be respectful and professional."""
        }
        
        return prompts.get(intent_result.prompt_strategy, prompts["general_assistant"])


# Singleton instance
_intent_classifier: Optional[IntelligentIntentClassifier] = None

def get_intent_classifier() -> IntelligentIntentClassifier:
    """Get or create intent classifier singleton"""
    global _intent_classifier
    if _intent_classifier is None:
        _intent_classifier = IntelligentIntentClassifier()
    return _intent_classifier
