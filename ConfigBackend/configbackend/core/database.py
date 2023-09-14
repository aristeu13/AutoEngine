from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from configbackend.core.settings import get_settings

settings = get_settings()
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_size=settings.database_pool_size,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
