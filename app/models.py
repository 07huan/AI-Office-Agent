from sqlalchemy.orm import foreign

from app.database import Base
from sqlalchemy import Integer,Column,String,ForeignKey
from sqlalchemy import DateTime,func

class User(Base):
    __tablename__ = "users"
    id=Column(Integer,primary_key=True,index=True)
    username=Column(String(50),unique=True,nullable=False)
    email=Column(String(50),unique=True,nullable=False)
    password=Column(String(255),nullable=False)
    created_at=Column(DateTime,server_default=func.now())

class Customer(Base):
    __tablename__ = "customers"

    id =Column(Integer,primary_key=True,index=True)
    name=Column(String(50),nullable=False)
    company=Column(String(100))
    status=Column(String(50))
    phone=Column(String(30))
    created_at=Column(DateTime,server_default=func.now())

class Todo(Base):
    __tablename__ = "todos"

    id=Column(Integer,primary_key=True,index=True)

    user_id=Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    title=Column(String(200),nullable=False)
    status=Column(String(20),server_default="未完成")
    created_at=Column(DateTime,server_default=func.now())


class TaskLog(Base):
    __tablename__ = "task_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    user_message = Column(
        String(500),
        nullable=False
    )

    route = Column(String(50))

    tool_name = Column(String(100))

    tool_result = Column(String(5000))

    final_answer = Column(String(5000))

    status = Column(
        String(20),
        default="success"
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )