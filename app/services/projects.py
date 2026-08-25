from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enums import ProjectMemberRole
from app.models.project import Project, ProjectMember
from app.models.user import User
from app.schemas.project import (
	ProjectCreate,
	ProjectDetailResponse,
	ProjectMemberAdd,
	ProjectMemberDetail,
	ProjectUpdate,
)


def get_project_or_404(project_id: int, db: Session) -> Project:
	project = db.query(Project).filter(Project.id == project_id).first()
	if project is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy dự án")
	return project


def require_owner(project: Project, current_user: User) -> None:
	if project.owner_id != current_user.id:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Chỉ chủ dự án được thực hiện thao tác này",
		)


def require_access(project: Project, current_user: User, db: Session) -> None:
	is_member = (
		db.query(ProjectMember)
		.filter(
			ProjectMember.project_id == project.id,
			ProjectMember.user_id == current_user.id,
		)
		.first()
		is not None
	)
	if project.owner_id != current_user.id and not is_member:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Bạn không có quyền xem dự án này",
		)


def create_project(project_in: ProjectCreate, current_user: User, db: Session) -> Project:
	project = Project(
		name=project_in.name,
		description=project_in.description,
		owner_id=current_user.id,
	)
	db.add(project)
	db.flush()
	db.add(
		ProjectMember(
			project_id=project.id,
			user_id=current_user.id,
			role=ProjectMemberRole.OWNER,
		)
	)
	db.commit()
	db.refresh(project)
	return project


def list_projects(search: str | None, current_user: User, db: Session) -> list[Project]:
	query = (
		db.query(Project)
		.outerjoin(ProjectMember, Project.id == ProjectMember.project_id)
		.filter(
			(Project.owner_id == current_user.id)
			| (ProjectMember.user_id == current_user.id)
		)
	)
	if search:
		query = query.filter(Project.name.ilike(f"%{search}%"))
	return query.distinct().all()


def get_project_detail(project_id: int, current_user: User, db: Session) -> ProjectDetailResponse:
	project = get_project_or_404(project_id, db)
	require_access(project, current_user, db)
	members = (
		db.query(ProjectMember)
		.filter(
			ProjectMember.project_id == project_id,
			ProjectMember.user_id != current_user.id,
		)
		.all()
	)
	return ProjectDetailResponse(
		id=project.id,
		name=project.name,
		description=project.description,
		owner_id=project.owner_id,
		created_at=project.created_at,
		members=[
			ProjectMemberDetail(
				user_id=member.user_id,
				full_name=member.user.full_name,
				email=member.user.email,
				role=member.role,
			)
			for member in members
		],
	)


def update_project(project_id: int, project_in: ProjectUpdate, current_user: User, db: Session) -> Project:
	project = get_project_or_404(project_id, db)
	require_owner(project, current_user)
	if project_in.name is not None:
		project.name = project_in.name
	db.commit()
	db.refresh(project)
	return project


def delete_project(project_id: int, current_user: User, db: Session) -> None:
	project = get_project_or_404(project_id, db)
	require_owner(project, current_user)
	db.delete(project)
	db.commit()


def add_project_member(
	project_id: int, member_in: ProjectMemberAdd, current_user: User, db: Session) -> ProjectMember:
	project = get_project_or_404(project_id, db)
	require_owner(project, current_user)
	user = db.query(User).filter(User.id == member_in.user_id).first()
	if user is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy người dùng")

	existing_member = (
		db.query(ProjectMember)
		.filter(
			ProjectMember.project_id == project_id,
			ProjectMember.user_id == member_in.user_id,
		)
		.first()
	)
	if existing_member:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Người dùng đã là thành viên của dự án",
		)

	member = ProjectMember(
		project_id=project_id,
		user_id=member_in.user_id,
		role=ProjectMemberRole.MEMBER,
	)
	db.add(member)
	db.commit()
	db.refresh(member)
	return member


def remove_project_member(project_id: int, user_id: int, current_user: User, db: Session) -> None:
	project = get_project_or_404(project_id, db)
	require_owner(project, current_user)
	member = (
		db.query(ProjectMember)
		.filter(
			ProjectMember.project_id == project_id,
			ProjectMember.user_id == user_id,
		)
		.first()
	)
	if member is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Người dùng không phải thành viên của dự án",
		)

	if member.role == ProjectMemberRole.OWNER:
		owner_count = (
			db.query(ProjectMember)
			.filter(
				ProjectMember.project_id == project_id,
				ProjectMember.role == ProjectMemberRole.OWNER,
			)
			.count()
		)
		if owner_count <= 1:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Không thể xóa owner cuối cùng của dự án",
			)

	db.delete(member)
	db.commit()


def list_project_members(project_id: int, current_user: User, db: Session) -> list[ProjectMember]:
	project = get_project_or_404(project_id, db)
	require_access(project, current_user, db)
	return db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()
