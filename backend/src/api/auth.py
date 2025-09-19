from datetime import datetime, timedelta
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

from src.core.config import settings
from src.core.logging import logger, log_audit_event
from src.models.user import User, UserRole
from src.models.audit import AuditLog

router = APIRouter()

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_id: str
    role: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.END_USER


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None


# Simple auth models (email/password only)
class SimpleRegister(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.END_USER


class SimpleLogin(BaseModel):
    email: EmailStr
    password: str


# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


# JWT utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password"""
    try:
        user = await User.find_one(
            {"$or": [{"username": username}, {"email": username}]}
        )
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return None


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """Get the current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = await User.find_one({"username": token_data.username})
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Get the current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# API Endpoints
@router.post("/simple/register")
async def simple_register(body: SimpleRegister):
    existing = await User.find_one({"email": body.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = get_password_hash(body.password)
    user = User(
        username=body.email.split('@')[0],
        email=body.email,
        full_name=body.email,
        hashed_password=hashed,
        role=body.role
    )
    await user.create()
    return {"message": "registered", "user_id": str(user.id)}


@router.post("/simple/login")
async def simple_login(body: SimpleLogin):
    user = await User.find_one({"email": body.email})
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer", "role": user.role, "user_id": str(user.id)}
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = await User.find_one(
            {"$or": [{"username": user_data.username}, {"email": user_data.email}]}
        )
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=user_data.role
        )
        
        await new_user.create()
        
        # Log audit event
        log_audit_event("USER_REGISTERED", str(new_user.id), {
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role
        })
        
        logger.info(f"New user registered: {new_user.username}")
        
        return UserResponse(
            id=str(new_user.id),
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role,
            is_active=new_user.is_active,
            created_at=new_user.created_at,
            last_login=new_user.last_login
        )
        
    except Exception as e:
        logger.error(f"User registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Login and get access token"""
    user = await authenticate_user(form_data.username, form_data.password)
    
    if not user:
        log_audit_event("LOGIN_FAILED", form_data.username, {
            "reason": "Invalid credentials"
        })
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        log_audit_event("LOGIN_FAILED", str(user.id), {
            "reason": "Account inactive"
        })
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await user.save()
    
    # Log successful login
    log_audit_event("LOGIN_SUCCESS", str(user.id), {
        "username": user.username,
        "login_time": user.last_login.isoformat()
    })
    
    logger.info(f"User logged in: {user.username}")
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=str(user.id),
        role=user.role
    )


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    """Get current user information"""
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.post("/logout")
async def logout(current_user: Annotated[User, Depends(get_current_active_user)]):
    """Logout user (client should delete the token)"""
    log_audit_event("LOGOUT", str(current_user.id), {
        "username": current_user.username,
        "logout_time": datetime.utcnow().isoformat()
    })
    
    logger.info(f"User logged out: {current_user.username}")
    
    return {"message": "Successfully logged out"}
