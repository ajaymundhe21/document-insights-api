import time
import random
from bson import ObjectId
from app.db import db, r

def process(doc_id):
    doc = db.documents.find_one({"_id": ObjectId(doc_id)})
    print("waiting for job...")
    if not doc:
        return

    db.documents.update_one(
        {"_id": ObjectId(doc_id)},
        {"$set": {"status": "processing"}}
    )
    
    time.sleep(random.randint(10, 30))

    if random.random() < 0.1:
        db.documents.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": {"status": "failed"}}
        )
        return

    summary = doc["content"][:50] + "..."

    db.documents.update_one(
        {"_id": ObjectId(doc_id)},
        {"$set": {"status": "completed", "summary": summary}}
    )

    cache_key = f"cache:{doc['user_id']}:{doc['content_hash']}"
    r.set(cache_key, summary, ex=3600)

    user_jobs_key = f"user:{doc['user_id']}:active"
    r.decr(user_jobs_key)


def run_worker():
    print("worker started")
    while True:
        job = r.brpop("document_queue")
        print("picked job:", job)
        if job:
            doc_id = job[1]
            process(doc_id)


if __name__ == "__main__":
    run_worker()