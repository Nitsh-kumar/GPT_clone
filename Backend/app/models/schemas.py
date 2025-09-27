from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# Auth schemas
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    roles: List[str]
    created_at: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class LoginResponse(BaseModel):
    success: bool
    message: str
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    expires_in: Optional[int] = None
    user: Optional[UserResponse] = None

class RegisterResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None

class UserProfile(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    roles: List[str]
    created_at: str

# Chat schemas
class ChatMessage(BaseModel):
    user_id: str
    message: str
    conversation_id: Optional[str] = None
    search_enabled: bool = True
    max_search_results: int = 5
    search_engine: str = "google"

class ChatResponse(BaseModel):
    success: bool
    response: str
    conversation_id: str
    search_results: List[Dict[str, Any]] = []

class ConversationHistory(BaseModel):
    success: bool
    conversations: List[Dict[str, Any]] = []

class ConversationMessages(BaseModel):
    success: bool
    messages: List[Dict[str, Any]] = []