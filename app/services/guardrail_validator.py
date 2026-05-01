"""
app/services/guardrail_validator.py
Valida a resposta gerada pelo LLM antes do envio outbound.
Sprint 5: adicionado bloqueio de dados sensíveis (LGPD).

Verificações implementadas
----
1. Comprimento mínimo e máximo.
2. Ausência de marcadores de instrução interna ([INSTRUÇÃO INTERNA]).
3. Ausência de PII óbvios (CPF, CNPJ, cartão de crédito).
4. Sem conteúdo vazio ou apenas whitespace.
5. Sem caracteres de controle suspeitos.
6. [Sprint 5] Bloqueio de perguntas sobre dados sensíveis (LGPD art. 11).

O validador não bloqueia silenciosamente — lança GuardrailViolationError
para que o chamador decida a ação (fallback, alerta, log).
"""

from __future__ import annotations

import logging
import re
import uuid
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Padrões de PII (detecção básica)
# ──────────────────────────────────────────────
_PII_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("CPF", re.compile(r"\b\d{3}[.\-]?\d{3}[.\-]?\d{3}[.\-]?\d{2}\b")),
    ("CNPJ", re.compile(r"\b\d{2}[.\-]?\d{3}[.\-]?\d{3}[/\-]?\d{4}[.\-]?\d{2}\b")),
    ("Cartão", re.compile(r"\b(?:\d[ \-]?){15,16}\b")),
]

_INTERNAL_MARKER = re.compile(r"\[INSTRUÇÃO INTERNA", re.IGNORECASE)
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

_MIN_LENGTH = 3
_MAX_LENGTH = 1_600  # ~2 mensagens WhatsApp

# ──────────────────────────────────────────────
# Sprint 5: Dados sensíveis LGPD (art. 11)
# Categorias proibidas de coleta sem base legal específica
# ──────────────────────────────────────────────
_SENSITIVE_CATEGORIES: list[tuple[str, list[str]]] = [
    ("health", ["saúde", "doença", "diagnóstico", "medicamento", "tratamento", "enfermidade", "condição médica"]),
    ("religion", ["religião", "crença", "fé", "culto", "igreja", "templo", "deus", "religioso"]),
    ("ethnicity", ["etnia", "raça", "cor da pele", "origem racial", "descendência"]),
    ("sexuality", ["orientação sexual", "sexualidade", "gay", "lésbica", "bissexual", "trans", "gênero"]),
    ("politics", ["partido político", "filiação partidária", "voto", "candidato"]),
    ("biometrics", ["biometria", "impressão digital", "reconhecimento facial", "dado genético"]),
]

# Mensagem de fallback quando dado sensível é bloqueado
_SENSITIVE_FALLBACK = "Prefiro seguir com outra pergunta 🙂"


# ──────────────────────────────────────────────
# Resultado estruturado
# ──────────────────────────────────────────────


@dataclass
class ValidationResult:
    valid: bool
    violations: list[str] = field(default_factory=list)

    def add(self, msg: str) -> None:
        self.violations.append(msg)
        self.valid = False


class GuardrailViolationError(ValueError):
    """Resposta do LLM viola uma ou mais regras de guardrail."""

    def __init__(self, violations: list[str]) -> None:
        self.violations = violations
        super().__init__(f"Guardrail violations: {violations}")


class SensitiveDataBlockedError(GuardrailViolationError):
    """
    Resposta do LLM contém pergunta sobre dado sensível (LGPD art. 11).
    Separada de GuardrailViolationError para permitir audit_log específico.
    """

    def __init__(self, category: str) -> None:
        self.category = category
        super().__init__([f"Dado sensível detectado: categoria={category}"])


# ──────────────────────────────────────────────
# GuardrailValidator
# ──────────────────────────────────────────────


class GuardrailValidator:
    """
    Valida o texto gerado pelo LLM.

    Uso
    ---
        validator = GuardrailValidator()
        clean_text = validator.validate(raw_llm_output)
        # Lança GuardrailViolationError se inválido
        # Retorna texto limpo (stripped) se válido

    Sprint 5 — com audit_log:
        clean_text = validator.validate(
            raw_llm_output,
            db=db,
            conversation_id=conversation.id,
        )
    """

    def __init__(
        self,
        min_length: int = _MIN_LENGTH,
        max_length: int = _MAX_LENGTH,
    ) -> None:
        self._min = min_length
        self._max = max_length

    def validate(
        self,
        text: str,
        *,
        db: Session | None = None,
        conversation_id: uuid.UUID | None = None,
    ) -> str:
        """
        Valida e retorna o texto limpo.

        Raises
        ----
        SensitiveDataBlockedError
            Se o texto contiver pergunta sobre dado sensível (LGPD).
        GuardrailViolationError
            Se qualquer outra verificação falhar.
        """
        result = ValidationResult(valid=True)
        cleaned = text.strip()

        # 1. Vazio
        if not cleaned:
            result.add("Resposta vazia ou apenas whitespace.")

        if result.valid:
            # 2. Comprimento mínimo
            if len(cleaned) < self._min:
                result.add(f"Resposta muito curta ({len(cleaned)} chars, mínimo {self._min}).")

            # 3. Comprimento máximo
            if len(cleaned) > self._max:
                result.add(f"Resposta muito longa ({len(cleaned)} chars, máximo {self._max}).")

            # 4. Marcadores internos vazados
            if _INTERNAL_MARKER.search(cleaned):
                result.add("Resposta contém marcador de instrução interna.")

            # 5. Caracteres de controle
            if _CONTROL_CHARS.search(cleaned):
                result.add("Resposta contém caracteres de controle inválidos.")

            # 6. PII
            for pii_name, pattern in _PII_PATTERNS:
                if pattern.search(cleaned):
                    result.add(f"Possível {pii_name} detectado na resposta.")

            # 7. Sprint 5: Dados sensíveis LGPD
            sensitive_category = self._detect_sensitive(cleaned)
            if sensitive_category:
                self._audit_sensitive_block(
                    db=db,
                    conversation_id=conversation_id,
                    category=sensitive_category,
                )
                raise SensitiveDataBlockedError(sensitive_category)

        if not result.valid:
            logger.warning(
                "[Guardrail] Violações detectadas: %s | texto=%r",
                result.violations,
                cleaned[:80],
            )
            raise GuardrailViolationError(result.violations)

        logger.debug("[Guardrail] Texto aprovado (%d chars).", len(cleaned))
        return cleaned

    # ──────────────────────────────────────────
    # Sprint 5: helpers de dado sensível
    # ──────────────────────────────────────────

    @staticmethod
    def _detect_sensitive(text: str) -> str | None:
        """
        Detecta se o texto contém referência a dado sensível.
        Retorna a categoria detectada ou None.
        Nunca registra o valor — apenas a categoria.
        """
        text_lower = text.lower()
        for category, keywords in _SENSITIVE_CATEGORIES:
            for keyword in keywords:
                if keyword in text_lower:
                    return category
        return None

    @staticmethod
    def _audit_sensitive_block(
        db: Session | None,
        conversation_id: uuid.UUID | None,
        category: str,
    ) -> None:
        """
        Registra no audit_log que um dado sensível foi bloqueado.
        Nunca registra o valor — apenas a categoria.
        """
        if db is None:
            logger.warning(
                "[Guardrail] Dado sensível bloqueado (sem db para audit): categoria=%s",
                category,
            )
            return

        try:
            from app.services.audit_service import log_event

            log_event(
                db,
                event="guardrail.sensitive_data_blocked",
                actor="system",
                entity="guardrail",
                entity_id=conversation_id or uuid.uuid4(),
                action="block",
                criticality="high",
                conversation_id=conversation_id,
                context={"data_category": category},  # categoria apenas, nunca o valor
            )
        except Exception as exc:
            logger.error("[Guardrail] Falha ao registrar audit_log de bloqueio: %s", exc)
