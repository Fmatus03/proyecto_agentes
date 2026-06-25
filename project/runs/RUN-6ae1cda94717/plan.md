# Plan

## Arquitectura

1. `WorkOrderRouter` valida entrada, tipo de trabajo, riesgo y presupuesto.
2. `OrchestratorGraph` ejecuta fases SDD y solo llama `harness.run_agent(agent_id,state)`.
3. `HarnessRunner` carga `AgentSpec`, memoria filtrada, contexto, policy, tools, budget y validators.
4. `ContextManager` indexa documentos autorizados, deduplica chunks, compacta y escribe evidencia.
5. `MemoryGate` separa memoria de fabrica, proyecto y agente.
6. `ValidatorChain` bloquea schema, evidencia, policy, safety, consistencia, cobertura, presupuesto y formato final.
7. `Observability` escribe logs JSONL, ledger y handoff.

## Stack de proyectos web

Next.js, React, TypeScript, Tailwind, shadcn/ui, FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL, Redis, OIDC/OAuth2, Docker, CI/CD y observabilidad, siempre como decision por evidencia del proyecto.
