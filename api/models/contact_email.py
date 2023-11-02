from pydantic import BaseModel, EmailStr
from typing import Optional


class ContactForm(BaseModel):
    from_address: EmailStr
    name: str
    company: Optional[str] = None
    message: str
