from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Generator, Optional, List, Dict, Any
from app.core.config import settings
from app.models.orm_models import Base, User, Conversation, Message
from app.core.auth import get_password_hash
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise

def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_default_users(db: Session):
    """Initialize default users if they don't exist"""
    try:
        # Check if admin user exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@chatbot.com",
                first_name="Admin",
                last_name="User",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                roles=["admin", "user"]
            )
            db.add(admin_user)
        
        # Check if demo user exists
        demo_user = db.query(User).filter(User.username == "demo_user").first()
        if not demo_user:
            demo_user = User(
                username="demo_user",
                email="demo@chatbot.com",
                first_name="Demo",
                last_name="User",
                hashed_password=get_password_hash("demo123"),
                is_active=True,
                roles=["user"]
            )
            db.add(demo_user)
        db.commit()
        logger.info("Default users initialized")
        
    except Exception as e:
        logger.error(f"Error initializing default users: {e}")
        db.rollback()
        raise

# User database operations
def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get a user by username"""
    try:
        return db.query(User).filter(User.username == username).first()
    except SQLAlchemyError as e:
        logger.error(f"Error getting user by username: {e}")
        return None

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email"""
    try:
        return db.query(User).filter(User.email == email).first()
    except SQLAlchemyError as e:
        logger.error(f"Error getting user by email: {e}")
        return None

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID"""
    try:
        return db.query(User).filter(User.id == user_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Error getting user by ID: {e}")
        return None

def create_user(db: Session, user_data: Dict[str, Any]) -> Optional[User]:
    """Create a new user"""
    try:
        db_user = User(
            username=user_data["username"],
            email=user_data["email"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            hashed_password=get_password_hash(user_data["password"]),
            is_active=True,
            roles=user_data.get("roles", ["user"])
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        logger.error(f"Error creating user: {e}")
        db.rollback()
        return None

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users with pagination"""
    try:
        return db.query(User).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error getting all users: {e}")
        return []

def update_user(db: Session, user_id: int, user_data: Dict[str, Any]) -> Optional[User]:
    """Update user data"""
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            for key, value in user_data.items():
                if hasattr(db_user, key):
                    setattr(db_user, key, value)
            db.commit()
            db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        logger.error(f"Error updating user: {e}")
        db.rollback()
        return None

def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user"""
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            db.delete(db_user)
            db.commit()
            return True
        return False
    except SQLAlchemyError as e:
        logger.error(f"Error deleting user: {e}")
        db.rollback()
        return False

# Conversation database operations
def create_conversation(db: Session, conversation_id: str, user_id: int, title: str) -> Optional[Conversation]:
    """Create a new conversation"""
    try:
        db_conversation = Conversation(
            id=conversation_id,
            user_id=user_id,
            title=title
        )
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        return db_conversation
    except SQLAlchemyError as e:
        logger.error(f"Error creating conversation: {e}")
        db.rollback()
        return None

def get_user_conversations(db: Session, user_id: int) -> List[Conversation]:
    """Get all conversations for a user"""
    try:
        return db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc()).all()
    except SQLAlchemyError as e:
        logger.error(f"Error getting user conversations: {e}")
        return []

def get_conversation_by_id(db: Session, conversation_id: str) -> Optional[Conversation]:
    """Get a conversation by ID"""
    try:
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Error getting conversation: {e}")
        return None

# Message database operations
def create_message(db: Session, message_data: Dict[str, Any]) -> Optional[Message]:
    """Create a new message"""
    try:
        db_message = Message(
            conversation_id=message_data["conversation_id"],
            user_id=message_data["user_id"],
            role=message_data["role"],
            content=message_data["content"],
            search_results=message_data.get("search_results")
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    except SQLAlchemyError as e:
        logger.error(f"Error creating message: {e}")
        db.rollback()
        return None

def get_conversation_messages(db: Session, conversation_id: str) -> List[Message]:
    """Get all messages for a conversation"""
    try:
        return db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
    except SQLAlchemyError as e:
        logger.error(f"Error getting conversation messages: {e}")
        return []