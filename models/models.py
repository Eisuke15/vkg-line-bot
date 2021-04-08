from sqlalchemy import Column, Integer, String, Text, DateTime
from models import Base

class Group_id(Base):
    __tablename__ = 'groupids'
    id = Column(Integer, primary_key=True)
    g_id = Column(String)
    

    def __init__(self, g_id=None):
        self.g_id = g_id
        
    def __repr__(self):
        return self.g_id