from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

url = os.environ["DB_URL"]
engine = create_engine(url, convert_unicode=True)
Session = sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base = declarative_base()
Base.metadata.create_all(bind=engine)