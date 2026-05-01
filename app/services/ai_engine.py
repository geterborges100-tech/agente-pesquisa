import asyncio
import logging
from typing import Any

from sqlalchemy.orm import Session

from app.models.extended_models import Message
from app.models.models_v1 import Conversation, ConversationStatus, Node, NodeType
from app.services.llm_client import LLMClient
from app.services.prompt_builder import PromptBuilder
from app.services.state_machine import StateMachine

logger = logging.getLogger(__name__)


class AIEngine:
    def __init__(self, llm_client: LLMClient, prompt_builder: PromptBuilder):
        self.llm_client = llm_client
        self.prompt_builder = prompt_builder

    async def process_inbound(
        self, db: Session, conversation: Conversation, message_text: str, script: dict[str, Any]
    ) -> dict[str, Any]:
        logger.info(f"[AIEngine] Iniciando pipeline conversation_id={conversation.id}")
        try:
            nodes = script.get("nodes", {})
            current_node_key = conversation.current_node_key or script.get("start_node")

            if not current_node_key or not nodes.get(current_node_key):
                return await self._free_chat(db, conversation, message_text)

            current_node_data = nodes[current_node_key]
            current_node = Node(key=current_node_key, **current_node_data)
            next_status, next_node_key = self._advance(conversation, current_node)
            outbound_text = current_node.text or "Entendido! Vamos continuar."
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

    async def _free_chat(self, db: Session, conversation: Conversation, message_text: str) -> dict[str, Any]:
        try:
            # Carrega as últimas 10 mensagens da conversa
            messages = (
                db.query(Message)
                .filter(Message.conversation_id == conversation.id)
                .order_by(Message.sent_at.asc())
                .limit(10)
                .all()
            )
            history = PromptBuilder.history_from_messages(messages)

            prompt_payload = self.prompt_builder.build(
                history=history,
                current_node=None,
                inbound_text=message_text,
            )
            loop = asyncio.get_running_loop()
            reply = await loop.run_in_executor(None, self.llm_client.complete, prompt_payload)
            logger.info(f"[AIEngine] Resposta do LLM: {reply[:80]}")
            return {
                "status": "ok",
                "outbound_text": reply,
                "conv_status": "active",
            }
        except Exception as e:
            logger.exception("LLM falhou ao gerar resposta")
            return {"status": "error", "reason": str(e)}

    def _advance(self, conversation: Conversation, current_node: Node) -> tuple[ConversationStatus, str | None]:
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
