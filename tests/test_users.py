# tests/test_users.py

import pytest


@pytest.mark.asyncio
async def test_list_user_documents(client):
    response = await client.get("/users/user123/documents")

    assert response.status_code == 200
    assert isinstance(response.json(), list)