from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from models import Program

#--------------------------SQLAlchemy ORM Functions--------------------------
def getPrograms(db: Session):
    try:
        programs = db.query(Program).all()
        return [
            {
                "program_id": p.program_id,
                "program_name": p.program_name,
                "program_specialization": p.program_specialization
            }
            for p in programs
        ]
    except SQLAlchemyError as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")
