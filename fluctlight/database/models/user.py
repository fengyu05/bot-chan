from sqlalchemy import Column, Integer, String

from fluctlight.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)

    def save(self, db):
        db.add(self)
        db.commit()