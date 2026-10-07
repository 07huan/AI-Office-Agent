from app.database import SessionLocal
from app.models import Todo

def add_todo(title:str,user_id:int):
    db=SessionLocal()

    try:
        todo=Todo(
            title=title,
            user_id=user_id
        )

        db.add(todo)
        db.commit()
        db.refresh(todo)

        return {
            "id":todo.id,
            "title":todo.title,
            "status":todo.status,
            "created_at":str(todo.created_at)
        }

    finally:
        db.close()


def query_todos(user_id: int, status: str = None):
    db = SessionLocal()

    try:
        # 先按照当前用户过滤
        query = db.query(Todo).filter(
            Todo.user_id == user_id
        )

        # 如果传了状态，再按照状态过滤
        if status:
            query = query.filter(
                Todo.status == status
            )

        todos = query.all()

        result = []

        for todo in todos:
            result.append({
                "id": todo.id,
                "user_id": todo.user_id,
                "title": todo.title,
                "status": todo.status,
                "created_at": str(todo.created_at)
            })

        return result

    finally:
        db.close()



