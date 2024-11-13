from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class Email(BaseModel):
    id: str
    subject: Optional[str] = None
    sender: Optional[EmailStr] = None
    received_at: Optional[datetime] = None
    body: Optional[str] = None
    raw_email: dict

    class Config:
        from_attributes = True
