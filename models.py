from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"
    email = Column(String, primary_key=True, index=True)
    hashed_password = Column(String)

class Link(Base):
    __tablename__ = "links"
    short_code = Column(String, primary_key=True, index=True)
    url = Column(String)
    owner_email = Column(String, index=True)
    clicks = Column(Integer, default=0)