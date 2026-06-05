from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import UserCredential, Student

def update_user_role(user_id: str, role: str, db: Session):
    """
    Update user role in user_credentials table.
    Only admin, student, or faculty roles allowed.
    """
    try:
        if role not in ["admin", "student", "faculty", "super admin"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role. Must be 'admin', 'student', 'super admin' or 'faculty'"
            )
        
        # Check if user exists
        user = db.query(UserCredential).filter(UserCredential.username == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update role
        user.role = role
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def link_student_to_profile(user_id: str, student_id: str, db: Session):
    """
    Link a student_id to a user credential.
    Used when creating a student account.
    """
    try:
        # Check if user exists
        user = db.query(UserCredential).filter(UserCredential.username == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if student exists
        student = db.query(Student).filter(Student.student_id == student_id).first()
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Update user with student_id and set role to student
        user.student_id = student_id
        user.role = "student"
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def get_user_profile(user_id: str, db: Session):
    """
    Get user profile by username.
    """
    try:
        user = db.query(UserCredential).filter(UserCredential.username == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "username": user.username,
            "role": user.role,
            "full_name": user.full_name,
            "student_id": user.student_id,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
    except SQLAlchemyError as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def delete_profile(user_id: str, db: Session):
    """
    Delete user profile.
    """
    try:
        # Check if user exists
        user = db.query(UserCredential).filter(UserCredential.username == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")
