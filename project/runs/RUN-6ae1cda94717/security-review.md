# Security Review

| control | estado | nota |
|---|---|---|
| shell libre | pass | no registrado en ToolRegistry |
| lectura secretos | pass | `secrets.read` prohibido |
| deploy directo | pass | `deploy.direct` prohibido |
| DB write | pass | `db.write` prohibido |
| side effects | pass | requieren aprobacion si son `write` o `external` |
| dependencias | pass | no instaladas en bootstrap |
| datos productivos | pass | no usados |
