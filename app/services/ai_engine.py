import logging
from typing import Optional, Dict, Any
from app.models.conversations import Conversation, ConversationStatus
from app.models.nodes import Node, NodeType
from app.services.prompt_builder import PromptBuilder
from app.services.llm_client import LLMClient
from app.services.state_machine import StateMachine
from app.repositories.conversations import update_conversation

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(
        self,
        llm_client: LLMClient,
        prompt_builder: PromptBuilder,
    ):
        self.llm_client = llm_client
        self.prompt_builder = prompt_builder

    async def process_inbound(
        self,
        conversation: Conversation,
        message_text: str,
        script: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Processa uma mensagem de entrada e avança o fluxo da conversa.
        """
        logger.info(f"[AIEngine] Iniciando pipeline conversation_id={conversation.id}")

        try:
            # Commit da mensagem recebida antes de qualquer processamento
            await self._commit_inbound(conversation, message_text)

            # Carrega o nó atual do script
            nodes = script.get("nodes", {})
            current_node_key = conversation.current_node_key or script.get("start_node")

            if not current_node_key:
                logger.warning("[AIEngine] Nenhum nó atual ou nó inicial definido.")
                return {"status": "error", "reason": "Script mal formatado"}

            current_node_data = nodes.get(current_node_key)
            if not current_node_data:
                logger.error(f"[AIEngine] Nó '{current_node_key}' não encontrado no script.")
                return {"status": "error", "reason": f"Nó '{current_node_key}' não encontrado."}

            current_node = Node(key=current_node_key, **current_node_data)

            # Decide o próximo passo
            next_status, next_node_key = self._advance(conversation, current_node)

            # Se for uma pergunta e estiver esperando resposta, não envia nada
            outbound_text = ""
            if current_node.node_type == NodeType.QUESTION:
                outbound_text = current_node.text
            elif current_node.node_type == NodeType.STATEMENT:
                outbound_text = current_node.text
            elif current_node.node_type == NodeType.END:
                outbound_text = current_node.text

            # Persiste o estado atualizado
            await update_conversation(conversation)

            logger.info(
                f"[AIEngine] Estado persistido no banco: node={next_node_key or 'none'} status={next_status.value}"
            )

            return {
                "status": "ok",
                "node_key": current_node.key,
                "next_node_key": next_node_key,
                "conv_status": next_status.value,
                "outbound_text": outbound_text,
            }

        except Exception as e:
            logger.exception(f"[AIEngine] Erro no pipeline: {str(e)}")
            return {"status": "error", "reason": str(e)}

    def _advance(
        self,
        conversation: Conversation,
        current_node: Node,
    ) -> tuple[ConversationStatus, Optional[str]]:
        """
        Determina o próximo estado com base no nó atual.
        Se for uma question, para e espera resposta.
        """
        current_status = ConversationStatus(conversation.status)

        if current_node.node_type == NodeType.QUESTION:
            # Pergunta enviada → aguarda resposta
            conversation.current_node_key = current_node.key
            new_status = StateMachine.transition(current_status, ConversationStatus.WAITING)
            conversation.status = new_status
            return new_status, current_node.key

        elif current_node.node_type == NodeType.STATEMENT and current_node.next_key:
            # Avança para o próximo nó
            conversation.current_node_key = current_node.next_key
            new_status = StateMachine.transition(current_status, ConversationStatus.ACTIVE)
            conversation.status = new_status
            return new_status, current_node.next_key

        elif current_node.node_type == NodeType.END or not current_node.next_key:
            # Finaliza a conversa
            conversation.current_node_key = None
            new_status = StateMachine.transition(current_status, ConversationStatus.CLOSED)
            conversation.status = new_status
            return new_status, None

        # Caso fallback: manter no mesmo nó
        return current_status, current_node.key

    async def _commit_inbound(self, conversation: Conversation, message_text: str):
        """
        Salva a mensagem recebida como parte do histórico da conversa.
        """
        from app.repositories.messages import create_message
        from app.models.messages import MessageDirection, SenderType

        await create_message(
            conversation_id=conversation.id,
            contact_id=conversation.contact_id,
            direction=MessageDirection.INBOUND,
            sender_type=SenderType.CONTACT,
            raw_text=message_text,
            normalized_text=message_text.strip().lower(),
        )
        logger.debug("[AIEngine] Mensagem recebida salva no histórico.")
