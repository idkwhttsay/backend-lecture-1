from src.celery import celery_app
from src.database import get_session
from src.tasks.models import Task
import random
import logging
from uuid import uuid4
from datetime import datetime

logger = logging.getLogger(__name__)

RANDOM_TITLES = [
    "Complete project documentation",
    "Review code changes",
    "Update database schema",
    "Fix authentication bug",
    "Implement new feature",
    "Optimize database queries",
    "Write unit tests",
    "Deploy to production",
    "Backup database",
    "Update dependencies",
    "Refactor legacy code",
    "Create API endpoint",
    "Update user interface",
    "Monitor system performance",
    "Security audit review"
]

RANDOM_DESCRIPTIONS = [
    "This task needs to be completed as soon as possible",
    "Low priority task that can be done when time permits",
    "Critical task that affects system functionality",
    "Maintenance task for keeping the system healthy",
    "Enhancement task to improve user experience",
    "Bug fix to resolve reported issues",
    "Documentation update for better clarity",
    "Performance improvement task",
    "Security-related task requiring attention",
    "Integration task with external services"
]

@celery_app.task()
def create_random_task(user):
    """
    Celery task to create a random task for the current user.
    """
    db = get_session()
    try:
        # Randomly select a title and description
        title = random.choice(RANDOM_TITLES)
        description = random.choice(RANDOM_DESCRIPTIONS)

        # Create a new task instance
        new_task = Task(
            id=uuid4(),
            user_id=user.id,
            title=title,
            description=description,
            completed=False,
        )

        # Add the task to the session and commit
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        db.close()

        logger.info(f"Random task created: {new_task.title}")

        return {
            "status": "success",
            "task_id": new_task.id,
        }
    except Exception as e:
        logger.error(f"Failed to add random task: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        raise e


@celery_app.task
def periodic_add_random_task():
    """
    Periodic Celery task specifically designed for scheduled execution
    Adds a random task to the database every minute
    """
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Periodic task started at {current_time}")

        # Create a database session
        db = get_session()

        # Generate random task data with timestamp
        random_title = random.choice(RANDOM_TITLES)
        random_description = f"{random.choice(RANDOM_DESCRIPTIONS)} - Auto-generated at {current_time}"

        # Create a new task instance
        new_task = Task(
            title=f"[AUTO] {random_title}",
            description=random_description,
            completed=False
        )

        # Add to database
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        logger.info(f"Periodic task successfully added: {new_task.title} (ID: {new_task.id}) at {current_time}")

        # Close the session
        db.close()

        return {
            "status": "success",
            "task_id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "execution_time": current_time,
            "message": f"Periodic random task '{new_task.title}' added successfully at {current_time}"
        }

    except Exception as e:
        logger.error(f"Periodic task failed at {datetime.now()}: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        raise e