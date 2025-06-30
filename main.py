from fastapi import FastAPI, Request
import requests
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@app.post("/groq")
async def groq_proxy(request: Request):
    body = await request.json()
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=body
    )
    return response.json()


@app.get("/")
def home():
    return {"status": "Server is running!"}


AZURE_TTS_KEY = os.environ["AZURE_TTS_KEY"]
AZURE_TTS_REGION = os.environ["AZURE_TTS_REGION"]

@app.post("/speak")
async def speak(req: Request):
    data = await req.json()
    text = data["text"]

    ssml = f"""
    <speak version='1.0' xml:lang='en-US'>
      <voice name='en-US-JennyNeural'>{text}</voice>
    </speak>
    """

    response = requests.post(
        f"https://{AZURE_TTS_REGION}.tts.speech.microsoft.com/cognitiveservices/v1",
        headers={
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-16khz-32kbitrate-mono-mp3",
            "Ocp-Apim-Subscription-Key": AZURE_TTS_KEY
        },
        data=ssml.encode("utf-8")
    )

    if response.status_code != 200:
        return {"error": "Azure TTS failed", "status": response.status_code}

    return StreamingResponse(response.iter_content(chunk_size=1024), media_type="audio/mpeg")