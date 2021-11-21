# routers/api.py
from datetime import datetime
from io import BytesIO
import json, sqlite3, base64, smtplib, ssl
from email.mime.text import MIMEText
from fastapi import APIRouter
from fastapi.responses import UJSONResponse
from starlette.requests import Request
from starlette.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from starlette.routing import request_response
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from starlette.templating import Jinja2Templates
#from models.model import 
from PIL import Image

templates = Jinja2Templates(directory="templates")

router = APIRouter()
db_name = "main.db"
conn = sqlite3.connect(db_name, check_same_thread=False)
cur = conn.cursor()

user_db_name = "users.db"
user_conn = sqlite3.connect(user_db_name, check_same_thread=False)
user_cur = user_conn.cursor()
message_db_name = "messages.db"
message_conn = sqlite3.connect(message_db_name, check_same_thread=False)
message_cur = message_conn.cursor()
group_db_name = "groups.db"
group_conn = sqlite3.connect(group_db_name, check_same_thread=False)
group_cur = group_conn.cursor()

router.mount("/static", StaticFiles(directory="static"), name="static")

@router.get("/images/{filename}", response_class=FileResponse)
def get_uploaded_images(filename: str): 
    return FileResponse("/root/DevChatAPI/images/" + filename)