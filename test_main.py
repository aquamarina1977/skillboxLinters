import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session, engine, Base
import models
import schemas

client = TestClient(app)


@pytest.fixture(scope="module")
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


    async with async_session() as session:
        recipe = models.Recipe(name="Test Recipe", cook_time=30, views=0)
        session.add(recipe)
        await session.commit()
        await session.refresh(recipe)
        yield recipe.id
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def test_get_recipes(setup_database):
    response = client.get('/recipes/')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_recipe(setup_database):
    recipe_id = setup_database
    response = client.get(f'/recipes/1')
    assert response.status_code == 200
    assert response.json()["title"] == "Рецепт борща"


def test_get_recipe_not_found():
    response = client.get('/recipes/9999')
    assert response.status_code == 404
    assert response.json() == {"detail": "Recipe not found"}


def test_create_recipe():
    new_recipe_data = {
        "title": "New Recipe",
        "author": "Василий Петров",
        "cook_time": 20,
        "views": 0,
        "ingredients": "1 стакан муки, 2 яйца",
        "description": "Простой и вкусный рецепт."
    }
    response = client.post('/recipes/', json=new_recipe_data)

    assert response.status_code == 200
    assert response.json()["title"] == "New Recipe"
    assert response.json()["author"] == "Василий Петров"
    assert response.json()["cook_time"] == 20
    assert response.json()["views"] == 0
    assert response.json()["ingredients"] == "1 стакан муки, 2 яйца"
    assert response.json()["description"] == "Простой и вкусный рецепт."
