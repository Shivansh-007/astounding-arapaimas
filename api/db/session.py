from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.constants import Connections

engine = create_engine(Connections.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
