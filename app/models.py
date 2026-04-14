from pydantic import BaseModel, Field, field_validator

class DocumentRequest(BaseModel):
    user_id: str = Field(..., min_length=3, max_length=50)
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=10, max_length=10000)

    @field_validator("user_id")
    def validate_user_id(cls, v):
        if not v.strip():
            raise ValueError("user_id cannot be empty")
        return v

    @field_validator("title")
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError("title cannot be blank")
        return v

    @field_validator("content")
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError("content cannot be blank")
        return v