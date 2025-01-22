from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pyttsx3
import time

app = FastAPI()

app.mount("/static", StaticFiles(directory="app8/static"), name="static")
templates = Jinja2Templates(directory="app8/templates")

OUTPUT_AUDIO_FILE = "app8/static/output.wav"


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "audio_url": None})


@app.post("/synthesize/")
async def synthesize_speech(request: Request, text: str = Form(...), rate: int = Form(150), volume: float = Form(1.0), voice_id: int = Form(0)):
    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[voice_id].id)

    engine.save_to_file(text, OUTPUT_AUDIO_FILE)
    engine.runAndWait()

    timestamp = int(time.time())
    audio_url = f"/static/output.wav?{timestamp}"

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "audio_url": audio_url}
    )