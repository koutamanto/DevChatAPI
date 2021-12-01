from re import U
from typing import List
from firebase_admin.credentials import Base
from pydantic import BaseModel
from pydantic.fields import Field

class getGroupName(BaseModel):
    type: str = "get_group_name"
    gid: str

class uploadIcon(BaseModel):
    type: str = "upload_icon"
    uid: str
    content: str
    filename: str

class textMessage(BaseModel):
    type: str = "text"
    content: str

class imageMessage(BaseModel):
    type: str = "image"
    filename: str
    content: str

class sendTextMessage(BaseModel):
    type: str = "send_text_message"
    sender: str
    to: str
    message: textMessage

class HTMLMessage(BaseModel):
    type: str = "html"
    content: str

class sendHTMLMessage(BaseModel):
    type: str = "send_html_message"
    sender: str
    to: str
    message: HTMLMessage

class sendHTMLMessageResponse(BaseModel):
    status: str = "success"
    url: str

class uploadGroupIcon(BaseModel):
    type: str = "upload_group_icon"
    gid: str
    content: str
    filename: str

class sendImageMessage(BaseModel):
    type: str = "send_image_message"
    sender: str
    to: str
    message: imageMessage

class createGroup(BaseModel):
    type: str = "create_group"
    uid: str
    name: str

class deleteFolder(BaseModel):
    type: str = "delete_folder"
    fid: str

class putIntoFolder(BaseModel):
    type: str = "put_into_folder"
    gid: str
    fid: str
    uid: str

class firstSignUp(BaseModel):
    type: str = "first_sign_up"
    user_name: str
    mail_address: str
    pass_word: str

class firstSignUpResponse(BaseModel):
    status: str = "success"
    uid: str

class invalidOpTypeResponse(BaseModel):
    status: str = "failed"
    reason: str = "invalid type"

class putIntoFolderResponse(BaseModel):
    status:str ="success"

class statusSuccess(BaseModel):
    status:str ="success"

class loginRequest(BaseModel):
    type: str = "log_in"
    mail_address: str
    pass_word: str

class friend(BaseModel):
    name: str = None
    uid: str = None
    icon_url: str = None

class group(BaseModel):
    name: str = None
    gid: str = None
    icon_url: str = None
    last_message: str = None
    unix: float = None

class folder(BaseModel):
    name: str = None
    fid: str = None
    groups: List[str] = None

class loginResponse(BaseModel):
    status: str = "success"
    friend: List[friend]
    group: List[group]
    folder: List[folder]
    uid: str

class joinGroup(BaseModel):
    type: str = "join_group"
    gid: str
    uid: str

class invalidPassword(BaseModel):
    status: str = "failed"
    reason: str = "password does not match"

class unregister(BaseModel):
    type: str = "unregister"
    uid: str
    password: str

class leaveGroup(BaseModel):
    type: str
    gid: str
    uid: str

class sendImageMessageResponse(BaseModel):
    status: str = "success"
    type: str = "image"
    url: str

class createGroupResponse(BaseModel):
    status: str = "success"
    gid: str

class deleteFolderResponse(BaseModel):
    status: str = "success"
    fid: str

class makeFolder(BaseModel):
    type: str = "make_folder"
    uid: str
    name: str

class makeFolderResponse(BaseModel):
    status: str = "success"
    fid: str

class leaveGroup(BaseModel):
    type: str = "leave_group"
    gid: str
    uid: str

class inviteIntoGroupResponse(BaseModel):
    status: str = "success"
    gid: str

class inviteIntoGroup(BaseModel):
    type: str = "invite_into_group"
    target_uid: str
    to: str
    uid: str

class RecentMessageData(BaseModel):
    content: str
    uid: str
    name: str
    unix: float
    number: int
    type: str
    icon_url: str

class getRecentMessageResponse(BaseModel):
    status: str = "success"
    datas: List[RecentMessageData]

class getRecentMessage(BaseModel):
    type: str = "get_recent_message"
    gid: str

class AllMessageData(BaseModel):
    content: str
    uid: str
    name: str
    unix: float
    number: int
    type: str

class getAllMessagesResponse(BaseModel):
    status: str = "success"
    datas: List[AllMessageData]

class getAllMessages(BaseModel):
    type: str = "get_all_message"
    gid: str

class signUp(BaseModel):
    type: str = "sign_up"
    uid: str
    otp: int

class signUpResponse(BaseModel):
    status: str = "success"
    uid: str

class firstForgotPassword(BaseModel):
    type: str = "first_forgot_password"
    mail_address: str

class firstForgotPasswordResponse(BaseModel):
    status: str = "success"
    uid: str

class forgotPassword(BaseModel):
    type: str = "forgot_password"
    otp: str
    uid: str

class forgotPasswordResponse(BaseModel):
    status: str = "success"

class resetPassword(BaseModel):
    type: str = "reset_password"
    uid: str
    new_password: str

class addFriendResponse(BaseModel):
    status: str = "success"
    target_uid: str

class addFriend(BaseModel):
    type: str = "add_friend"
    from_uid: str
    target_uid: str

class isChatChanged(BaseModel):
    last_num: int
    gid: str

class isChatChangedResponse(BaseModel):
    status: bool
    nums: List[int]

class getNewMessage(BaseModel):
    type: str = "get_new_message"
    gid: str
    nums: List[int]