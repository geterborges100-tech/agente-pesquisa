import uuid

from sqlalchemy.orm import Session


async def create_message(db: Session, conversation_id: uuid.UUID, role: str, content: str):
    # Aqui você pode implementar a lógica de salvar a mensagem no banco se tiver a model de Message
    # Por ora, vamos apenas dar um print ou pass para não quebrar o import
    print(f"Mensagem registrada para {conversation_id}: [{role}] {content[:20]}...")
    return None
