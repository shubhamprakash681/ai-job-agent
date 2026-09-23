from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import SetupStatus, SetupRequest, TokenResponse, UserLogin, UserResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.core.logging import get_logger
from app.api.deps import get_current_user

logger = get_logger(__name__)
router = APIRouter()

@router.get("/setup/status", response_model=SetupStatus)
async def setup_status(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        
        if user:
            return SetupStatus(is_setup=True, message="System is already setup")
        return SetupStatus(is_setup=False, message="System requires setup")
    except Exception as e:
        logger.error(f"Error querying database for setup status: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unavailable: {str(e)}"
        )

@router.post("/setup", response_model=TokenResponse)
async def setup(request: SetupRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).limit(1))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System is already setup"
        )
        
    user = User(
        email=request.email,
        hashed_password=hash_password(request.password),
        full_name=request.full_name,
        is_active=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    access_token = create_access_token(subject=str(user.id))

    # Auto-seed candidate knowledge base from YAML files
    try:
        from app.services.candidate.kb_seeder import seed_candidate_kb
        await seed_candidate_kb(db, user_id=user.id)
    except Exception:
        pass

    return TokenResponse(access_token=access_token, user=user)

@router.post("/login", response_model=TokenResponse)
async def login(request: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
        
    access_token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=access_token, user=user)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
