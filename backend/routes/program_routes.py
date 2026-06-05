from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from db.deps import get_db
from functions.program_func import getPrograms

router = APIRouter()

@router.get("/get")
def getProgramsRoute(db: Session = Depends(get_db)):
    return getPrograms(db)