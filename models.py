from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class JobModel(Base):
    __tablename__ = 'jobs'
    _id = Column(Integer, primary_key=True)

    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    salary = Column(String)
    summary = Column(String)
    location = Column(String, nullable=False, unique=True)
    apply_url  = Column(String, unique=True)
    added_at = Column(String)