from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import models
import schemas
from database import Base, async_session, engine

app = FastAPI()


def get_db():
    async def _get_db():
        async with async_session() as session:
            yield session

    return _get_db


db_dependency = Depends(get_db())


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()


@app.get("/recipes/", response_model=List[schemas.RecipeOut])
async def get_recipes(db: AsyncSession = db_dependency):
    query = select(models.Recipe).order_by(
        models.Recipe.views.desc(), models.Recipe.cook_time.asc()
    )
    result = await db.execute(query)
    return result.scalars().all()


@app.get("/recipes/{recipe_id}", response_model=schemas.RecipeOut)
async def get_recipe(recipe_id: int, db: AsyncSession = db_dependency):
    query = select(models.Recipe).where(models.Recipe.id == recipe_id)
    result = await db.execute(query)
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    recipe.views += 1
    await db.commit()
    return recipe


@app.post("/recipes/", response_model=schemas.RecipeOut)
async def create_recipe(recipe: schemas.RecipeIn, db: AsyncSession = db_dependency):
    new_recipe = models.Recipe(**recipe.dict())
    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe)
    return new_recipe
