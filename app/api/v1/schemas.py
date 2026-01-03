from pydantic import BaseModel, Field, EmailStr

# --- AUTHENTICATION SCHEMES ---

class LoginRequest(BaseModel):
    """Schema for user login credentials."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100)

class RegisterRequest(BaseModel):
    """Schema for new user registration."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100)
