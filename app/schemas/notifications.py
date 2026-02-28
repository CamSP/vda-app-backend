from pydantic import BaseModel

class RegisterTokenRequest(BaseModel):
    token: str

class BroadcastRequest(BaseModel):
    title: str
    body: str
    data: dict | None = None