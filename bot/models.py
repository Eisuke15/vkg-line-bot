from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    group_id = Column(String)

    def __init__(self, group_id=None):
        self.group_id = group_id
        
    def __repr__(self):
        return self.group_id