from sqlalchemy import Column, String, Integer, Text
from database import Base

class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    cook_time = Column(Integer, nullable=False)
    views = Column(Integer, default=0)
    ingredients = Column(Text, nullable=False)
    description = Column(Text, nullable=False)