"""Upload test — port 8002 verbose."""
import httpx
import json

with open(r"d:\deepblue\sample.png", "rb") as f:
    files = {"file": ("sample.png", f, "image/png")}
    print("Uploading to port 8002...", flush=True)
    r = httpx.post("http://localhost:8002/api/v1/prescription/upload", files=files, timeout=120.0)

print(f"Status: {r.status_code}", flush=True)

data = r.json()
print(json.dumps(data, indent=2, ensure_ascii=False), flush=True)
