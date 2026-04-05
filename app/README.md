# Document Insights API

## Overview
This service allows users to submit documents, process them asynchronously, and retrieve summaries.

## Tech Stack
- FastAPI
- MongoDB Atlas
- Redis
- Docker

## Features
- Submit document for processing
- Background worker processes documents asynchronously
- Rate limiting (max 3 active jobs per user)
- Content-based caching
- Pagination support

## APIs

### POST /documents
Submit a document

### GET /documents/{id}
Get document status and summary

### GET /users/{user_id}/documents
List documents for a user (with pagination)

## Design Decisions
- Redis is used for:
  - Rate limiting
  - Caching duplicate content
  - Queue for background processing
- Worker runs separately to process jobs asynchronously
- MongoDB stores document lifecycle and data

## Run Locally

```bash
docker compose up --build