from fastapi import Depends, HTTPException, status, Request
from typing import Optional
import jwt
import os
from sqlalchemy.orm import Session

from db.database import get_db
from models import UserCredential

# JWT settings (should match auth_routes.py)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"

def get_user_from_token(request: Request, db: Session = Depends(get_db)) -> dict:
    """
    Extract and verify JWT token from request headers.
    Returns the user data if authenticated.
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        # Verify the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user from database
        user = db.query(UserCredential).filter(UserCredential.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return {"username": user.username, "role": user.role, "student_id": user.student_id}
        
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )

def get_current_user(request: Request, db: Session = Depends(get_db)) -> dict:
    """
    Dependency to get the currently authenticated user.
    """
    return get_user_from_token(request, db)

def get_user_profile(username: str, db: Session) -> Optional[dict]:
    """
    Get user profile from user_credentials table.
    """
    user = db.query(UserCredential).filter(UserCredential.username == username).first()
    
    if not user:
        return None
    
    return {
        "username": user.username,
        "role": user.role,
        "full_name": user.full_name,
        "student_id": user.student_id,
        "email": user.email
    }

def get_current_user_profile(request: Request, db: Session = Depends(get_db)) -> dict:
    """
    Get profile of currently authenticated user.
    """
    user = get_current_user(request, db)
    profile = get_user_profile(user["username"], db)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return profile

def get_current_user_role(request: Request, db: Session = Depends(get_db)) -> str:
    """
    Get role of currently authenticated user.
    """
    user = get_current_user(request, db)
    return user.get("role", "student")

def check_role(roles: list[str]):
    """
    Dependency to check if user has required role.
    """
    def checker(request: Request, db: Session = Depends(get_db)):
        role = get_current_user_role(request, db)
        if role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{role}' not authorized. Required roles: {roles}"
            )
        return role
    
    return Depends(checker)

def is_admin(request: Request, db: Session = Depends(get_db)) -> bool:
    """
    Check if current user is an admin.
    """
    try:
        role = get_current_user_role(request, db)
        return role == "admin" or role == "super admin"
    except:
        return False

def get_admin_dept_from_token(request: Request) -> Optional[str]:
    """
    Extract admin department from JWT token.
    Returns the dept if found, None otherwise.
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        dept = payload.get("dept")
        return dept
    except jwt.InvalidTokenError:
        return None
    except Exception:
        return None