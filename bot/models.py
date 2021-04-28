import os

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#環境変数ファイルから読み込み
load_dotenv()

#DB用初期設定
engine = create_engine(os.environ["DB_URL"], convert_unicode=True)
Session = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base = declarative_base()

class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    group_id = Column(String)

    def __init__(self, group_id=None):
        self.group_id = group_id
        
    def __repr__(self):
        return self.group_id
