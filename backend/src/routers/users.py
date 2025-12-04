from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..models.civitas import CivitasUser as UserModel
from ..schemas.civitas import CivitasUser

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/", response_model=List[CivitasUser])
def get_users(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db)
):
    """
    Get list of all users with optional search query.
    Search matches against firstname, lastname, email, and phone_number.
    """
    query = db.query(UserModel)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (UserModel.firstname.ilike(search_pattern)) |
            (UserModel.lastname.ilike(search_pattern)) |
            (UserModel.email.ilike(search_pattern)) |
            (UserModel.phone_number.ilike(search_pattern))
        )

    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=CivitasUser)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific user by ID.
    """
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    return user
