from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from api.router import router as api_router

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(api_router, prefix="/api")

# Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Home
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Erd
@app.get("/erd", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("erd.html", {"request": request})

# Classdiagram
@app.get("/classdiagram", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("classdiagram.html", {"request": request})

# Userstories
@app.get("/userstories", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("userstories.html", {"request": request})

# Scrumboard
@app.get("/scrumboard", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("scrumboard.html", {"request": request})