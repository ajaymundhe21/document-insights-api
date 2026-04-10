from pymongo import MongoClient
import redis
import os

MONGO_URI = os.getenv("MONGO_URI")

client =MongoClient(MONGO_URI)
db = client["document_db"]

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=6379,
    decode_responses=True
)