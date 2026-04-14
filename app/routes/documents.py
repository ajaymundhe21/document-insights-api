from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from app.models import DocumentRequest
from app.db import db, r
from app.utils import get_hash
from bson import ObjectId
from datetime import datetime, timezone

datetime.now(timezone.utc)
router = APIRouter()


@router.post("/documents", status_code=status.HTTP_201_CREATED)
def create_document(doc: DocumentRequest):

    user_jobs_key = f"user:{doc.user_id}:active"
    current = r.incr(user_jobs_key)
    if current > 3:
        r.decr(user_jobs_key)
        raise HTTPException(status_code=429, detail="limit reached")

    content_hash = get_hash(doc.content)


    cache_key = f"cache:{content_hash}"
    cached_summary = r.get(cache_key)

    if cached_summary:
        r.decr(user_jobs_key)
        return {
            "status": "completed",
            "summary": cached_summary,
            "cached": True
        }

    existing = db.documents.find_one({
        "user_id": doc.user_id,
        "content_hash": content_hash,
        "status": "completed"
    })

    if existing:
        r.decr(user_jobs_key)
        return {
            "status": "completed",
            "summary": existing["summary"],
            "cached": True
        }

  
    document_data = {
        "user_id": doc.user_id,
        "title": doc.title,
        "content": doc.content,
        "content_hash": content_hash,
        "status": "queued",
        "summary": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

    result = db.documents.insert_one(document_data)


    r.lpush("document_queue", str(result.inserted_id))

    return {
        "document_id": str(result.inserted_id),
        "status": "queued"
    }

@router.get("/documents/{doc_id}")
def get_document(doc_id: str):


    if not ObjectId.is_valid(doc_id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    doc = db.documents.find_one({"_id": ObjectId(doc_id)})

    if not doc:
        raise HTTPException(status_code=404, detail="Not found")

    status = doc["status"]


    if status in ["queued", "processing"]:
        return {
            "status": status
        }

    elif status == "completed":
        return {
            "status": "completed",
            "summary": doc.get("summary")
        }

    elif status == "failed":
        return {
            "status": "failed",
            "error": doc.get("error", "processing failed")
        }

@router.get("/users/{user_id}/documents")
def list_documents(
    user_id: str,
    page: int = 1,
    page_size: int = 5,
    status: str = None
):


    if page < 1 or page_size < 1 or page_size > 50:
        raise HTTPException(status_code=400, detail="Invalid pagination")
    
    allowed_status = {"queued", "processing", "completed", "failed"}
    if status and status not in allowed_status:
        raise HTTPException(status_code=400, detail="Invalid status filter")
    query = {"user_id": user_id}

    if status:
        query["status"] = status

    skip = (page - 1) * page_size


    total = db.documents.count_documents(query)

  
    docs = db.documents.find(query)\
        .sort("created_at", -1)\
        .skip(skip)\
        .limit(page_size)

    result = []
    for doc in docs:
        result.append({
            "id": str(doc["_id"]),
            "title": doc["title"],
            "status": doc["status"],
            "created_at": doc["created_at"]
        })

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "documents": result
    }

@router.get("/health")
def health():
    try:
        db.command("ping")
        r.ping()
        return {"status": "ok"}
    except:
        raise HTTPException(status_code=500, detail="unhealthy")