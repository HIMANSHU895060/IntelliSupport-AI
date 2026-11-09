from pydantic import BaseModel, EmailStr, Field
class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
class LoginIn(BaseModel):
    email: EmailStr
    password: str
class ChatIn(BaseModel):
    message: str = Field(min_length=2, max_length=5000)
class TicketIn(BaseModel):
    subject: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=3, max_length=5000)
    category: str = "general"
    priority: str = "medium"
class StatusIn(BaseModel):
    status: str
class RoleIn(BaseModel):
    role: str
