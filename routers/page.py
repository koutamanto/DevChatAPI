# routers/page.py
import json, sqlite3, sys
import re
from fastapi import APIRouter
from fastapi.params import Cookie
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.routing import request_response
from fastapi.staticfiles import StaticFiles
from starlette.templating import _TemplateResponse, Jinja2Templates
from get_group_name import getGroupName

from get_messagesV2 import get_messagesV2
from login import loginV2
sys.path.append("../")
from add_friend import add_friend
templates = Jinja2Templates(directory="templates")

router = APIRouter(default_response_class=HTMLResponse)
router.mount("/static", StaticFiles(directory="static"), name="static")

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

@router.get("/", response_class=HTMLResponse)
async def root_page(request: Request):
    return templates.TemplateResponse("index.html", {"request":request})

@router.get("/change_icon")
def change_icon(request: Request, uid: str = Cookie(None)):
    cur.execute(f'SELECT icon_url, name FROM users WHERE id="{uid}"')
    icon_url, name = cur.fetchone()
    return templates.TemplateResponse(
        "change_icon/index.html", 
        {
            "request":request,
            "icon_url":icon_url, 
            "name":name, 
            "uid":uid
        }
    )

@router.get("/profile_of_member/{uid}")
def add_page(request: Request, uid:str):
    cur.execute(f'SELECT name, icon_url FROM users WHERE id="{uid}"')
    name, icon_url = cur.fetchone()
    #print(name, icon_url)
    return templates.TemplateResponse(
        "profile_of_member/index.html",
        {
            "request":request,
            "uid":uid, 
            "name":name, 
            "icon_url":icon_url
        }
    )

@router.get("/add/{target_uid}")
def add_page(request: Request, target_uid: str, uid: str = Cookie(None)):
    try:
        add_friend(uid, target_uid)
        return RedirectResponse("/home")
    except:
        return templates.TemplateResponse(
            "login/add.html", 
            {
                "request":request,
                "target_uid":target_uid
            }
        )

@router.get("/create_group")
def create_group_page(request: Request, uid: str = Cookie(None)):
    return templates.TemplateResponse(
        "create_group/index.html", 
        {
            "request":request,
            "uid":uid
        }
    )

@router.get("/setting/group/{gid}")
def group_setting_page(request: Request, gid: str):
    group_cur.execute(f'SELECT uid, name, icon FROM {gid}')
    user_datas = group_cur.fetchall()
    cur.execute(f'SELECT name, icon_url FROM gid WHERE gid="{gid}"')
    name, icon_url = cur.fetchone()
    return templates.TemplateResponse(
        "setting/group.html",
        {
            "request": request,
            "gid": gid,
            "user_datas":user_datas,
            "name": name,
            "icon_url": icon_url
        }
    )

@router.get("/html_messages/{filename}")
def get_html_messages(filename: str, request: Request):
    return templates.TemplateResponse(
        "html_messages/" + filename,
        context={
            "request":request
        }
    )
@router.get("/profile/{uid}")
def profile_page(request: Request, uid: str):
    cur.execute(f'SELECT name, icon_url FROM users WHERE id="{uid}"')
    name, icon_url = cur.fetchone()
    #print(name, icon_url)
    return templates.TemplateResponse(
        "profile/index.html",
        {
            "request":request,
            "uid":uid, 
            "name":name, 
            "icon_url":icon_url
        }
    )

@router.get("/invite/{target_uid}")
def invite_into_group_page(request: Request, target_uid: str, uid: str = Cookie(None)):
    user_cur.execute(f"SELECT id, name FROM {uid}")
    datas = user_cur.fetchall()
    gids = []
    names = []
    for gid, name in datas:
        if gid[0] == "g":
            gids.append(gid)
            names.append(name)
        else:
            pass
    print(datas)
    return templates.TemplateResponse(
        "invite/index.html", 
        {
            "request": request,
            "uid":uid, 
            "group_list":zip(gids, names), 
            "target_uid":target_uid
        }
    )

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        "login/index.html",
        context={"request":request}
    )

@router.get("/group/{gid}")
def group_talk(request: Request, gid: str, uid: str = Cookie(None)):
    datas = get_messagesV2(gid)
    group_name = getGroupName(gid)["gid"]
    return templates.TemplateResponse(
        "group/index.html", 
        {
            "request": request,
            "datas":datas, 
            "uid":uid, 
            "gid":gid, 
            "group_name":group_name
        }
    )

@router.get("/otp_auth")
def otp_auth_page(request: Request, uid: str = Cookie(None)):
    return templates.TemplateResponse(
        "register/otp.html",
        {
            "request": request,
            "uid":uid
        }
    )

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        "register/index.html",
        context={"request":request}
    )

@router.get("/home")
def home(request:Request, email: str = Cookie(None), password: str = Cookie(None), uid: str = Cookie(None)):
    #print(email, password, uid)
    datas = loginV2(email, password)
    user_datas = datas["friend"]
    group_datas = datas["group"]
    folder_datas = datas["folder"]
    return templates.TemplateResponse(
        "home/index.html", 
        context={
            "request": request,
            "user_datas":user_datas, 
            "group_datas":group_datas, 
            "uid":uid
        }
    )