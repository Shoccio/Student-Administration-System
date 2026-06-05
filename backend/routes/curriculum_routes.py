from functions import curriculum_func
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from db.deps import get_db
from schema.curriculum_schema import Curriculum

router = APIRouter()

@router.get("/get/{program_id}")
def getPrgmCurr(program_id: str, db: Session = Depends(get_db)):
    return curriculum_func.getPrgmCurr(program_id, db)

@router.post("/add")
def addCurr(curr: Curriculum, db: Session = Depends(get_db)):
    return curriculum_func.addCurr(curr, db)

@router.delete("/delete")
def deleteCurr(curr: Curriculum, db: Session = Depends(get_db)):
    return curriculum_func.deleteCurr(curr, db)

@router.patch("/archive")
def archiveCurr(curr: Curriculum, db: Session = Depends(get_db)):
    return curriculum_func.archiveCurr(curr, db)

@router.patch("/unarchive")
def unarchiveCurr(curr: Curriculum, db: Session = Depends(get_db)):
    return curriculum_func.unarchiveCurr(curr, db)

@router.put("/toggleArchive")
def toggleArchive(db: Session = Depends(get_db)):
    return curriculum_func.toggleArchive(db)