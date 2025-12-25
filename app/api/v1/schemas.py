from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=50, description="Email"),
    password: str = Field(min_length=5, max_length=50, description="Password")

class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=50, description="Email"),
    password: str = Field(min_length=5, max_length=50, description="Password")