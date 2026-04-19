"""
app/services/guardrail_validator.py
Valida a resposta gerada pelo LLM antes do envio outbound.

Verificações implementadas
--------------------------
1. Comprimento mínimo e máximo.
2. Ausência de marcadores de instrução interna ([INSTRUÇÃO INTERNA]).
3. Ausência de PII óbvios (CPF, CNPJ, cartão de crédito).
4. Sem conteúdo vazio ou apenas whitespace.
5. Sem caracteres de controle suspeitos.

O validador não bloqueia silenciosamente — lança GuardrailViolationError
para que o chamador decida a ação (fallback, alerta, log).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Padrões de PII (detecção básica — não substitui tokenização real)
# ---------------------------------------------------------------------------
_PII_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("CPF",  re.compile(r"\b\d{3}[.\-]?\d{3}[.\-]?\d{3}[.\-]?\d{2}\b")),
    ("CNPJ", re.compile(r"\b\d{2}[.\-]?\d{3}[.\-]?\d{3}[/\-]?\d{4}[.\-]?\d{2}\b")),
    ("Cartão", re.compile(r"\b(?:\d[ \-]?){15,16}\b")),
]

_INTERNAL_MARKER = re.compile(r"\[INSTRUÇÃO INTERNA", re.IGNORECASE)
_CONTROL_CHARS   = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

_MIN_LENGTH = 3
_MAX_LENGTH = 1_600  # ~2 mensagens WhatsApp


# ---------------------------------------------------------------------------
# Resultado estruturado
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# GuardrailValidator
# ---------------------------------------------------------------------------


class GuardrailValidator:
    """
    Valida o texto gerado pelo LLM.

    Uso
    ---
        validator = GuardrailValidator()
        clean_text = validator.validate(raw_llm_output)
        # Lança GuardrailViolationError se inválido
        # Retorna texto limpo (stripped) se válido
    """

    def __init__(
        self,
        min_length: int = _MIN_LENGTH,
        max_length: int = _MAX_LENGTH,
    ) -> None:
        self._min = min_length
        self._max = max_length

    def validate(self, text: str) -> str:
        """
        Valida e retorna o texto limpo.

        Raises
        ------
        GuardrailViolationError
            Se qualquer verificação falhar.
        """
        result = ValidationResult(valid=True)
        cleaned = text.strip()

        # 1. Vazio
        if not cleaned:
            result.add("Resposta vazia ou apenas whitespace.")

        if result.valid:
            # 2. Comprimento mínimo
            if len(cleaned) < self._min:
                result.add(
                    f"Resposta muito curta ({len(cleaned)} chars, mínimo {self._min})."
                )

            # 3. Comprimento máximo
            if len(cleaned) > self._max:
                result.add(
                    f"Resposta muito longa ({len(cleaned)} chars, máximo {self._max})."
                )

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

        if not result.valid:
            logger.warning(
                "[Guardrail] Violações detectadas: %s | texto=%r",
                result.violations,
                cleaned[:80],
            )
            raise GuardrailViolationError(result.violations)

        logger.debug("[Guardrail] Texto aprovado (%d chars).", len(cleaned))
        return cleaned
