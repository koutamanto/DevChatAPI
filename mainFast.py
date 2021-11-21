import base64
from io import BytesIO
from os import name
import re
import uuid
from PIL import Image

from flask import Flask, jsonify, request
from flask_sslify import SSLify

import sqlite3, json, requests
from flask.templating import render_template
import smtplib, ssl
from email.mime.text import MIMEText
from datetime import datetime
from flask_swagger import swagger
from flask import send_file
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from requests.api import get
from starlette.responses import JSONResponse
from werkzeug.utils import redirect
from login import loginV2
from get_messagesV2 import get_messagesV2
from get_group_name import getGroupName
from add_friend import add_friend

from fastapi import FastAPI, Form, Request
from fastapi.responses import PlainTextResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import random
import uvicorn
from routers import page, api, file
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
app.include_router(page.router)
app.include_router(api.router)
app.include_router(file.router)

if __name__ == '__main__':
    uvicorn.run("mainFast:app",
                host="0.0.0.0",
                port=443,
                reload=True,
                ssl_keyfile="./privkey.pem", 
                ssl_certfile="./fullchain.pem",
                )