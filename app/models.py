from pydantic import BaseModel

class DocumentRequest(BaseModel):
    user_id : str 
    title: str
    content : str

