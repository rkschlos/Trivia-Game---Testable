from fastapi.testclient import TestClient
from main import app
from postgres.db import CategoryQueries

client = TestClient(app)

class EmptyCategoryQueries:
    def get_category(self, id):
        return None

#the original function in categories.py depends on the class CategoryQueries
#which calls the database
# so below, we override that depency so our test does not rely on the database

def test_get_category_returns_404():
    # ARRANGE
    # Use our fake database
    app.dependency_overrides[CategoryQueries] = EmptyCategoryQueries

    # ACT
    # Make the request
    response = client.get("/api/postgres/categories/1")

    # ASSERT
    # Assert that we got a 404
    assert response.status_code == 404

    # CLEAN UP
    # Clear out the dependencies
    app.dependency_overrides = {}

class NormalCategoryQueries:
    def get_category(self, id):
        return[id, "OUR CATEGORY", True]

def test_get_category_returns_200():
    # ARRANGE
    app.dependency_overrides[CategoryQueries] = NormalCategoryQueries

    # ACT
    response = client.get("/api/postgres/categories/1")
    d = response.json()

    # ASSERT
    assert response.status_code == 200
    assert d["id"] == 1
    assert d["title"] == "OUR CATEGORY"
    assert d["canon"] == True

    # CLEAN UP
    app.dependency_overrides = {}