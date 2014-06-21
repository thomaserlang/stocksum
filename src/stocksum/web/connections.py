from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from stocksum.config import config

class Database:
    def __init__(self):
        self.engine = create_engine(
            config['database']['url'],
            echo=False,
            pool_recycle=3600,
        )
        self.session = sessionmaker(
            bind=self.engine,
        )

database = Database()