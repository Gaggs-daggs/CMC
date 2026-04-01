"""Debug — trace exact response object from Gemini 2.5 Flash."""
import warnings
warnings.filterwarnings("ignore")
import google.generativeai as genai
import json

genai.configure(api_key="AIzaSyCbZiclZf-vq-N179KBNb-9LORudZH4chA")

model = genai.GenerativeModel("gemini-2.5-flash")

with open(r"d:\deepblue\sample.png", "rb") as f:
    image_bytes = f.read()

image_part = {"mime_type": "image/png", "data": image_bytes}

prompt = """You are a medical prescription reader. Analyze this prescription image and extract ALL information into structured JSON.

Return ONLY valid JSON (no markdown, no code fences) with this exact structure:
{
  "doctor_name": "Dr. Name or empty string if not visible",
  "patient_name": "Patient name or empty string if not visible",
  "date": "Date on prescription or empty string",
  "diagnosis": "Diagnosis or condition mentioned, or empty string",
  "medicines": [
    {
      "name": "Medicine name (generic + brand if visible)",
      "dosage": "e.g. 500mg, 10ml",
      "frequency": "e.g. twice daily, once at night",
      "duration": "e.g. 5 days, 2 weeks",
      "instructions": "e.g. take with water, avoid dairy",
      "timing": "e.g. after food, before breakfast, morning and night"
    }
  ],
  "additional_notes": "Any other notes, follow-up instructions, or warnings on the prescription"
}

RULES:
- Extract EVERY medicine listed, even if partially readable
- For unclear text, make your best interpretation and note uncertainty
- Include dosage strength (mg, ml, etc.) whenever visible
- Capture timing instructions (before/after food, morning/night)
- If something is not visible or not mentioned, use empty string ""
- Return ONLY the JSON object, nothing else"""

print("Calling Gemini 2.5 Flash...")
response = model.generate_content(
    [prompt, image_part],
    generation_config=genai.types.GenerationConfig(
        temperature=0.1,
        max_output_tokens=2048,
    ),
)

print(f"Type of response: {type(response)}")
print(f"Candidates count: {len(response.candidates)}")
print(f"Parts count: {len(response.candidates[0].content.parts)}")

for i, part in enumerate(response.candidates[0].content.parts):
    print(f"\n--- Part {i} ---")
    print(f"Type: {type(part)}")
    if hasattr(part, 'text'):
        print(f"Text length: {len(part.text)}")
        print(f"Text preview: {part.text[:300]}")
    if hasattr(part, 'thought') and part.thought:
        print(f"THOUGHT: {part.text[:200]}")

print(f"\n--- response.text ---")
print(f"Length: {len(response.text)}")
print(f"Full text:\n{response.text}")
