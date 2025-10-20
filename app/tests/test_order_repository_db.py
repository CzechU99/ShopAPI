import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.models import User
from app.repositories.user_repo import UserRepository

DATABASE_URL = "postgresql://testshop:testshop@db_test:5432/testshopdb"


@pytest.fixture(scope="session")
def db_engine():
    """Tworzy SQLAlchemy engine podłączony do kontenera PostgreSQL."""
    engine = create_engine(DATABASE_URL, future=True)
    Base.metadata.create_all(bind=engine)  
    yield engine
    Base.metadata.drop_all(bind=engine) 


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Fixture dla izolowanej sesji na każdy test."""
    Session = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)
    session = Session()
    yield session
    session.rollback()
    session.close()


def test_create_user_and_retrieve_by_id(db_session):
    repo = UserRepository(db_session)

    new_user = User(
        email="jan.kowalski@example.com",
        full_name="Jan Kowalski",
        hashed_password="JKowalski92"
    )

    created_user = repo.create(new_user)
    db_session.commit()

    retrieved_user = repo.get_by_id(created_user.id)

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == "jan.kowalski@example.com"
    assert retrieved_user.full_name == "Jan Kowalski"
    assert retrieved_user.created_at is not None
