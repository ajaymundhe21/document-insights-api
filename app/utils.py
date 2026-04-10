import hashlib

def get_hash(content: str):
    return hashlib.sha256(content.encode()).hexdigest()
