# Spec

## Objetivo

Operar una fabrica de agentes web ARNES/SDD con arnes obligatorio, evidencia trazable, memoria aislada por proyecto, gates, QA y logs.

## Requisitos

| id | tipo | descripcion | gate |
|---|---|---|---|
| REQ-001 | funcional | WorkOrder estricto y router con riesgo/presupuesto. | schema |
| REQ-002 | funcional | Ejecucion de agentes solo por `harness.run_agent(agent_id,state)`. | policy |
| REQ-003 | funcional | Agentes minimos registrados uno a uno con tools y permisos. | schema |
| REQ-004 | funcional | RAG/index/cache deterministico con context-pack y evidence-register. | evidence |
| REQ-005 | funcional | Memoria `Aprendizaje.md` separada por fabrica/proyecto/agente. | memory |
| REQ-006 | funcional | Ciclo SDD completo con 14 fases y 12 pasos operacionales. | consistency |
| REQ-007 | funcional | Validacion por Schema, Evidence, Policy, Safety, Consistency, Coverage, Budget, ToolOutput y FinalFormat. | final_format |
| REQ-008 | funcional | QA y trazabilidad post-implementacion segun `CHECKLIST.md`. | qa |
| NFR-001 | no_funcional | Reproducibilidad practica mediante temperatura 0, seed fijo, sort estable y cache. | stability |
| NFR-002 | no_funcional | No invencion: decision critica sin evidencia termina `not_answerable`. | evidence |
| NFR-003 | no_funcional | Side effects, secretos, deploy, merge y DB write bloqueados salvo aprobacion. | safety |

## Aclaraciones

No hay ambiguedades criticas para preparar la fabrica base. Los detalles del primer proyecto independiente se capturaran en `project/work_order.json`.
