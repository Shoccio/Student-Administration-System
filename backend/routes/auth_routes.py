from functions import auth_func, user_func
from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
from typing import Optional
from db.database import get_db
from models import UserCredential
import bcrypt
import jwt
from datetime import datetime, timedelta
import os

router = APIRouter()

# Password hashing using bcrypt directly
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    safe_password = password.encode('utf-8')[:72]
    return bcrypt.hashpw(safe_password, bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash"""
    try:
        safe_password = password.encode('utf-8')[:72]
        return bcrypt.checkpw(safe_password, hashed.encode('utf-8'))
    except:
        return False

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

class LoginRequest(BaseModel):
    username: str  # student_id for students, username for admin
    password: str

class AdminCreateRequest(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    role: str
    dept: Optional[str] = None

class AdminUpdateRequest(BaseModel):
    username: str
    email: str
    full_name: str
    role: str
    password: Optional[str] = None
    dept: Optional[str] = None

@router.post("/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Simple database-based authentication.
    Students: username = student_id (e.g., "2021-00001")
    Admins: username = admin username (e.g., "admin")
    Returns JWT token for session management.
    """
    try:
        username = credentials.username.strip()
        password = credentials.password
        
        # Query user_credentials table
        user = db.query(UserCredential).filter(UserCredential.username == username).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        stored_password = user.hashed_password
        
        # Check if password is temporary (not hashed yet)
        if stored_password.startswith("TEMP_"):
            # First login - hash the temp password and update
            temp_password = stored_password.replace("TEMP_", "")
            if password == temp_password:
                hashed = hash_password(password)
                user.hashed_password = hashed
                db.commit()
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password"
                )
        else:
            # Verify hashed password
            if not verify_password(password, stored_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password"
                )
        
        # Generate JWT token
        token_data = {
            "sub": username,
            "username": username,
            "role": user.role,
            "dept": user.dept or None,
            "student_id": user.student_id,
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        # Return token and user profile
        profile = {
            "username": user.username,
            "role": user.role,
            "full_name": user.full_name,
            "student_id": user.student_id,
            "email": user.email
        }
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "profile": profile
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


class PasswordChangeRequest(BaseModel):
    new_password: str


DEFAULT_STUDENT_PASSWORD = "#Uphsl123"
MIN_PASSWORD_LENGTH = 8


@router.post("/edit-password/{username}")
def edit_password(username: str, request: PasswordChangeRequest, db: Session = Depends(get_db)):
    """
    Change password for a user in user_credentials table.
    """
    try:
        user = db.query(UserCredential).filter(UserCredential.username == username).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if len(request.new_password) < MIN_PASSWORD_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"New password must be at least {MIN_PASSWORD_LENGTH} characters long"
            )

        # Respect bcrypt 72-byte limit
        hashed = hash_password(request.new_password)

        user.hashed_password = hashed
        db.commit()

        return {"message": "Password updated successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")


@router.post("/reset-student-password/{student_id}")
def reset_student_password(student_id: str, db: Session = Depends(get_db)):
    """
    Reset a student's password to the default value.
    Looks up by student_id first, then falls back to username.
    """
    try:
        user = db.query(UserCredential).filter(UserCredential.student_id == student_id).first()

        if not user:
            user = db.query(UserCredential).filter(UserCredential.username == student_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student account not found"
            )

        safe_password = DEFAULT_STUDENT_PASSWORD.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        hashed = hash_password(DEFAULT_STUDENT_PASSWORD)

        user.hashed_password = hashed
        db.commit()

        return {
            "message": "Student password reset successfully",
            "default_password": DEFAULT_STUDENT_PASSWORD,
            "username": user.username,
            "student_id": student_id
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")


@router.delete("/delete-user/{username}")
def delete_user(username: str, db: Session = Depends(get_db)):
    """
    Delete a user from user_credentials table.
    """
    try:
        user = db.query(UserCredential).filter(UserCredential.username == username).first()

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


@router.post("/admin/create")
def create_admin(admin_data: AdminCreateRequest, db: Session = Depends(get_db)):
    """
    Create a new admin user.
    Accepts admin details and stores them in user_credentials table with hashed password.
    """
    try:
        # Validate required fields
        if not admin_data.username or not admin_data.email or not admin_data.full_name or not admin_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields: username, email, full_name, password"
            )
        
        # Check if username already exists
        existing_user = db.query(UserCredential).filter(UserCredential.username == admin_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Username '{admin_data.username}' already exists"
            )
        
        # Check if email already exists
        existing_email = db.query(UserCredential).filter(UserCredential.email == admin_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{admin_data.email}' already exists"
            )
        
        # Validate password length
        if len(admin_data.password) < MIN_PASSWORD_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
            )
        
        # Hash password (respect bcrypt 72-byte limit)
        hashed_password = hash_password(request.password)
        
        # Create new admin
        new_admin = UserCredential(
            username=admin_data.username,
            email=admin_data.email,
            full_name=admin_data.full_name,
            hashed_password=hashed_password,
            role=admin_data.role or "admin",
            student_id=None,
            dept=admin_data.dept
        )
        
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        
        return {
            "message": "Admin created successfully",
            "admin": {
                "username": admin_data.username,
                "email": admin_data.email,
                "full_name": admin_data.full_name,
                "role": admin_data.role or "admin",
                "dept": admin_data.dept
            }
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.put("/admin-update/{username}")
def update_admin(username: str, admin_data: AdminUpdateRequest, db: Session = Depends(get_db)):
    """
    Update an existing admin user.
    """
    try:
        # Validate required fields
        if not admin_data.username or not admin_data.email or not admin_data.full_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields: username, email, full_name"
            )
        
        # Get the admin to update
        admin = db.query(UserCredential).filter(UserCredential.username == username).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        
        # Check for duplicate username (if username changed)
        if admin_data.username != username:
            existing_user = db.query(UserCredential).filter(UserCredential.username == admin_data.username).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Username '{admin_data.username}' already exists"
                )
        
        # Check for duplicate email
        if admin_data.email != admin.email:
            existing_email = db.query(UserCredential).filter(UserCredential.email == admin_data.email).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Email '{admin_data.email}' already exists"
                )
        
        # Update admin fields
        admin.username = admin_data.username
        admin.email = admin_data.email
        admin.full_name = admin_data.full_name
        admin.role = admin_data.role or "admin"
        admin.dept = admin_data.dept
        
        # Update password if provided
        if admin_data.password:
            if len(admin_data.password) < MIN_PASSWORD_LENGTH:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
                )
            safe_password = admin_data.password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
            admin.hashed_password = hash_password(safe_password)
        
        db.commit()
        db.refresh(admin)
        
        return {
            "message": "Admin updated successfully",
            "admin": {
                "username": admin.username,
                "email": admin.email,
                "full_name": admin.full_name,
                "role": admin.role,
                "dept": admin.dept
            }
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.delete("/admin-delete/{username}")
def delete_admin(username: str, db: Session = Depends(get_db)):
    """
    Delete an admin user by username.
    """
    try:
        admin = db.query(UserCredential).filter(UserCredential.username == username).first()
        
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Admin with username '{username}' not found"
            )
        
        db.delete(admin)
        db.commit()
        
        return {"message": f"Admin '{username}' deleted successfully"}
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get("/admins/search")
def search_admins(query: str, db: Session = Depends(get_db)):
    """
    Search for admins by name or username.
    """
    try:
        if not query or query.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query parameter is required"
            )
        
        # Query user_credentials table for admins
        admins = db.query(UserCredential).filter(UserCredential.role == "admin").all()
        
        if not admins:
            return {"admins": []}
        
        # Filter by name - case insensitive
        query_lower = query.lower().strip()
        matching_admins = []
        
        for admin in admins:
            full_name = (admin.full_name or "").lower()
            username = (admin.username or "").lower()
            
            if query_lower in full_name or query_lower in username:
                matching_admins.append({
                    "username": admin.username,
                    "full_name": admin.full_name,
                    "email": admin.email,
                    "role": admin.role
                })
        
        return {"admins": matching_admins}
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get("/admin/{name}")
def get_admin_by_name(name: str, db: Session = Depends(get_db)):
    """
    Get a specific admin by name or username.
    """
    try:
        if not name or name.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name parameter is required"
            )
        
        # Query user_credentials table for admins
        admins = db.query(UserCredential).filter(UserCredential.role == "admin").all()
        
        if not admins:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No admins found"
            )
        
        # Search for exact match or partial match - case insensitive
        name_lower = name.lower().strip()
        
        for admin in admins:
            full_name = (admin.full_name or "").lower()
            username = (admin.username or "").lower()
            
            if name_lower == full_name or name_lower == username or name_lower in full_name or name_lower in username:
                return {
                    "username": admin.username,
                    "full_name": admin.full_name,
                    "email": admin.email,
                    "role": admin.role,
                    "student_id": admin.student_id,
                    "dept": admin.dept,
                }
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Admin with name '{name}' not found"
        )
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
