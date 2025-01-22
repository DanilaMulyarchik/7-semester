import speech_recognition as sr
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app9.process import *

app = FastAPI()


with open("app9/operations.json", "r", encoding="utf-8") as f:
    operations = json.load(f)

app.mount("/static", StaticFiles(directory="app9/static"), name="static")
templates = Jinja2Templates(directory="app9/templates")


class Command(BaseModel):
    command: str


def recognize_speech_from_microphone():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio, language="ru-RU")
        return command
    except sr.UnknownValueError:
        return "Не удалось распознать речь"
    except sr.RequestError as e:
        return f"Ошибка запроса; {e}"


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return templates.TemplateResponse("index.html", {"request": {}})


@app.post("/process_command/")
async def process_command(command: Command):
    command_text = command.command.lower()
    response = operations.get(command_text, "Неизвестная команда")
    try:
        if 'напиши' in command_text:
            answer = generate(command_text)
        else:
            answer = globals()[response]()
    except:
        answer = command_text + f" -- неизвестная команда\n Команды -- {', '.join(operation())}"
    return {"response": answer}


'''@app.websocket("/ws/voice_input/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            command_text = recognize_speech_from_microphone()
            response = operations.get(command_text.lower(), "90")
            await websocket.send_text(response)
    except WebSocketDisconnect:
        print("Клиент отключился")'''