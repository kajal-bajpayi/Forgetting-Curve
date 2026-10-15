from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models.user import User

# function to test if user can be saved and retrieved in db

def test_user():
    # creating temeporary database
    test_engine= create_engine("sqlite:///:memory:")

    #Create table in temporary db
    Base.metadata.create_all(bind=test_engine)

    with Session(test_engine) as session:
        user = User(
            email="learning@example.com",
            password_hash="test-hash",
        )

        # Todo 1
        session.add(user)
        session.commit()
        session.refresh(user)
        assert user.id is not None

        # Building a query to find by email
        statement = select(User).where(User.email == "learning@example.com")

        saved_user = session.scalar(statement)

        assert saved_user is not None
        assert saved_user.email == "learning@example.com"

    test_engine.dispose()


    
