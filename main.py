from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import models
import schemas
from database import async_session, engine, Base

app = FastAPI()

async def get_db():
    async with async_session() as session:
        yield session


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()


@app.get('/recipes/', response_model=List[schemas.RecipeOut])
async def get_recipes(db: AsyncSession = Depends(get_db)):
    query = select(models.Recipe).order_by(models.Recipe.views.desc(), models.Recipe.cook_time.asc())
    result = await db.execute(query)
    return result.scalars().all()


@app.get('/recipes/{recipe_id}', response_model=schemas.RecipeOut)
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    query = select(models.Recipe).where(recipe_id == models.Recipe.id)
    result = await db.execute(query)
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    recipe.views += 1
    await db.commit()
    return recipe


@app.post('/recipes/', response_model=schemas.RecipeOut)
async def create_recipe(recipe: schemas.RecipeIn, db: AsyncSession = Depends(get_db)):
    new_recipe = models.Recipe(**recipe.dict())
    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe)
    return new_recipe

