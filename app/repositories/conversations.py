import uuid
from sqlalchemy.orm import Session
from app.models.models_v1 import Conversation

def update_conversation(db: Session, conversation_id: uuid.UUID, current_node: str):
    db_conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if db_conv:
        db_conv.current_node_key = current_node
        db.commit()
        db.refresh(db_conv)
    return db_conv
