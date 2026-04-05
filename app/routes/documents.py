from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.models import DocumentRequest
from app.db import db, r
from app.utils import get_hash
from bson import ObjectId

router = APIRouter()

@router.post("/documents")
def create_document(doc: DocumentRequest):
    user_jobs_key = f"user:{doc.user_id}:active"

    # limit check
    active_jobs = int(r.get(user_jobs_key) or 0)
    if active_jobs >= 3:
        raise HTTPException(status_code=429, detail="limit reached")

    content_hash = get_hash(doc.content)

    cache_key = f"cache:{doc.user_id}:{content_hash}"
    cached_summary = r.get(cache_key)

    if cached_summary:
        return {
            "status": "completed",
            "summary": cached_summary,
            "cached": True
        }

    document_data = {
        "user_id": doc.user_id,
        "title": doc.title,
        "content": doc.content,
        "content_hash": content_hash,
        "status": "queued",
        "summary": None,
        "created_at": datetime.utcnow()
    }

    result = db.documents.insert_one(document_data)

    # push to queue
    r.lpush("document_queue", str(result.inserted_id))

    # increase active jobs
    r.incr(user_jobs_key)

    return {
        "document_id": str(result.inserted_id),
        "status": "queued"
    }


@router.get("/documents/{doc_id}")
def get_document(doc_id: str):
    doc = db.documents.find_one({"_id": ObjectId(doc_id)})

    if not doc:
        return {"error": "not found"}

    doc["_id"] = str(doc["_id"])
    return doc

@router.get("/users/{user_id}/documents")
def list_documents(user_id: str, page: int = 1, page_size: int = 5, status: str = None):
    query = {"user_id": user_id}

    if status:
        query["status"] = status

    skip = (page - 1) * page_size

    docs = db.documents.find(query).skip(skip).limit(page_size)

    result = []
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        result.append(doc)

    return {
        "page": page,
        "page_size": page_size,
        "documents": result
    }