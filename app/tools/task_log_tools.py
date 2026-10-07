import json

from app.database import SessionLocal
from app.models import TaskLog


def save_task_log(
        user_id: int,
        user_message: str,
        route: str,
        tool_name: str,
        tool_result,
        final_answer: str,
        status: str = "success"
):
    db = SessionLocal()

    try:
        task_log = TaskLog(
            user_id=user_id,
            user_message=user_message,
            route=route,
            tool_name=tool_name,
            tool_result=json.dumps(
                tool_result,
                ensure_ascii=False
            ),
            final_answer=final_answer,
            status=status
        )

        db.add(task_log)
        db.commit()
        db.refresh(task_log)

        return task_log

    finally:
        db.close()