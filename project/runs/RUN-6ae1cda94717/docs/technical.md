# Documentacion Tecnica

## Operacion

1. Preparar `project/work_order.json`.
2. Ejecutar `python3 -m factory.cli run --project project --objective "<objetivo>"`.
3. Revisar `project/runs/<run_id>/RUN_STATE.md`.
4. No realizar deploy, merge, DB write, secretos ni llamadas externas sin aprobacion humana.

## Mantenimiento

- Agregar agentes solo si separan responsabilidad, permisos, riesgo, memoria, tools o evaluacion.
- Agregar tools solo con ToolSpec y policy.
- Mantener schemas con `additionalProperties=false` y enums cerrados.
