import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import engine, async_session_factory
from app.db.base import Base
from app.models import ResumeVariant
from sqlalchemy import select

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session_factory() as session:
        await create_default_variants(session)


async def create_default_variants(session: AsyncSession):
    variants = [
        {
            "name": "java-react-fullstack",
            "display_name": "Java + React Full Stack",
            "description": "Full stack role with Java backend and React frontend.",
            "is_default": True
        },
        {
            "name": "java-backend",
            "display_name": "Java Backend / Spring Boot",
            "description": "Backend focused role using Java and Spring Boot ecosystem.",
            "is_default": False
        },
        {
            "name": "fullstack-engineer",
            "display_name": "Full Stack Engineer",
            "description": "Generic full stack engineering role.",
            "is_default": False
        },
        {
            "name": "backend-distributed",
            "display_name": "Backend / Distributed Systems",
            "description": "Backend engineering focused on distributed systems and scalability.",
            "is_default": False
        }
    ]

    for v in variants:
        result = await session.execute(
            select(ResumeVariant).where(ResumeVariant.name == v["name"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            new_variant = ResumeVariant(**v)
            session.add(new_variant)
            
    await session.commit()
