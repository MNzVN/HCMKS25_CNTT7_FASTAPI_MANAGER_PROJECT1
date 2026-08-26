from datetime import datetime, timedelta

import app.models
from app.core.security import get_password_hash
from app.db.database import Base, SessionLocal, engine
from app.models.enums import ProjectMemberRole, TaskPriority, TaskStatus, UserRole
from app.models.project import Project, ProjectMember
from app.models.task import Task
from app.models.user import User


Base.metadata.create_all(bind=engine)


def get_or_create_user(db, email, full_name, password, role):
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        user = User(
            email=email,
            full_name=full_name,
            password_hash=get_password_hash(password),
            role=role,
            is_active=True,
        )
        db.add(user)
        db.flush()
    return user


def main():
    db = SessionLocal()
    try:
        admin = get_or_create_user(
            db,
            "admin@example.com",
            "System Admin",
            "Admin123456",
            UserRole.ADMIN,
        )
        member = get_or_create_user(
            db,
            "member@example.com",
            "Project Member",
            "Member123456",
            UserRole.USER,
        )

        project = (
            db.query(Project)
            .filter(
                Project.name == "Demo Project",
                Project.owner_id == admin.id,
            )
            .first()
        )
        if project is None:
            project = Project(
                name="Demo Project",
                description="Du lieu mau de kiem thu API",
                owner_id=admin.id,
            )
            db.add(project)
            db.flush()

        memberships = [
            (admin.id, ProjectMemberRole.OWNER),
            (member.id, ProjectMemberRole.MEMBER),
        ]
        for user_id, role in memberships:
            membership = (
                db.query(ProjectMember)
                .filter(
                    ProjectMember.project_id == project.id,
                    ProjectMember.user_id == user_id,
                )
                .first()
            )
            if membership is None:
                db.add(
                    ProjectMember(
                        project_id=project.id,
                        user_id=user_id,
                        role=role,
                    )
                )

        task_data = [
            ("Thiet ke giao dien", "Tao giao dien dang nhap", TaskStatus.TODO, TaskPriority.HIGH, 2),
            ("Viet API login", "Tao endpoint dang nhap va JWT", TaskStatus.IN_PROGRESS, TaskPriority.MEDIUM, 5),
            ("Kiem thu API", "Kiem thu cac case dung va sai", TaskStatus.DONE, TaskPriority.LOW, 1),
        ]
        for title, description, task_status, priority, days in task_data:
            task = (
                db.query(Task)
                .filter(Task.project_id == project.id, Task.title == title)
                .first()
            )
            if task is None:
                db.add(
                    Task(
                        project_id=project.id,
                        title=title,
                        description=description,
                        status=task_status,
                        priority=priority,
                        due_date=datetime.now() + timedelta(days=days),
                        assignee_id=member.id,
                    )
                )

        db.commit()
        print("Seed data created successfully.")
        print("Admin: admin@example.com / Admin123456")
        print("Member: member@example.com / Member123456")
        print(f"Project ID: {project.id}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
