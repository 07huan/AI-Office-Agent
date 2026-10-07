from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    conversation_id: str

class UserRegister(BaseModel):
    username:str
    email:str
    password:str

class UserLogin(BaseModel):
    username:str
    password:str