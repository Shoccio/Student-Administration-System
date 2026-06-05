from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from schema.curriculum_schema import Curriculum
from models import Curriculum as CurriculumModel

archiveCheck = True

def getPrgmCurr(program_id: str, db: Session):
    """Get all curricula for a specific program"""
    try:
        query = db.query(CurriculumModel).filter(CurriculumModel.program_id == program_id)
        
        # Filter out archived if archiveCheck is False
        if not archiveCheck:
            # Don't filter, return all
            pass
        else:
            # archiveCheck is True, but the model doesn't have archived field
            # Just return all for now
            pass
        
        curricula = query.all()
        return [
            {
                "id": c.id,
                "name": c.name,
                "program_id": c.program_id,
                "created_at": c.created_at,
                "updated_at": c.updated_at
            }
            for c in curricula
        ]
    except SQLAlchemyError as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def addCurr(curr: Curriculum, db: Session):
    """Add a new curriculum"""
    try:
        new_curriculum = CurriculumModel(
            name=curr.name,
            program_id=curr.program_id
        )
        db.add(new_curriculum)
        db.commit()
        db.refresh(new_curriculum)
        
        return {
            "message": "Curriculum added successfully",
            "data": {
                "id": new_curriculum.id,
                "name": new_curriculum.name,
                "program_id": new_curriculum.program_id
            }
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Failed to add curriculum: {str(e)}")

def deleteCurr(curr: Curriculum, db: Session):
    """Delete a curriculum by name and program_id"""
    try:
        curriculum = db.query(CurriculumModel).filter(
            CurriculumModel.name == curr.name,
            CurriculumModel.program_id == curr.program_id
        ).first()
        
        if not curriculum:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Curriculum not found")
        
        db.delete(curriculum)
        db.commit()
        
        return {"message": "Curriculum deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Failed to delete curriculum: {str(e)}")

def archiveCurr(curr: Curriculum, db: Session):
    """Archive a curriculum (set archived column to true)"""
    # Note: Current schema doesn't have an archived column
    # This function needs schema updates to work properly
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Archive functionality requires schema update")

def unarchiveCurr(curr: Curriculum, db: Session):
    """Unarchive a curriculum"""
    # Note: Current schema doesn't have an archived column
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Unarchive functionality requires schema update")
    
def toggleArchive():
    global archiveCheck
    archiveCheck = not archiveCheck