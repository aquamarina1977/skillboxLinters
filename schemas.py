from pydantic import BaseModel


class BaseRecipe(BaseModel):
    title: str
    author: str
    cook_time: int
    ingredients: str
    description: str


class RecipeIn(BaseRecipe):
    pass


class RecipeOut(BaseRecipe):
    id: int
    views: int

    class Config:
        orm_mode = True
