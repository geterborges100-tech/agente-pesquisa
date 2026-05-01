def _build_ai_engine(db: Session) -> AIEngine | None:
    """
    Instancia o AIEngine lendo a configuração LLM da tabela llm_configs.
    Retorna None se não houver config ativa (webhook continua funcionando sem IA).
    """
    from sqlalchemy import select

    from app.models.extended_models import LLMConfig

    evolution_base = os.environ.get("EVOLUTION_BASE_URL", "")
    evolution_instance = os.environ.get("EVOLUTION_INSTANCE", "Provedor_CRM")

    if not evolution_base:
        logger.warning("[webhooks_router] EVOLUTION_BASE_URL não definida — AIEngine desabilitado.")
        return None

    # Busca config LLM ativa no banco
    stmt = select(LLMConfig).where(LLMConfig.account_id == ACCOUNT_ID, LLMConfig.is_active == True).limit(1)
    config: LLMConfig | None = db.scalars(stmt).first()

    if config is None:
        logger.warning(
            "[webhooks_router] Nenhuma LLMConfig ativa para account_id=%s — AIEngine desabilitado.",
            ACCOUNT_ID,
        )
        return None

    try:
        llm = LLMClient(
            api_key=config.api_key,
            base_url=config.base_url,
            model=config.model,
            max_tokens=config.max_tokens,
        )
        outbound = EvolutionOutboundClient(
            base_url=evolution_base,
            api_key=EVOLUTION_API_KEY,
            instance=evolution_instance,
        )
        logger.info(
            "[webhooks_router] AIEngine ativo: provider=%s model=%s",
            config.provider,
            config.model,
        )
        return AIEngine(db=db, llm_client=llm, outbound_client=outbound)
    except Exception as exc:
        logger.warning("[webhooks_router] Falha ao criar AIEngine: %s", exc)
        return None
