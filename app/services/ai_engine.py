import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.models_v1 import Conversation, Node, NodeType, ConversationStatus
from app.services.prompt_builder import PromptBuilder
from app.services.llm_client import LLMClient
from app.services.state_machine import StateMachine
from app.repositories.conversations import update_conversation
from app.repositories.messages import create_message

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self, llm_client: LLMClient, prompt_builder: PromptBuilder):
        self.llm_client = llm_client
        self.prompt_builder = prompt_builder

    async def process_inbound(
        self,
        db: Session,
        conversation: Conversation,
        message_text: str,
        script: Dict[str, Any],
    ) -> Dict[str, Any]:
        logger.info(f"[AIEngine] Iniciando pipeline conversation_id={conversation.id}")
        try:
            await self._commit_inbound(db, conversation, message_text)

            nodes = script.get("nodes", {})
            current_node_key = conversation.current_node_key or script.get("start_node")

            if not current_node_key or not nodes.get(current_node_key):
                logger.warning("[AIEngine] Script vazio ou no nao encontrado - usando fallback.")
                return {"status": "ok", "outbound_text": "Ola! Como posso ajudar voce hoje?"}

            current_node_data = nodes[current_node_key]
            current_node = Node(key=current_node_key, **current_node_data)

            next_status, next_node_key = self._advance(conversation, current_node)

            outbound_text = current_node.text or "Entendido! Vamos continuar."

            await update_conversation(db, conversation.id, next_node_key or "")

            logger.info(f"[AIEngine] Estado: node={next_node_key or 'none'} status={next_status.value}")
            return {
                "status": "ok",
                "node_key": current_node.key,
                "next_node_key": next_node_key,
                "conv_status": next_status.value,
                "outbound_text": outbound_text,
            }

        except Exception as e:
            logger.exception(f"[AIEngine] Erro: {str(e)}")
            return {"status": "error", "reason": str(e)}

    def _advance(self, conversation: Conversation, current_node: Node) -> tuple[ConversationStatus, Optional[str]]:
        current_status = ConversationStatus(conversation.status)
        if current_node.node_type == NodeType.QUESTION:
            conversation.current_node_key = current_node.key
            new_status = StateMachine.transition(current_status, ConversationStatus.WAITING)
            conversation.status = new_status
            return new_status, current_node.key
        elif current_node.node_type == NodeType.STATEMENT and current_node.next_key:
            conversation.current_node_key = current_node.next_key
            new_status = StateMachine.transition(current_status, ConversationStatus.ACTIVE)
            conversation.status = new_status
            return new_status, current_node.next_key
        else:
            conversation.current_node_key = None
            new_status = StateMachine.transition(current_status, ConversationStatus.CLOSED)
            conversation.status = new_status
            return new_status, None

    async def _commit_inbound(self, db: Session, conversation: Conversation, message_text: str):
        create_message(db=db, conversation_id=conversation.id, role="user", content=message_text)
        logger.debug("[AIEngine] Mensagem inbound salva no historico.")
