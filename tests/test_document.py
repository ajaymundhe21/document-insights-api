# tests/test_documents.py

import pytest


@pytest.mark.asyncio
async def test_submit_document_success(client):
    payload = {
        "user_id": "user123",
        "title": "Test Document",
        "content": "This is sample content"
    }

    response = await client.post("/documents", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert "document_id" in data
    assert data["status"] == "queued"


@pytest.mark.asyncio
async def test_submit_document_validation_fail(client):
    payload = {
        "user_id": "user123",
        "content": "Missing title"
    }

    response = await client.post("/documents", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_document_not_found(client):
    response = await client.get("/documents/invalid_id")

    assert response.status_code == 404