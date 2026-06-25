# Test Plan

| test_id | cubre | tipo | esperado |
|---|---|---|---|
| TEST-001 | WorkOrder/CycleState schemas | unit | campos extra y enums invalidos bloqueados |
| TEST-002 | AgentRegistry completo | unit | agentes minimos presentes |
| TEST-003 | Policy tool allowlist | negativo | tool no allowlisted bloqueada |
| TEST-004 | EvidenceValidator | negativo | claim critico sin evidencia => not_answerable |
| TEST-005 | BudgetValidator | negativo | presupuesto excedido => error |
| TEST-006 | MemoryGate | unit | proyecto aislado con Aprendizaje.md |
| TEST-007 | Orchestrator | integration | run bootstrap produce artefactos minimos |
