"""
AI-Powered Health Assistant using Ollama with MedLlama2
A healthcare-specific language model fine-tuned on medical literature
"""
import ollama
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are MedAssist, an expert AI health assistant. You provide comprehensive, structured medical information with empathy and care.

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

EXAMPLE RESPONSE FOR "I have a tumor in my leg":

"**Understanding Your Condition** 📋
A tumor is an abnormal growth of cells that can be either benign (non-cancerous) or malignant (cancerous). Leg tumors can occur in the bone, muscle, or soft tissue. Common causes include:
• Benign growths like lipomas (fatty tissue) or fibromas
• Bone tumors (osteosarcoma, chondrosarcoma)
• Soft tissue sarcomas

Symptoms may include swelling, pain, limited movement, or a visible lump.

**Treatment & Medications** 💊
Tumor treatment requires proper medical evaluation and CANNOT be treated with over-the-counter medications. Treatment depends on the type:
• Benign tumors: May need surgical removal or monitoring
• Malignant tumors: May require surgery, chemotherapy, radiation, or targeted therapy
• Your doctor will determine the best approach after diagnosis

**Doctor Recommendation** 👨‍⚕️
Please consult an **Oncologist** (cancer specialist) or **Orthopedic Oncologist** (for bone tumors).
• Tests needed: MRI/CT scan, Biopsy, Blood tests
• Urgency: Schedule an appointment within 1-2 weeks
• Bring any previous medical reports

**Empathy & Support** 💚
I understand this must be a worrying time for you. Facing a possible tumor diagnosis takes courage, and it's completely normal to feel scared or anxious. Remember:
• Many tumors are benign and treatable
• Early consultation leads to better outcomes
• You don't have to face this alone - lean on family and friends
• Stay positive while getting proper medical care

Take care, and please don't delay seeing a specialist. 🙏"

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


class AIHealthAssistant:
    def __init__(self, model: str = "medllama2"):
        self.model = model
        self.conversations: Dict[str, list] = {}
    
    async def chat(self, session_id: str, message: str, language: str = "en") -> Dict[str, Any]:
        if session_id not in self.conversations:
            self.conversations[session_id] = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
        
        self.conversations[session_id].append({"role": "user", "content": message})
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=self.conversations[session_id],
                options={"temperature": 0.7, "top_p": 0.9}
            )
            
            ai_response = response['message']['content']
            self.conversations[session_id].append({"role": "assistant", "content": ai_response})
            
            # Check for emergency keywords
            urgency = self._check_urgency(message, ai_response)
            
            return {
                "response_text": ai_response,
                "urgency_level": urgency
            }
            
        except Exception as e:
            logger.error(f"AI Error: {e}")
            return {
                "response_text": "I'm having trouble processing that. Could you rephrase your question?",
                "urgency_level": "unknown"
            }
    
    def _check_urgency(self, message: str, response: str) -> str:
        msg_lower = message.lower()
        emergency_signs = [
            ("chest pain" in msg_lower and "arm" in msg_lower),
            ("can't breathe" in msg_lower or "cant breathe" in msg_lower),
            ("heart attack" in msg_lower),
            ("unconscious" in msg_lower),
            ("severe bleeding" in msg_lower)
        ]
        if any(emergency_signs):
            return "emergency"
        if "doctor" in response.lower() or "hospital" in response.lower():
            return "doctor_recommended"
        return "self_care"
    
    def clear_conversation(self, session_id: str):
        if session_id in self.conversations:
            del self.conversations[session_id]


# Global instance
ai_assistant = AIHealthAssistant()


class AIService:
    def __init__(self):
        self.assistant = ai_assistant
        # Import drug service for medication suggestions
        from .drug_service import drug_service
        from .triage_service import triage_service, mental_health_service, analyze_message
        from .nlp.translator import translation_service
        self.drug_service = drug_service
        self.triage_service = triage_service
        self.mental_health_service = mental_health_service
        self.analyze_message = analyze_message
        self.translator = translation_service
    
    async def get_ai_response(self, user_message: str, conversation_history: list = None, language: str = "en", vitals: Dict = None) -> Dict[str, Any]:
        import uuid
        session_id = str(uuid.uuid4())
        
        if conversation_history:
            self.assistant.conversations[session_id] = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
            for msg in conversation_history:
                self.assistant.conversations[session_id].append(msg)
        
        # Analyze message for triage and mental health
        analysis = self.analyze_message(user_message, vitals)
        triage = analysis["triage"]
        mental_health = analysis["mental_health"]
        
        # Get AI response
        result = await self.assistant.chat(session_id, user_message, language)
        
        # Get medication suggestions based on symptoms
        # BUT NOT for serious conditions (tumors, cancer, diabetes, etc.) or mental health crisis
        symptoms_detected = self._extract_symptoms(user_message)
        medications = []
        
        # Check if we should suggest OTC medications
        # Allow for: self_care, doctor_routine, and also when no serious condition detected
        is_serious_condition = triage.get("no_otc", False)
        is_mental_crisis = mental_health.get("is_crisis", False)
        
        # Suggest meds for minor ailments (headache, fever, cold, etc.)
        if symptoms_detected and not is_serious_condition and not is_mental_crisis:
            try:
                drug_result = self.drug_service.get_prescription_response(user_message)
                if drug_result.get("found_symptoms"):
                    medications = drug_result.get("medications", [])[:3]
                    logger.info(f"Medications suggested: {[m.get('name') for m in medications]}")
            except Exception as e:
                logger.error(f"Drug service error: {e}")
        
        # Build response with mental health support if needed
        response_text = result.get("response_text", "Sorry, I couldn't process that.")
        
        # If mental health crisis, prepend crisis response
        if mental_health.get("is_crisis"):
            response_text = mental_health.get("supportive_response", "") + "\n\n---\n\n" + response_text
        elif mental_health.get("has_mental_health_content"):
            # Add supportive elements without replacing AI response
            pass  # The AI model is trained to handle mental health empathetically
        
        # Translate response to user's language (AI always responds in English)
        original_response = response_text
        if language and language != "en":
            try:
                response_text = self.translator.translate_from_english(response_text, language)
                logger.info(f"Translated response to {language}")
            except Exception as e:
                logger.error(f"Translation failed: {e}, using English response")
                # Keep original English response if translation fails
        
        return {
            "response": response_text,
            "original_response": original_response if language != "en" else None,  # Include original for debugging
            "language": language,
            "symptoms_detected": symptoms_detected,
            "urgency_level": triage.get("level", "self_care"),
            "medications": medications,
            "triage": {
                "level": triage.get("level"),
                "label": triage.get("label"),
                "color": triage.get("color"),
                "action": triage.get("action"),
                "reason": triage.get("reason"),
                "detected_condition": triage.get("detected_condition"),
                "specific_action": triage.get("specific_action"),
                "no_otc": triage.get("no_otc", False),
                "emotional_support": triage.get("emotional_support", False)
            },
            "mental_health": {
                "detected": mental_health.get("has_mental_health_content", False),
                "categories": mental_health.get("categories", []),
                "severity": mental_health.get("severity", "low"),
                "is_crisis": mental_health.get("is_crisis", False),
                "resources": self._format_resources(mental_health.get("resources", [])),
                "grounding_exercise": mental_health.get("grounding_exercise"),
                "breathing_exercise": mental_health.get("breathing_exercise")
            },
            "requires_immediate_attention": analysis.get("requires_immediate_attention", False),
            "follow_up_questions": mental_health.get("follow_up_questions", [])
        }
    
    def _extract_symptoms(self, message: str) -> list:
        symptoms = ["headache", "fever", "pain", "cough", "nausea", "dizziness", 
                   "fatigue", "breathing", "chest", "stomach", "vomiting", "cold",
                   "allergy", "rash", "acidity", "diarrhea", "sleep", "anxiety",
                   "depressed", "stressed", "worried", "panic", "anxious", "scared"]
        found = [s for s in symptoms if s in message.lower()]
        return found
    
    def _format_resources(self, resources: list) -> list:
        """Convert string resources to {name, phone} objects for frontend"""
        formatted = []
        for res in resources:
            if isinstance(res, dict):
                formatted.append(res)
            elif isinstance(res, str):
                # Parse "Name: number" or "Name (info): number" format
                import re
                # Try to extract name and phone number
                match = re.match(r'^🆘?\s*([^:]+?):\s*([\d\-]+)', res)
                if match:
                    formatted.append({
                        "name": match.group(1).strip(),
                        "phone": match.group(2).replace("-", "")
                    })
                else:
                    # Fallback - try to find any phone number
                    phone_match = re.search(r'(\d{10,}|\d{4}[-\s]?\d{3}[-\s]?\d{3,4})', res)
                    if phone_match:
                        phone = phone_match.group(1).replace("-", "").replace(" ", "")
                        name = res.replace(phone_match.group(0), "").strip(" :-()🆘")
                        formatted.append({"name": name or "Helpline", "phone": phone})
        
        # Default resources if none parsed
        if not formatted:
            formatted = [
                {"name": "iCall (Free Counseling)", "phone": "9152987821"},
                {"name": "Vandrevala Foundation", "phone": "18602662345"}
            ]
        
        return formatted
