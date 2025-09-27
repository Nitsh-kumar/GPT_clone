from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models.schemas import (
    UserLogin, UserRegister, LoginResponse, RegisterResponse, 
    UserResponse, UserProfile
)
from app.core.auth import (
    create_access_token, get_current_user, verify_password
)
from app.models.db import (
    get_db, get_user_by_username, get_user_by_email, 
    create_user, get_all_users, get_user_by_id
)
from app.core.config import settings

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token"""
    try:
        # Get user from database
        user = get_user_by_username(db, user_data.username)
        
        if not user or not verify_password(user_data.password, user.hashed_password):
            return LoginResponse(
                success=False,
                message="Incorrect username or password"
            )
        
        if not user.is_active:
            return LoginResponse(
                success=False,
                message="Account is disabled"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        user_response = UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            roles=user.roles or ["user"],
            created_at=user.created_at.isoformat() if user.created_at else ""
        )
        
        return LoginResponse(
            success=True,
            message="Login successful",
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/register", response_model=RegisterResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if username already exists
        if get_user_by_username(db, user_data.username):
            return RegisterResponse(
                success=False,
                message="Username already registered"
            )
        
        # Check if email already exists
        if get_user_by_email(db, user_data.email):
            return RegisterResponse(
                success=False,
                message="Email already registered"
            )
        
        # Validate password strength (basic validation)
        if len(user_data.password) < 6:
            return RegisterResponse(
                success=False,
                message="Password must be at least 6 characters long"
            )
        
        # Create new user
        new_user_data = {
            "username": user_data.username,
            "email": user_data.email,
            "password": user_data.password,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "roles": ["user"]
        }
        
        new_user = create_user(db, new_user_data)
        
        if not new_user:
            return RegisterResponse(
                success=False,
                message="Failed to create user"
            )
        
        user_response = UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            is_active=new_user.is_active,
            roles=new_user.roles or ["user"],
            created_at=new_user.created_at.isoformat() if new_user.created_at else ""
        )
        
        return RegisterResponse(
            success=True,
            message="User registered successfully",
            user=user_response
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    try:
        username = current_user["username"]
        user = get_user_by_username(username)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserProfile(
            username=user["username"],
            email=user["email"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            roles=user.get("roles", ["user"]),
            created_at=user.get("created_at", "")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )

@router.post("/verify-token")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """Verify if the current token is valid"""
    return {
        "valid": True,
        "username": current_user["username"],
        "message": "Token is valid"
    }

@router.post("/refresh-token")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh the access token"""
    try:
        username = current_user["username"]
        user = get_user_by_username(username)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"], "user_id": user["id"]},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )

@router.get("/users", response_model=dict)
async def list_users(current_user: dict = Depends(get_current_user)):
    """List all users (admin only)"""
    try:
        username = current_user["username"]
        user = get_user_by_username(username)
        
        # Check if user has admin role
        if "admin" not in user.get("roles", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        users_db = get_users_db()
        users_list = []
        
        for user_data in users_db.values():
            users_list.append(UserResponse(
                id=user_data["id"],
                username=user_data["username"],
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                is_active=user_data["is_active"],
                roles=user_data.get("roles", ["user"]),
                created_at=user_data.get("created_at", "")
            ))
        
        return {
            "success": True,
            "users": users_list,
            "total": len(users_list)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}"
        )

@router.get("/users/{username}", response_model=UserProfile)
async def get_user(username: str, current_user: dict = Depends(get_current_user)):
    """Get user by username (admin only or own profile)"""
    try:
        current_username = current_user["username"]
        current_user_data = get_user_by_username(current_username)
        
        # Check if user is admin or requesting own profile
        if current_username != username and "admin" not in current_user_data.get("roles", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        user = get_user_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserProfile(
            username=user["username"],
            email=user["email"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            roles=user.get("roles", ["user"]),
            created_at=user.get("created_at", "")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )