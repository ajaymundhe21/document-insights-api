import time
import random
import logging
from bson import ObjectId
from app.db import db, r

logging.basicConfig(level=logging.INFO)


def process(doc_id: str):
    lock_key = f"lock:{doc_id}"
    user_jobs_key = None

    
    if not r.set(lock_key, "1", nx=True, ex=60):
        return

    try:
        doc = db.documents.find_one({"_id": ObjectId(doc_id)})
        if not doc:
            return

        user_jobs_key = f"user:{doc['user_id']}:active"

       
        db.documents.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": {
                "status": "processing",
                "processing_started_at": time.time()
            }}
        )

        
        time.sleep(random.randint(10, 30))

        
        if random.random() < 0.1:
            db.documents.update_one(
                {"_id": ObjectId(doc_id)},
                {"$set": {
                    "status": "failed",
                    "error": "processing failed",
                    "updated_at": time.time()
                }}
            )
            return

        
        summary = doc["content"][:50] + "..."

     
        db.documents.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": {
                "status": "completed",
                "summary": summary,
                "completed_at": time.time(),
                "updated_at": time.time()
            }}
        )

        
        cache_key = f"cache:{doc['content_hash']}"
        r.set(cache_key, summary, ex=3600)

    except Exception as e:
        logging.error(f"Worker failed for {doc_id}: {e}")

        db.documents.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": {
                "status": "failed",
                "error": str(e)
            }}
        )

    finally:
        
        if user_jobs_key:
            r.decr(user_jobs_key)


def run_worker():
    logging.info("Worker started")

    while True:
        job = r.brpop("document_queue")
        if job:
            doc_id = job[1].decode()
            logging.info(f"Processing job {doc_id}")
            process(doc_id)


if __name__ == "__main__":
    run_worker()