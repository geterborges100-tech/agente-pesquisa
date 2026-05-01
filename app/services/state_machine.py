"""
app/services/state_machine.py
Máquina de estados da Conversation.

Transições permitidas
---------------------
    OPEN    → ACTIVE   : primeira mensagem do contact recebida com roteiro ativo
    ACTIVE  → WAITING  : AI enviou pergunta e aguarda resposta
    WAITING → ACTIVE   : contact respondeu; próxima pergunta enviada
    ACTIVE  → CLOSED   : roteiro concluído (nó de tipo "end" alcançado)
    WAITING → CLOSED   : timeout ou handoff encerra a conversa
    * → CLOSED         : encerramento forçado

Modelo de Conversation relevante (models_v1.py)
-----------------------------------------------
    status          : str  — estado atual
    current_node_key: str  — chave do nó corrente no definition_json
"""

from __future__ import annotations

import logging
from enum import Enum

logger = logging.getLogger(__name__)


class ConversationStatus(str, Enum):
    OPEN = "open"
    ACTIVE = "active"
    WAITING = "waiting"
    CLOSED = "closed"


# Transições válidas: {from_state} → {allowed_to_states}
_ALLOWED_TRANSITIONS: dict[ConversationStatus, set[ConversationStatus]] = {
    ConversationStatus.OPEN: {ConversationStatus.ACTIVE, ConversationStatus.CLOSED},
    ConversationStatus.ACTIVE: {ConversationStatus.WAITING, ConversationStatus.CLOSED},
    ConversationStatus.WAITING: {ConversationStatus.ACTIVE, ConversationStatus.CLOSED},
    ConversationStatus.CLOSED: set(),  # estado terminal
}


class InvalidTransitionError(ValueError):
    """Transição de estado não permitida."""


class StateMachine:
    """
    Gerencia transições de estado de uma Conversation.

    Não acessa o banco diretamente — recebe/retorna o status como string
    para manter a classe testável sem ORM.
    """

    @staticmethod
    def transition(current_status: str, new_status: str) -> str:
        """
        Valida e retorna o novo status.

        Parameters
        ----------
        current_status : str
            Status atual da conversa (ex: "open").
        new_status : str
            Status desejado (ex: "active").

        Returns
        -------
        str — new_status validado.

        Raises
        ------
        InvalidTransitionError
            Se a transição não for permitida.
        ValueError
            Se algum status for inválido.
        """
        try:
            from_state = ConversationStatus(current_status)
            to_state = ConversationStatus(new_status)
        except ValueError as exc:
            raise ValueError(f"Status inválido: {exc}") from exc

        allowed = _ALLOWED_TRANSITIONS[from_state]
        if to_state not in allowed:
            raise InvalidTransitionError(
                f"Transição não permitida: {from_state.value!r} → {to_state.value!r}. "
                f"Permitidas: {[s.value for s in allowed]}"
            )

        logger.info("[StateMachine] %s → %s", from_state.value, to_state.value)
        return to_state.value

    @staticmethod
    def can_transition(current_status: str, new_status: str) -> bool:
        """Retorna True se a transição for permitida, sem lançar exceção."""
        try:
            from_state = ConversationStatus(current_status)
            to_state = ConversationStatus(new_status)
        except ValueError:
            return False
        return to_state in _ALLOWED_TRANSITIONS[from_state]
