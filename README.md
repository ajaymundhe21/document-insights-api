# Document Insights API

## Overview
The Document Insights API is a backend service that accepts document text, processes it asynchronously, and returns structured summaries.

The system is designed to handle multiple users with limited processing capacity using rate limiting, caching, and a background worker.

---

## Tech Stack
- FastAPI (API layer)
- MongoDB Atlas (persistent storage)
- Redis (queue, caching, rate limiting)
- Docker Compose (local orchestration)

---

## Core Features

### 1. Asynchronous Processing
- Documents are queued in Redis
- A background worker consumes jobs and processes them
- Simulates processing with a delay (10–30 seconds)
- Updates status: `queued → processing → completed / failed`

### 2. Per-User Rate Limiting
- Each user can have a maximum of **3 active jobs**
- Enforced using Redis counters
- Requests exceeding limit return **HTTP 429**

### 3. Content-Based Caching
- Documents are hashed using SHA-256
- Duplicate content returns cached summary instantly
- Redis used as cache layer with TTL

### 4. Pagination & Filtering
- List documents with:
  - Pagination (`page`, `page_size`)
  - Optional status filtering

---

## API Endpoints

### POST `/documents`
Submit a document for processing

**Response**
```json
{
  "document_id": "...",
  "status": "queued"
}