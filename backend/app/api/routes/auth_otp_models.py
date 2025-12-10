class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str
