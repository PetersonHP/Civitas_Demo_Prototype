from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..models.civitas import Label as LabelModel
from ..schemas.civitas import Label

router = APIRouter(
    prefix="/labels",
    tags=["labels"],
)


@router.get("/", response_model=List[Label])
def get_labels(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db)
):
    """
    Get list of all labels with optional search query.
    Search matches against label_name and label_description.
    """
    query = db.query(LabelModel)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (LabelModel.label_name.ilike(search_pattern)) |
            (LabelModel.label_description.ilike(search_pattern))
        )

    labels = query.offset(skip).limit(limit).all()
    return labels


@router.get("/{label_id}", response_model=Label)
def get_label(
    label_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific label by ID.
    """
    label = db.query(LabelModel).filter(LabelModel.label_id == label_id).first()
    if not label:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Label not found")
    return label
