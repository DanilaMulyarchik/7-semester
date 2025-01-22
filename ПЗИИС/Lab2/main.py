from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request
from database import DB

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register", response_class=HTMLResponse)
async def register(request: Request, first_name: str = Form(...), last_name: str = Form(...), username: str = Form(...),
                   email: str = Form(...), password: str = Form(...), repeat_password: str = Form(...)):
    if password != repeat_password:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Пароли не совпадают"})
    if DB().find({'username': username}):
        return templates.TemplateResponse("register.html", {"request": request, "error": "Логин пользователя занят"})
    if DB().find({'email': email}):
        return templates.TemplateResponse("register.html", {"request": request, "error": "Почта уже зарегистрирована"})
    DB().add([first_name, last_name, username, email, password])
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/main", response_class=HTMLResponse)
async def main(request: Request, username: str = Form(...), password: str = Form(...)):
    if DB().find({'username': username, 'password': password}):
        return templates.TemplateResponse("main.html", {"request": request, 'users': DB().get_users()})
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Неверный логин или пароль"})


@app.post("/add_user", response_class=HTMLResponse)
async def add_user(request: Request, first_name: str = Form(...), last_name: str = Form(...), username: str = Form(...),
                   email: str = Form(...), password: str = Form(...), repeat_password: str = Form(...)):

    if password != repeat_password:
        return {'error': 'Password'}

    DB().add([first_name, last_name, username, email, password])
    return templates.TemplateResponse("main.html", {"request": request, 'users': DB().get_users()})


@app.post("/delete_user", response_class=HTMLResponse)
async def delete_user(request: Request, first_name: str = Form(...), last_name: str = Form(...)):
    DB().delete(first_name)
    return templates.TemplateResponse("main.html", {"request": request, 'users': DB().get_users()})

#добавить редактирование!
@app.post("/delete_user", response_class=HTMLResponse)
async def delete_user(request: Request, first_name: str = Form(...), last_name: str = Form(...)):
    DB().delete(first_name)
    return templates.TemplateResponse("main.html", {"request": request, 'users': DB().get_users()})