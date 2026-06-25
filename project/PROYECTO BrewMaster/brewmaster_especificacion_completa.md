# Especificación BrewMaster — Sistema de Gestión para Cervecerías Artesanales

A continuación tienes una **especificación directa** para BrewMaster, un sistema web de gestión integral para cervecerías artesanales, coherente entre módulos, tablas y endpoints.

# 0. Supuesto general del sistema

Sistema web para gestionar:

Insumos, recetas, producción de lotes, calidad, mermas, inventario de productos terminados, ventas, clientes, órdenes de compra, proveedores, equipos, finanzas operativas, reportes, dashboard y alertas por correo.

Arquitectura recomendada:

`/api/v1`

Regla general de endpoints:

`GET` consulta, `POST` crea, `PUT/PATCH` actualiza, `DELETE` elimina lógico, endpoints de acción solo para cambios de estado.

Ejemplo correcto:

`POST /api/v1/batches/{id}/complete`

No recomendado:

`POST /api/v1/completarLote`

---

# A. Casos de uso con flujos

## 1. Gestión de insumos y proveedores

### UC-INS-01 Registrar insumo

Actor: Responsable de compras / administrador.

Flujo:

1. Usuario abre módulo Insumos.
2. Selecciona Nuevo insumo.
3. Ingresa código, nombre, tipo, unidad de medida, proveedor, bodega, costos y umbrales de stock.
4. Sistema valida código único y campos obligatorios.
5. Sistema guarda insumo en estado activo.
6. Sistema registra auditoría.

Alternos:

- Si el código ya existe, bloquea guardado.
- Si faltan campos obligatorios, muestra errores por campo.
- Si costo unitario es negativo, bloquea guardado.

### UC-INS-02 Registrar entrada de insumo

Flujo:

1. Usuario abre Entradas de insumos.
2. Selecciona insumo, cantidad, costo, proveedor y referencia.
3. Sistema valida cantidad mayor a cero.
4. Sistema actualiza stock actual del insumo.
5. Sistema registra movimiento en Kardex con tipo ENTRADA.
6. Sistema verifica umbral de alerta: si stock recuperado, resetea `last_alert_sent_at`.
7. Sistema registra auditoría.

Alternos:

- Insumo inactivo bloquea entrada.
- Costo negativo bloquea operación.

### UC-INS-03 Gestionar alertas de stock bajo

Flujo:

1. Sistema ejecuta proceso programado tras cada movimiento de inventario.
2. Evalúa stock actual contra umbral configurado.
3. Si stock cayó bajo umbral, encola notificación.
4. Worker envía correo a destinatarios configurados.
5. Sistema registra intento en `notification_queue`.

Alternos:

- Stock en cero: envío inmediato sin respetar intervalo.
- No reenvía antes de 24 horas salvo stock en cero.
- Tras 5 intentos fallidos, queda en error definitivo.

### UC-INS-04 Editar insumo

Flujo:

1. Usuario abre listado de insumos.
2. Selecciona insumo y abre ficha.
3. Modifica campos permitidos: nombre, tipo, costo, umbrales y alertas.
4. Sistema valida cambios.
5. Sistema actualiza insumo.
6. Sistema registra auditoría.

Alternos:

- No permite cambiar unidad de medida si el insumo tiene movimientos.
- No permite editar insumos eliminados.

### UC-INS-05 Inactivar insumo

Flujo:

1. Usuario selecciona insumo.
2. Presiona Inactivar.
3. Sistema valida que no haya recetas activas que lo usen.
4. Sistema cambia estado a inactivo.
5. Sistema registra auditoría.

Alternos:

- Insumo usado en receta activa no puede inactivarse.
- Insumo inactivo no puede recibir nuevas entradas.

### UC-INS-06 Registrar proveedor

Flujo:

1. Usuario abre módulo Proveedores.
2. Selecciona Nuevo proveedor.
3. Ingresa código, razón social, correo, teléfono, dirección, contacto y condición de pago.
4. Sistema valida código único.
5. Sistema guarda proveedor en estado activo.
6. Sistema registra auditoría.

Alternos:

- Código duplicado bloquea guardado.
- Correo inválido bloquea guardado si se ingresa.

---

## 2. Gestión de recetas

### UC-REC-01 Crear receta

Actor: Jefe de producción / administrador.

Flujo:

1. Usuario abre módulo Recetas.
2. Selecciona Nueva receta.
3. Ingresa nombre, descripción, tipo de cerveza, ABV estimado, volumen por lote y pasos de elaboración.
4. Agrega ingredientes: insumo, cantidad y unidad.
5. Sistema valida al menos un ingrediente activo.
6. Sistema calcula costo estimado según costos unitarios actuales.
7. Sistema guarda receta en estado activo.

Alternos:

- No permite receta sin ingredientes.
- Insumo inactivo no puede agregarse como ingrediente.
- Si la receta ya tiene lotes activos, no puede editarse.

### UC-REC-02 Clonar receta

Flujo:

1. Usuario abre receta existente.
2. Selecciona Clonar receta.
3. Sistema crea copia con nombre modificado y estado en_prueba.
4. Usuario ajusta ingredientes o parámetros.
5. Sistema guarda nueva versión.

Alternos:

- Receta clonada hereda todos los ingredientes.
- No se puede clonar una receta inactiva.

---

## 3. Gestión de producción

### UC-PROD-01 Crear lote de producción

Actor: Jefe de producción / operario.

Flujo:

1. Usuario abre Producción.
2. Selecciona Nueva producción.
3. Elige receta activa y tipo de presentación.
4. Ingresa cantidad a producir, fecha y responsable.
5. Sistema carga ingredientes según receta.
6. Sistema valida stock disponible de insumos.
7. Sistema crea lote en estado en_elaboracion.

Alternos:

- Sin receta activa, bloquea creación.
- Stock insuficiente de insumos muestra alerta pero puede continuar según configuración.

### UC-PROD-02 Completar lote

Flujo:

1. Usuario abre lote en elaboración.
2. Ingresa cantidad producida, horas de mano de obra, kWh, litros de agua y merma.
3. Selecciona Completar lote.
4. Sistema valida stock de insumos suficiente para la receta.
5. Sistema descuenta insumos proporcionales a cantidad producida.
6. Sistema registra salidas en Kardex de insumos con tipo SALIDA_PRODUCCION.
7. Sistema crea o incrementa inventario de productos terminados.
8. Sistema calcula costo total: insumos + mano de obra + energía + agua + merma + indirectos.
9. Sistema calcula costo por litro y costo por unidad.
10. Sistema registra en auditoría y verifica alertas de stock.

Alternos:

- Stock insuficiente bloquea completar salvo política de faltante aprobada.
- Costo total no puede ser negativo.

### UC-PROD-03 Registrar control de calidad

Flujo:

1. Usuario abre lote completado.
2. Accede a Control de calidad.
3. Ingresa densidades (OG/FG), ABV calculado, pH, temperatura, evaluación organoléptica.
4. Indica resultado: aprobado o rechazado.
5. Sistema guarda registro de calidad.
6. Si rechazado, lote puede marcarse como merma.

Alternos:

- Solo un registro de calidad por lote.
- Motivo obligatorio si resultado es rechazado.

### UC-PROD-04 Registrar merma

Flujo:

1. Usuario abre módulo Mermas.
2. Selecciona tipo de entidad: insumo o producto terminado.
3. Ingresa entidad, cantidad, costo unitario, tipo de merma y motivo.
4. Sistema calcula costo total.
5. Sistema descuenta del inventario correspondiente.
6. Sistema registra movimiento en Kardex con tipo MERMA.
7. Sistema actualiza KPI de mermas en dashboard.

Alternos:

- Motivo obligatorio en toda merma.
- No permite cantidad mayor al stock disponible.

---

## 4. Gestión de inventario de productos terminados

### UC-PRO-01 Consultar inventario de productos

Actor: Responsable de ventas / administrador.

Flujo:

1. Usuario abre Inventario de productos terminados.
2. Filtra por receta, presentación, estado o stock.
3. Sistema muestra listado con stock actual, costo y precio de venta.
4. Usuario abre detalle.
5. Sistema muestra Kardex del producto.

Alternos:

- Stock en cero se resalta visualmente.
- Costo visible solo para usuarios con permiso.

### UC-PRO-02 Actualizar precio de venta

Flujo:

1. Usuario abre producto.
2. Edita precio de venta base.
3. Sistema valida precio mayor o igual a cero.
4. Sistema guarda nuevo precio.
5. Sistema registra auditoría.

Alternos:

- Precio menor al costo genera advertencia no bloqueante.
- Solo roles autorizados pueden modificar precios.

---

## 5. Gestión de ventas y clientes

### UC-VTA-01 Registrar cliente

Actor: Responsable de ventas / administrador.

Flujo:

1. Usuario abre módulo Clientes.
2. Selecciona Nuevo cliente.
3. Ingresa nombre, identificador fiscal, correo, tipo de cliente y condiciones comerciales.
4. Sistema valida identificador único.
5. Sistema guarda cliente activo.
6. Sistema registra auditoría.

Alternos:

- Identificador fiscal duplicado bloquea guardado.
- Cliente con ventas no se elimina físicamente.

### UC-VTA-02 Registrar venta

Flujo:

1. Usuario abre Nueva venta.
2. Selecciona cliente (opcional).
3. Agrega productos, cantidades y precios sugeridos según tipo de cliente.
4. Sistema valida stock disponible por producto.
5. Sistema calcula ganancia por línea: `(precio_venta − costo_unitario) × cantidad`.
6. Usuario confirma venta.
7. Sistema descuenta del inventario de productos terminados.
8. Sistema registra en Kardex de productos con tipo VENTA.
9. Sistema registra auditoría.

Alternos:

- No permite vender más que el stock disponible.
- Cliente inactivo bloquea nueva venta.
- Precio en cero genera advertencia.

### UC-VTA-03 Gestionar reservas de stock

Flujo:

1. Usuario abre Reservas.
2. Selecciona cliente, producto, cantidad y fecha de entrega.
3. Sistema valida stock disponible (stock actual menos reservas activas).
4. Sistema crea reserva activa.
5. Usuario puede liberar o convertir en venta cuando corresponda.

Alternos:

- Stock reservado no disponible para otras ventas.
- Reserva vencida queda en estado vencida automáticamente.

### UC-VTA-04 Editar cliente

Flujo:

1. Usuario busca cliente en listado.
2. Abre ficha de cliente.
3. Modifica datos: nombre, correo, teléfono, tipo de cliente y condiciones.
4. Sistema valida cambios.
5. Sistema actualiza cliente.
6. Sistema registra auditoría.

Alternos:

- No permite cambiar identificador fiscal si el cliente tiene ventas.
- No permite editar clientes eliminados.

### UC-VTA-05 Anular venta

Flujo:

1. Usuario abre venta confirmada.
2. Selecciona Anular y proporciona motivo.
3. Sistema valida que la venta no tenga más de 24 horas salvo permiso especial.
4. Sistema revierte stock descargado al inventario.
5. Sistema registra en Kardex con tipo DEVOLUCION.
6. Sistema marca venta como anulada.
7. Sistema registra auditoría.

Alternos:

- Venta con reservas asociadas requiere liberar reservas primero.
- Solo roles autorizados pueden anular ventas antiguas.

---

## 6. Gestión de compras

### UC-COM-01 Crear orden de compra

Actor: Responsable de compras / administrador.

Flujo:

1. Usuario abre Órdenes de compra.
2. Selecciona Nuevo pedido.
3. Elige proveedor y agrega insumos, cantidades y precios.
4. Sistema calcula total estimado.
5. Usuario guarda orden en estado borrador.
6. Usuario envía orden: estado cambia a enviada.

Alternos:

- Proveedor inactivo bloquea creación.
- Precio negativo bloquea línea.
- Cantidad menor o igual a cero bloquea línea.

### UC-COM-02 Recepcionar compra

Flujo:

1. Usuario abre orden enviada.
2. Ingresa cantidades recibidas por insumo.
3. Sistema valida cantidades contra pendiente.
4. Sistema genera entrada de inventario de insumos.
5. Sistema registra en Kardex con tipo ENTRADA.
6. Si recepción parcial, orden queda en parcialmente_recibida.
7. Si recepción total, orden queda en recibida.

Alternos:

- No recibe más de lo solicitado sin aprobación.
- Orden cancelada no permite recepción.

---

## 7. Gestión de equipos

### UC-EQU-01 Registrar equipo

Actor: Jefe de producción / administrador.

Flujo:

1. Usuario abre Equipos.
2. Selecciona Nuevo equipo.
3. Ingresa nombre, tipo, marca, modelo, serie, costo de adquisición y vida útil.
4. Sistema guarda equipo en estado operativo.

Alternos:

- Código de equipo único.
- Costo de adquisición no puede ser negativo.

### UC-EQU-02 Registrar mantenimiento

Flujo:

1. Usuario abre equipo.
2. Selecciona Nuevo movimiento.
3. Elige tipo: mantencion, falla, reparacion, revision o descarte.
4. Ingresa descripción, costo y fecha.
5. Sistema actualiza `ultima_mantencion` y `proxima_revision`.
6. Sistema registra historial.

Alternos:

- Equipo descartado no acepta nuevos movimientos.
- Próxima revisión en el pasado genera alerta.

---

## 8. Gestión financiera básica

### UC-FIN-01 Registrar gasto operativo

Actor: Responsable de finanzas / administrador.

Flujo:

1. Usuario abre Gastos.
2. Ingresa concepto, categoría, monto, fecha y referencia.
3. Sistema valida monto mayor a cero.
4. Sistema guarda gasto.
5. Sistema actualiza reportes financieros.

Alternos:

- Categoría obligatoria.
- Gasto con documentos no puede eliminarse.

### UC-FIN-02 Consultar reportes financieros

Flujo:

1. Usuario abre Reportes financieros.
2. Selecciona tipo: estado de resultados, flujo de caja, cuentas por cobrar o punto de equilibrio.
3. Define rango de fechas.
4. Sistema calcula y muestra resultados.
5. Usuario exporta si tiene permiso.

Alternos:

- Datos sensibles ocultos sin permiso financiero.
- Exportación queda registrada en auditoría.

### UC-FIN-03 Gestionar metas mensuales

Flujo:

1. Usuario abre módulo Metas mensuales.
2. Selecciona mes y año objetivo.
3. Ingresa metas: litros de producción, monto de ventas, número de clientes nuevos y margen esperado.
4. Sistema guarda metas.
5. Dashboard muestra progreso vs meta en tiempo real.

Alternos:

- Solo admin puede crear o modificar metas.
- Meta sin dato numérico no bloquea guardado del resto.

---

## 9. Dashboard y reportes

### UC-REP-01 Ver dashboard general

Actor: Todos los roles según permisos.

Flujo:

1. Usuario ingresa al sistema.
2. Sistema carga KPIs según rol y permisos.
3. Muestra producción, inventario, ventas, compras, mermas y alertas.
4. Usuario filtra por fecha o bodega.

Alternos:

- Sin permisos, oculta KPIs financieros.
- Sin datos, muestra indicadores en cero.

### UC-REP-02 Exportar reporte

Flujo:

1. Usuario abre módulo Reportes.
2. Selecciona tipo: producción, ventas, inventario, Kardex, mermas, costos, financiero o auditoría.
3. Define filtros y formato: CSV, XLSX o PDF.
4. Sistema genera y entrega archivo.
5. Sistema registra exportación.

Alternos:

- Reporte de auditoría solo para admin y auditor.
- Rango amplio puede generar reporte diferido.

---

## 10. Gestión de configuración y alertas

### UC-ALT-01 Configurar alertas por correo

Actor: Administrador.

Flujo:

1. Usuario abre Configuración SMTP.
2. Ingresa parámetros: servidor, puerto, usuario, contraseña y correo remitente.
3. Sistema valida configuración.
4. Sistema guarda encriptado.
5. Usuario puede enviar correo de prueba.

Alternos:

- Solo admin puede editar SMTP.
- Credenciales nunca visibles en texto plano.

### UC-ALT-02 Configurar metas mensuales

Flujo:

1. Usuario abre Metas mensuales.
2. Selecciona mes y año.
3. Ingresa metas: litros de producción, monto de ventas, número de clientes y margen esperado.
4. Sistema guarda metas.
5. Dashboard muestra progreso vs meta.

Alternos:

- Solo admin puede definir metas.
- Meta sin dato no bloquea guardado del resto.

### UC-ALT-03 Gestionar usuarios y roles

Flujo:

1. Administrador abre módulo Usuarios.
2. Crea o edita usuario con nombre, correo, contraseña temporal y rol.
3. Sistema valida correo único y contraseña mínima.
4. Sistema guarda usuario activo.
5. Sistema registra auditoría.

Alternos:

- Rol obligatorio para guardar usuario.
- Correo duplicado bloquea creación.
- Solo admin puede gestionar usuarios y roles.

---

# B. Especificación de pantallas

## 30 pantallas

### P-01 Login

Campos: correo, contraseña.  
Acciones: ingresar, recuperar contraseña.  
Validaciones: credenciales válidas, usuario activo.

### P-02 Recuperar contraseña

Campos: correo.  
Acciones: enviar enlace de restablecimiento.  
Validaciones: formato de correo válido.

### P-03 Dashboard general

Muestra: KPIs de producción, inventario, ventas y finanzas. Gráfico de ventas últimos 6 meses, gráficos de stock, flujo de caja, meta vs real.  
Acciones: filtrar por fecha, abrir detalle de alerta.

### P-04 Listado de insumos

Campos filtro: código, nombre, tipo, bodega, estado.  
Muestra: badge de bajo stock.  
Acciones: crear, editar, exportar, abrir Kardex.

### P-05 Formulario de insumo

Campos: código, nombre, descripción, tipo, unidad de medida, proveedor, bodega, costo unitario, stock mínimo, stock máximo, fecha vencimiento, alertas email.  
Acciones: guardar, cancelar.

### P-06 Kardex de insumo

Campos filtro: fecha de inicio, fecha de fin, tipo de movimiento.  
Muestra: fecha, tipo, cantidad, costo, saldo resultante, referencia, usuario.  
Acciones: exportar.

### P-07 Entrada de insumos

Campos: insumo, cantidad, costo unitario, proveedor, referencia, observación.  
Acciones: registrar entrada.

### P-08 Listado de proveedores

Campos filtro: nombre, estado, tipo de insumo.  
Acciones: crear, editar, activar/desactivar.

### P-09 Formulario de proveedor

Campos: código, razón social, correo, teléfono, dirección, contacto principal, tipo de insumos, condición de pago.  
Acciones: guardar, cancelar.

### P-10 Listado de recetas

Campos filtro: nombre, tipo de cerveza, estado.  
Acciones: crear, editar, clonar, consultar costo.

### P-11 Formulario de receta

Campos de cabecera: nombre, descripción, tipo, ABV estimado, volumen por lote, pasos de elaboración.  
Sub-tabla de ingredientes: insumo, cantidad, unidad.  
Acciones: agregar ingrediente, guardar, cancelar.

### P-12 Listado de bodegas

Campos: código, nombre, tipo, responsable, capacidad.  
Acciones: crear, editar.

### P-13 Tipos de presentación

Campos: nombre, volumen, unidad, costo de presentación.  
Acciones: crear, editar.

### P-14 Listado de lotes de producción

Campos filtro: receta, estado, fecha de producción.  
Acciones: crear, completar, cancelar, ver detalle, control de calidad.

### P-15 Formulario de lote de producción

Campos: receta, tipo de presentación, cantidad a producir, fecha, responsable, horas de mano de obra, kWh, litros de agua, merma, costo indirecto, observaciones.  
Acciones: guardar, completar, cancelar.

### P-16 Detalle de lote

Muestra: datos del lote, insumos consumidos, costo total calculado, costo por litro, costo por unidad, resultado de calidad.  
Acciones: ver Kardex de insumos afectados.

### P-17 Control de calidad de lote

Campos: OG, FG, ABV calculado, ABV esperado, pH, temperatura de fermentación, apariencia, nota de aroma, nota de sabor, observaciones organolépticas, resultado, motivo de rechazo.  
Acciones: guardar.

### P-18 Inventario de productos terminados

Campos filtro: receta, presentación, estado, stock.  
Muestra: stock actual, costo unitario, precio de venta.  
Acciones: actualizar precio, ver Kardex, exportar.

### P-19 Registro de mermas

Campos: tipo de entidad (insumo/producto), entidad, cantidad, costo unitario, tipo de merma, motivo, fecha, lote asociado.  
Acciones: registrar.

### P-20 Listado de clientes

Campos filtro: nombre, identificador fiscal, tipo de cliente, estado.  
Acciones: crear, editar, activar/desactivar, ver historial de ventas.

### P-21 Formulario de cliente

Campos: nombre/razón social, identificador fiscal, correo, teléfono, dirección, tipo de cliente, forma de pago habitual, límite de crédito.  
Acciones: guardar, cancelar.

### P-22 Formulario de venta

Campos: cliente (opcional), fecha, responsable, observación.  
Líneas: producto, cantidad, precio sugerido por tipo de cliente, ganancia estimada.  
Acciones: agregar línea, confirmar venta.

### P-23 Reservas de stock

Campos: cliente, producto, cantidad, fecha de entrega prometida, precio.  
Acciones: crear, liberar, convertir en venta.

### P-24 Órdenes de compra

Campos filtro: proveedor, estado, fecha.  
Acciones: crear, editar, enviar, recepcionar, cancelar.

### P-25 Formulario de orden de compra

Campos: proveedor, fecha de emisión, fecha esperada de recepción, observación.  
Líneas: insumo, cantidad solicitada, precio unitario.  
Acciones: guardar, enviar.

### P-26 Recepción de compra

Campos: orden de compra, cantidades recibidas por insumo, bodega de destino.  
Acciones: recepcionar parcial, recepcionar total.

### P-27 Gestión de equipos

Campos filtro: tipo, estado, revisión vencida.  
Acciones: crear, editar, registrar movimiento, ver historial.

### P-28 Gastos operativos

Campos filtro: categoría, fecha, responsable.  
Acciones: crear, editar, eliminar, exportar.

### P-29 Reportes

Opciones: producción, ventas, inventario, Kardex, mermas, costos, financiero, auditoría.  
Campos filtro: fecha de inicio, fecha de fin, entidad específica.  
Acciones: generar, exportar CSV/XLSX/PDF.

### P-30 Configuración y alertas

Secciones: configuración SMTP, notificaciones enviadas, metas mensuales, gestión de usuarios y roles.  
Acciones: guardar SMTP, enviar prueba, definir meta, crear usuario, asignar rol.

---

# C. Reglas de negocio

## 60 reglas de negocio

1. Todo registro operativo debe pertenecer a una empresa.
2. Todo usuario debe tener un rol asignado y activo.
3. Todo cambio crítico debe registrarse en auditoría con usuario, fecha, entidad, acción e IP.
4. Los registros con historial operativo no se eliminan físicamente.
5. La eliminación lógica cambia estado a inactivo o cancelado.
6. Las contraseñas deben almacenarse siempre encriptadas con bcrypt o equivalente.
7. Un usuario inactivo no puede iniciar sesión.
8. Solo el rol admin puede gestionar usuarios y roles.
9. Los permisos se evalúan por rol en cada operación de API.
10. Un usuario sin permiso recibe HTTP 403, nunca datos parciales.
11. El código de insumo debe ser único por empresa.
12. Un insumo inactivo no puede recibir entradas ni usarse en recetas o lotes.
13. El costo unitario de un insumo no puede ser negativo.
14. El stock mínimo de un insumo no puede ser negativo.
15. El stock actual de un insumo no puede ser negativo.
16. Un insumo con movimientos de inventario no se elimina físicamente.
17. Toda entrada de insumo actualiza el stock actual y registra en Kardex.
18. Toda salida de insumo valida que haya stock suficiente antes de procesar.
19. El sistema no permite stock negativo salvo configuración explícita.
20. Las alertas de stock bajo se envían solo si el insumo tiene alertas habilitadas.
21. No se reenvía alerta de stock bajo antes de 24 horas para el mismo insumo.
22. Stock en cero fuerza envío de alerta inmediato sin respetar intervalo.
23. Stock recuperado sobre mínimo resetea el temporizador de alerta.
24. Tras 5 intentos fallidos de correo, la notificación queda en estado de error definitivo.
25. Una receta debe tener al menos un ingrediente activo.
26. Una receta con lotes activos en producción no puede editarse.
27. El costo estimado de una receta se calcula automáticamente con los costos unitarios vigentes.
28. Una receta solo puede clonarse si está activa o en prueba.
29. Un lote de producción creado queda en estado en_elaboracion.
30. Un lote no puede completarse sin stock suficiente de insumos de la receta.
31. Al completar un lote, los insumos se descuentan proporcionalmente a la cantidad producida.
32. Al completar un lote, el inventario de productos terminados se crea o incrementa.
33. El costo total de un lote incluye insumos, mano de obra, energía, agua, merma e indirectos.
34. El costo por unidad incluye el costo de la presentación (envase, tapa, etiqueta).
35. Un lote cancelado no afecta inventario ni Kardex.
36. Solo puede existir un registro de control de calidad por lote.
37. El resultado de control de calidad aprobado o rechazado es obligatorio al guardar.
38. Un lote rechazado en calidad puede registrarse completamente como merma.
39. Toda merma debe tener motivo detallado obligatorio.
40. La merma descuenta del inventario correspondiente y registra en Kardex.
41. El porcentaje de merma se compara contra el umbral del 5% para alertas en dashboard.
42. El nombre de la receta debe ser único por empresa.
43. El identificador fiscal del cliente debe ser único por empresa.
44. Un cliente inactivo no puede asignarse a una nueva venta.
45. Un cliente con ventas no puede eliminarse físicamente.
46. El precio de venta sugerido en la venta se toma según tipo de cliente y lista vigente.
47. El stock disponible para ventas es stock actual menos reservas activas.
48. No se puede vender más que el stock disponible.
49. Una reserva activa no puede usarse en otra venta hasta liberarse o vencerse.
50. El proveedor de una orden de compra debe estar activo.
51. Una orden de compra en borrador puede editarse; una enviada no puede modificarse sin permiso.
52. La recepción de compra no puede superar la cantidad solicitada salvo tolerancia configurada.
53. La recepción total cierra la orden; la recepción parcial la deja en estado parcialmente_recibida.
54. Una orden cancelada no acepta recepción de mercadería.
55. El código de equipo debe ser único por empresa.
56. Un equipo descartado no acepta nuevos movimientos de mantenimiento.
57. La próxima revisión vencida genera alerta en dashboard y en listado de equipos.
58. Los gastos operativos con documentos asociados no pueden eliminarse.
59. El monto de un gasto operativo debe ser mayor a cero.
60. Solo admin y auditor pueden acceder al reporte de auditoría.

---

# D. Validaciones y CHECK

## 100 validaciones

1. V001: `user_id` obligatorio en todas las operaciones manuales.
2. V002: `created_at` obligatorio y con zona horaria del sistema.
3. V003: `updated_at` obligatorio en entidades modificables.
4. V004: `status` obligatorio en toda entidad con ciclo de vida.
5. V005: IDs deben ser enteros positivos o UUID según entidad.
6. V006: Fechas deben rechazar formatos inválidos.
7. V007: No aceptar campos de texto con solo espacios en blanco.
8. V008: Longitud máxima de texto respetar límites definidos por campo.
9. V009: Correos deben tener formato válido RFC 5321.
10. V010: Teléfonos deben tener longitud mínima de 7 dígitos.
11. V011: Campos monetarios deben tener exactamente dos decimales.
12. V012: Montos no pueden ser NaN ni nulos si participan en totales.
13. V013: Cantidades deben ser numéricas y no NaN.
14. V014: Cantidades deben tener máximo cuatro decimales.
15. V015: Usuario autenticado obligatorio en toda llamada protegida.
16. V016: Usuario inactivo debe recibir HTTP 401 al autenticar.
17. V017: Contraseña debe tener mínimo 8 caracteres.
18. V018: Contraseña nunca almacenable en texto plano.
19. V019: Token JWT expirado debe rechazarse con HTTP 401.
20. V020: Rol obligatorio para usuario activo.
21. V021: Rol inactivo no puede asignarse a usuario.
22. V022: Correo de usuario único por empresa.
23. V023: Intentos fallidos de login deben registrarse en auditoría.
24. V024: Cambio de contraseña exige contraseña actual correcta.
25. V025: Código de insumo obligatorio.
26. V026: Código de insumo único por empresa.
27. V027: Nombre de insumo obligatorio.
28. V028: Tipo de insumo obligatorio (lista cerrada).
29. V029: Unidad de medida de insumo obligatoria.
30. V030: Costo unitario de insumo mayor o igual a cero.
31. V031: Stock mínimo mayor o igual a cero.
32. V032: Stock máximo mayor o igual a stock mínimo si ambos definidos.
33. V033: Stock actual mayor o igual a cero salvo configuración explícita.
34. V034: Insumo inactivo no puede recibir entradas de inventario.
35. V035: Insumo inactivo no puede incluirse en receta.
36. V036: Alerta de insumo requiere al menos un correo destinatario válido.
37. V037: Umbral personalizado de alerta mayor a cero si definido.
38. V038: Intervalo mínimo entre alertas mayor a cero horas.
39. V039: Máximo de reintentos de correo mayor a cero.
40. V040: Código de proveedor único por empresa.
41. V041: Razón social de proveedor obligatoria.
42. V042: Correo de proveedor debe ser válido si se ingresa.
43. V043: Proveedor con órdenes de compra no puede eliminarse físicamente.
44. V044: Proveedor inactivo no puede asignarse a nueva orden de compra.
45. V045: Nombre de receta obligatorio.
46. V046: Nombre de receta único por empresa.
47. V047: Tipo de cerveza obligatorio en receta.
48. V048: Volumen por lote mayor a cero.
49. V049: ABV estimado mayor o igual a cero.
50. V050: Receta debe tener al menos un ingrediente.
51. V051: Cantidad de ingrediente en receta mayor a cero.
52. V052: Unidad de ingrediente de receta obligatoria.
53. V053: Receta con lotes activos no puede editarse.
54. V054: Receta inactiva no puede asignarse a nuevo lote.
55. V055: Número de lote único por empresa.
56. V056: Receta de lote obligatoria.
57. V057: Tipo de presentación de lote obligatorio.
58. V058: Cantidad producida en lote mayor a cero.
59. V059: Fecha de producción de lote obligatoria.
60. V060: Responsable de lote obligatorio.
61. V061: Horas de mano de obra mayor o igual a cero.
62. V062: kWh consumidos mayor o igual a cero.
63. V063: Litros de agua mayor o igual a cero.
64. V064: Porcentaje de merma entre 0 y 100.
65. V065: Costo total de lote mayor o igual a cero.
66. V066: Lote no puede completarse sin stock suficiente de insumos.
67. V067: Lote en estado completado no puede editarse.
68. V068: Lote cancelado no puede completarse.
69. V069: Control de calidad requiere resultado aprobado o rechazado.
70. V070: Motivo de rechazo en calidad obligatorio si resultado es rechazado.
71. V071: Notas organolépticas entre 1 y 10.
72. V072: OG mayor a cero.
73. V073: FG mayor a cero y menor a OG.
74. V074: pH entre 0 y 14.
75. V075: Tipo de merma obligatorio (lista cerrada).
76. V076: Motivo detallado de merma obligatorio.
77. V077: Cantidad de merma mayor a cero.
78. V078: Cantidad de merma no puede superar stock disponible de la entidad.
79. V079: Identificador fiscal de cliente único por empresa.
80. V080: Nombre de cliente obligatorio.
81. V081: Tipo de cliente obligatorio (lista cerrada).
82. V082: Límite de crédito mayor o igual a cero.
83. V083: Cliente inactivo no puede asignarse a venta.
84. V084: Venta debe tener al menos una línea.
85. V085: Línea de venta requiere producto activo.
86. V086: Cantidad en línea de venta mayor a cero.
87. V087: Precio en línea de venta mayor o igual a cero.
88. V088: Cantidad vendida no puede superar stock disponible.
89. V089: Ganancia por línea calculada automáticamente.
90. V090: Reserva requiere cliente, producto, cantidad y fecha de entrega.
91. V091: Cantidad de reserva mayor a cero.
92. V092: Cantidad de reserva no puede superar stock disponible libre.
93. V093: Número de orden de compra único por empresa.
94. V094: Orden de compra requiere proveedor activo.
95. V095: Orden de compra requiere al menos una línea.
96. V096: Cantidad solicitada en orden mayor a cero.
97. V097: Precio unitario en orden mayor o igual a cero.
98. V098: Cantidad recibida no puede superar solicitada más tolerancia.
99. V099: Código de equipo único por empresa.
100. V100: Monto de gasto operativo mayor a cero.

---

# F. Endpoints REST

## Base

`/api/v1`

## 40 endpoints

1. `POST /api/v1/auth/login` — iniciar sesión, retorna token JWT.
2. `POST /api/v1/auth/logout` — cerrar sesión.
3. `GET /api/v1/auth/me` — obtener usuario autenticado.
4. `POST /api/v1/auth/change-password` — cambiar contraseña.
5. `GET /api/v1/users` — listar usuarios con filtros por rol y estado.
6. `POST /api/v1/users` — crear usuario (solo admin).
7. `GET /api/v1/users/{id}` — obtener detalle de usuario.
8. `PUT /api/v1/users/{id}` — editar usuario.
9. `PATCH /api/v1/users/{id}/toggle-status` — activar o desactivar usuario.
10. `GET /api/v1/suppliers` — listar proveedores.
11. `POST /api/v1/suppliers` — crear proveedor.
12. `PUT /api/v1/suppliers/{id}` — actualizar proveedor.
13. `PATCH /api/v1/suppliers/{id}/toggle-status` — activar o desactivar proveedor.
14. `GET /api/v1/supplies` — listar insumos con filtros.
15. `POST /api/v1/supplies` — crear insumo.
16. `GET /api/v1/supplies/{id}` — obtener insumo.
17. `PUT /api/v1/supplies/{id}` — actualizar insumo.
18. `PATCH /api/v1/supplies/{id}/toggle-status` — activar o desactivar insumo.
19. `GET /api/v1/supplies/{id}/kardex` — Kardex del insumo.
20. `GET /api/v1/supplies/low-stock` — insumos bajo stock mínimo.
21. `POST /api/v1/supply-entries` — registrar entrada de insumo.
22. `GET /api/v1/supply-entries` — listar entradas de insumos.
23. `GET /api/v1/recipes` — listar recetas.
24. `POST /api/v1/recipes` — crear receta.
25. `GET /api/v1/recipes/{id}` — obtener receta con ingredientes.
26. `PUT /api/v1/recipes/{id}` — actualizar receta.
27. `POST /api/v1/recipes/{id}/clone` — clonar receta.
28. `GET /api/v1/batches` — listar lotes de producción.
29. `POST /api/v1/batches` — crear lote.
30. `GET /api/v1/batches/{id}` — obtener lote con detalle de insumos.
31. `PUT /api/v1/batches/{id}` — editar lote en elaboración.
32. `POST /api/v1/batches/{id}/complete` — completar lote.
33. `POST /api/v1/batches/{id}/cancel` — cancelar lote.
34. `POST /api/v1/batches/{id}/quality-check` — registrar control de calidad.
35. `GET /api/v1/products` — listar inventario de productos terminados.
36. `PUT /api/v1/products/{id}/price` — actualizar precio de venta.
37. `POST /api/v1/sales` — registrar venta.
38. `GET /api/v1/sales` — listar ventas con filtros.
39. `GET /api/v1/customers` — listar clientes.
40. `POST /api/v1/customers` — crear cliente.

---

# G. Estados recomendados por módulo

## Usuarios

`active`, `inactive`

## Insumos y proveedores

`active`, `inactive`

## Recetas

`active`, `inactive`, `en_prueba`

## Lotes de producción

`en_elaboracion`, `completado`, `cancelado`

## Control de calidad

`aprobado`, `rechazado`

## Inventario de productos

`active`, `inactive`

## Ventas

`completada`, `anulada`

## Reservas de stock

`activa`, `consumida`, `liberada`, `vencida`

## Órdenes de compra

`borrador`, `enviada`, `parcialmente_recibida`, `recibida`, `cancelada`

## Equipos

`operativo`, `mantenimiento`, `fuera_servicio`, `descartado`

## Notificaciones

`queued`, `sent`, `failed`

---

# H. Modelo básico de permisos

1. `supplies.read`
2. `supplies.create`
3. `supplies.update`
4. `supplies.toggle-status`
5. `supply-entries.create`
6. `recipes.read`
7. `recipes.create`
8. `recipes.update`
9. `recipes.clone`
10. `batches.read`
11. `batches.create`
12. `batches.complete`
13. `batches.cancel`
14. `batches.quality-check`
15. `waste.create`
16. `waste.read`
17. `products.read`
18. `products.update-price`
19. `sales.read`
20. `sales.create`
21. `customers.read`
22. `customers.create`
23. `customers.update`
24. `reservations.create`
25. `reservations.manage`
26. `purchase-orders.read`
27. `purchase-orders.create`
28. `purchase-orders.receive`
29. `purchase-orders.cancel`
30. `suppliers.read`
31. `suppliers.create`
32. `suppliers.update`
33. `equipment.read`
34. `equipment.create`
35. `equipment.movement`
36. `expenses.read`
37. `expenses.create`
38. `reports.read`
39. `reports.export`
40. `admin.users`
41. `admin.settings`
42. `audit.read`

---

# I. Endpoint recomendado como patrón principal

El mejor patrón para BrewMaster es:

```http
POST /api/v1/{resource}/{id}/{action}
```

Solo para acciones de negocio que cambian estado.

Ejemplos correctos:

```http
POST /api/v1/batches/{id}/complete
POST /api/v1/batches/{id}/cancel
POST /api/v1/batches/{id}/quality-check
POST /api/v1/purchase-orders/{id}/send
POST /api/v1/purchase-orders/{id}/receive
POST /api/v1/reservations/{id}/consume
POST /api/v1/reservations/{id}/release
```

Para CRUD normal:

```http
GET    /api/v1/supplies
POST   /api/v1/supplies
GET    /api/v1/supplies/{id}
PUT    /api/v1/supplies/{id}
PATCH  /api/v1/supplies/{id}/toggle-status
```

Este diseño es simple, consistente y escalable para web, móvil o integraciones futuras.

---

# J. Desarrollo SDD para BREWMASTER

## J.1 Metadatos de control

| campo | valor |
|---|---|
| proyecto | `BREWMASTER` |
| producto | Sistema web de gestión para cervecerías artesanales |
| version_spec | `sdd-2026-06-24` |
| workflow | `sdd-extended-1.0` |
| arnes | obligatorio |
| orquestador | obligatorio |
| entrada valida | `harness.run_agent(agent_id, state)` |
| estado objetivo | especificacion lista para planificacion e implementacion |
| costo externo permitido | `0.000000 USD` en modo local deterministico |
| no_inventar | `true` |

## J.2 Alcance cerrado para MVP

Incluye:

1. Autenticación JWT, usuarios, roles, permisos y auditoría.
2. Proveedores, insumos, bodegas, tipos de presentación y Kardex de insumos.
3. Entradas de insumos, alertas de stock bajo por correo y cola de notificaciones.
4. Recetas con ingredientes, costo estimado y clonado.
5. Lotes de producción, completar lote, control de calidad y mermas.
6. Inventario de productos terminados, precios de venta y Kardex de productos.
7. Clientes, ventas, reservas de stock y precios por tipo de cliente.
8. Proveedores, órdenes de compra, recepción parcial y total.
9. Equipos, historial de mantenimientos y alertas de revisión vencida.
10. Gastos operativos, reportes financieros básicos y metas mensuales.
11. Dashboard con KPIs reales, gráficos y alertas operacionales.
12. Reportes exportables: producción, ventas, inventario, Kardex, mermas, costos, financiero y auditoría.

Excluye del MVP:

1. Integración con sistemas tributarios externos o facturación electrónica.
2. Contabilidad completa y conciliación bancaria.
3. Aplicación móvil nativa.
4. POS fiscal certificado.
5. Multiempresa con consolidación.
6. Deploy productivo, lectura de secretos o acceso a datos reales sin aprobación.

## J.3 Supuestos funcionales

1. La empresa opera con una moneda base y zona horaria configurables.
2. El stock disponible se calcula como stock actual menos reservas activas.
3. La eliminación física no se usa para entidades con historial operativo.
4. El costo por unidad de producto incluye costo de producción más costo de presentación.
5. Las alertas de stock por correo respetan un intervalo mínimo configurable de 24 horas.
6. El dashboard carga datos reales en tiempo real o con caché de corta duración.
7. Las exportaciones de reportes quedan registradas en auditoría.
8. La configuración SMTP se almacena encriptada.

## J.4 Arquitectura objetivo

Capas:

1. Frontend web: aplicación responsive con rutas protegidas por rol, formularios con validación local, tablas paginadas y estados de carga, vacío y error.
2. API REST: `/api/v1`, validación de entrada, permisos por acción, transacciones por caso de uso y respuestas JSON consistentes.
3. Dominio: servicios por módulo con reglas de negocio puras y eventos de auditoría.
4. Persistencia: base relacional con constraints, índices y eliminación lógica.
5. Jobs: alertas de stock, reintentos de correo, vencimientos de reservas y backups.
6. Observabilidad: logs estructurados, auditoría funcional y métricas de errores.

Stack tecnológico:

| capa | tecnología |
|---|---|
| frontend | React + Bootstrap |
| backend | Python 3 + FastAPI |
| ORM | SQLAlchemy + Alembic |
| base de datos | MySQL o MariaDB |
| jobs | APScheduler |
| autenticación | JWT con refresh token |
| reportes | CSV / XLSX / PDF |
| documentación API | Swagger / OpenAPI automático con FastAPI |
| archivos exportados | almacenamiento local o compatible S3 |

## J.5 Modelo de dominio canónico

Usuarios y seguridad:

| entidad | propósito | campos clave |
|---|---|---|
| `users` | identidad operativa | `id`, `nombre`, `email`, `password_hash`, `rol`, `estado`, `created_at` |
| `roles` | roles del sistema | `id`, `nombre`, `descripcion`, `estado` |
| `permissions` | permisos por acción | `id`, `codigo`, `descripcion`, `modulo` |
| `role_permissions` | relación rol-permiso | `role_id`, `permission_id` |
| `audit_logs` | historial de acciones | `user_id`, `action`, `entity`, `entity_id`, `detail`, `ip_address`, `created_at` |
| `settings` | configuración global | `key`, `value` (encriptado si sensible) |

Insumos y proveedores:

| entidad | propósito | campos clave |
|---|---|---|
| `suppliers` | proveedores | `codigo`, `nombre`, `email`, `telefono`, `contacto`, `condicion_pago`, `estado` |
| `warehouses` | bodegas | `codigo`, `nombre`, `tipo`, `responsable`, `capacidad`, `temperatura_controlada`, `estado` |
| `supply_categories` | categorías de insumos | `id`, `nombre`, `descripcion`, `estado` |
| `supplies` | insumos | `codigo`, `nombre`, `tipo`, `unidad_medida`, `proveedor_id`, `bodega_id`, `costo_unitario`, `stock_minimo`, `stock_actual`, `enable_email_alerts`, `alert_emails`, `last_alert_sent_at`, `estado` |
| `supply_movements` | Kardex de insumos | `supply_id`, `tipo_movimiento`, `cantidad`, `costo_unitario`, `saldo_resultante`, `referencia`, `user_id`, `created_at` |
| `supply_entries` | entradas de insumos | `supply_id`, `cantidad`, `costo_unitario`, `proveedor_id`, `referencia`, `user_id` |
| `notification_queue` | cola de correos | `supply_id`, `recipients`, `subject`, `body_html`, `status`, `attempts`, `sent_at`, `error_message` |

Recetas y producción:

| entidad | propósito | campos clave |
|---|---|---|
| `beer_styles` | estilos de cerveza | `id`, `nombre`, `descripcion`, `abv_min`, `abv_max`, `ibu_min`, `ibu_max` |
| `presentation_types` | tipos de presentación | `nombre`, `volumen`, `unidad`, `costo_presentacion`, `estado` |
| `recipes` | recetas de cerveza | `nombre`, `tipo`, `abv_estimado`, `volumen_por_lote`, `pasos_elaboracion`, `costo_estimado`, `estado` |
| `recipe_ingredients` | ingredientes de receta | `recipe_id`, `supply_id`, `cantidad`, `unidad` |
| `production_batches` | lotes de producción | `numero_lote`, `recipe_id`, `presentation_type_id`, `cantidad_producida`, `fecha_produccion`, `responsable_id`, `estado`, `horas_mano_obra`, `kwh_consumidos`, `litros_agua`, `porcentaje_merma`, `costo_total`, `costo_por_litro`, `costo_por_unidad` |
| `batch_quality_checks` | control de calidad | `batch_id`, `og`, `fg`, `abv_calculado`, `ph`, `temp_fermentacion`, `nota_aroma`, `nota_sabor`, `resultado`, `motivo_rechazo`, `responsable_id` |
| `waste_records` | mermas | `tipo_entidad`, `entidad_id`, `cantidad_perdida`, `costo_unitario`, `costo_total`, `tipo_merma`, `motivo_detallado`, `responsable_id`, `fecha`, `batch_id` |

Inventario de productos y ventas:

| entidad | propósito | campos clave |
|---|---|---|
| `finished_products` | inventario productos terminados | `recipe_id`, `presentation_type_id`, `cantidad_stock`, `costo_unitario`, `precio_venta`, `fecha_vencimiento_aprox`, `estado` |
| `product_movements` | Kardex de productos | `product_id`, `tipo_movimiento`, `cantidad`, `costo_unitario`, `saldo_resultante`, `referencia`, `user_id` |
| `customer_types` | tipos de cliente | `id`, `nombre`, `descripcion`, `descuento_pct_base` |
| `customers` | clientes | `nombre`, `identificador_fiscal`, `email`, `telefono`, `tipo_cliente`, `forma_pago`, `limite_credito`, `estado` |
| `product_prices` | precios por tipo de cliente | `product_id`, `tipo_cliente`, `precio_unitario`, `precio_por_docena`, `descuento_pct`, `vigente_desde`, `vigente_hasta` |
| `sales` | ventas | `numero_documento`, `cliente_id`, `fecha_venta`, `responsable_id`, `total`, `ganancia_total` |
| `sale_items` | líneas de venta | `sale_id`, `product_id`, `cantidad`, `precio_unitario`, `costo_unitario`, `ganancia_unitaria` |
| `stock_reservations` | reservas de stock | `cliente_id`, `product_id`, `cantidad_reservada`, `fecha_entrega_prometida`, `precio`, `estado` |

Compras, equipos y finanzas:

| entidad | propósito | campos clave |
|---|---|---|
| `purchase_orders` | órdenes de compra | `numero_orden`, `proveedor_id`, `fecha_emision`, `fecha_esperada_recepcion`, `total_estimado`, `estado` |
| `purchase_order_items` | líneas de orden de compra | `order_id`, `supply_id`, `cantidad_solicitada`, `precio_unitario`, `cantidad_recibida` |
| `equipment_types` | tipos de equipo | `id`, `nombre`, `descripcion`, `intervalo_revision_dias` |
| `equipment` | equipos | `codigo`, `nombre`, `tipo`, `marca`, `modelo`, `serie`, `fecha_compra`, `costo_adquisicion`, `estado`, `ultima_mantencion`, `proxima_revision` |
| `equipment_movements` | historial de equipos | `equipment_id`, `tipo_movimiento`, `descripcion`, `costo`, `fecha`, `responsable_id` |
| `expense_categories` | categorías de gastos | `id`, `nombre`, `descripcion`, `estado` |
| `operational_expenses` | gastos operativos | `concepto`, `categoria`, `monto`, `fecha`, `proveedor`, `documento_referencia`, `responsable_id` |
| `monthly_goals` | metas mensuales | `mes`, `litros_produccion`, `monto_ventas`, `num_clientes`, `margen_promedio_pct` |
| `password_reset_tokens` | tokens de recuperación de contraseña | `user_id`, `token_hash`, `expires_at`, `used_at`, `created_at` |
| `export_jobs` | trabajos de exportación diferidos | `id`, `user_id`, `tipo_reporte`, `filtros`, `estado`, `archivo_url`, `created_at`, `completed_at` |
| `smtp_config` | configuración de servidor de correo | `id`, `host`, `port`, `username`, `password_encrypted`, `from_email`, `use_tls`, `updated_by` |
| `batch_supply_snapshots` | snapshot de insumos al completar lote | `batch_id`, `supply_id`, `cantidad_usada`, `costo_unitario_momento`, `nombre_insumo` |

## J.6 Reglas transaccionales críticas

1. Completar un lote debe validar stock, descontar insumos, actualizar inventario de productos y calcular costos en una sola transacción.
2. La entrada de insumo debe actualizar stock y registrar Kardex en la misma transacción.
3. La venta debe validar stock disponible, descontar inventario y registrar Kardex en la misma transacción.
4. La recepción de orden de compra debe generar entrada de inventario y actualizar el estado de la orden en la misma transacción.
5. La reserva de stock debe calcularse siempre sobre stock actual menos suma de reservas activas.
6. La merma debe descontar del inventario y registrar en Kardex de forma atómica.
7. El envío de alertas de correo no debe bloquear el flujo principal; se encola y procesa asíncronamente.
8. El backup de base de datos no debe interrumpir operaciones; se ejecuta en horario de baja actividad.
9. Toda acción de cambio de estado debe ser idempotente o rechazar repetición con el estado actual explícito.
10. El cálculo de costo de lote debe ejecutarse solo al completar y no puede modificarse posterior.

## J.7 Contrato de API

Formato común de respuesta exitosa:

```json
{
  "data": {},
  "meta": {
    "request_id": "REQ-TBD",
    "timestamp": "2026-06-24T00:00:00Z"
  }
}
```

Formato común de error:

```json
{
  "error": {
    "code": "validation_error",
    "message": "La solicitud contiene campos inválidos.",
    "details": [
      {
        "field": "cantidad",
        "issue": "must_be_greater_than_zero"
      }
    ]
  },
  "meta": {
    "request_id": "REQ-TBD"
  }
}
```

Códigos mínimos:

| codigo | uso |
|---|---|
| `validation_error` | input inválido |
| `permission_denied` | permiso insuficiente, HTTP 403 |
| `not_found` | recurso inexistente o inaccesible, HTTP 404 |
| `state_conflict` | acción no permitida por estado actual |
| `stock_unavailable` | stock insuficiente para la operación |
| `inactive_entity` | entidad inactiva no puede usarse |
| `duplicate_record` | unicidad violada |
| `auth_error` | credenciales inválidas o token expirado |

## J.8 Requisitos no funcionales

| id | requisito | criterio |
|---|---|---|
| RNF-01 | Seguridad | contraseñas con bcrypt, JWT expirable, RBAC por rol en cada endpoint |
| RNF-02 | Auditoría | 100% de cambios críticos con actor, fecha, entidad, acción e IP |
| RNF-03 | Rendimiento | listados paginados; API responde bajo 800 ms en consultas comunes con índices |
| RNF-04 | Integridad | transacciones en producción, ventas, compras e inventario |
| RNF-05 | Disponibilidad | jobs reintentables e idempotentes; notificaciones asíncronas |
| RNF-06 | Exportación | reportes exportables con CSV, XLSX y PDF según tipo |
| RNF-07 | Accesibilidad | interfaz responsive en móvil, tablet y escritorio |
| RNF-08 | Observabilidad | logs estructurados con request_id, user_id, módulo y latencia |
| RNF-09 | Privacidad | costos y datos financieros ocultos sin permiso explícito |
| RNF-10 | Mantenibilidad | Swagger/OpenAPI activo, migraciones versionadas con Alembic, tests por módulo |

## J.9 Criterios de aceptación por módulo

| módulo | aceptación mínima |
|---|---|
| Usuarios y auth | login, JWT, roles, CRUD usuarios y auditoría de accesos |
| Insumos | CRUD, Kardex trazable, alertas de stock bajo con correo e intervalo respetado |
| Recetas | CRUD, cálculo de costo, clonado y bloqueo si tiene lotes activos |
| Producción | crear lote, completar con descuento de insumos, calidad, merma y costo calculado |
| Inventario productos | stock actualizado al completar lote, precio editable, Kardex trazable |
| Ventas | registrar venta con stock validado, ganancia calculada y Kardex actualizado |
| Reservas | crear, liberar y convertir en venta con stock disponible correcto |
| Compras | orden, recepción parcial/total y entrada de inventario automática |
| Equipos | CRUD, historial de mantenimientos y alerta de revisión vencida |
| Finanzas | gastos operativos, reportes financieros básicos y metas mensuales |
| Dashboard | KPIs reales, gráficos y alertas operacionales descartables |
| Reportes | todos los tipos exportables con filtros de fecha y permisos aplicados |

## J.10 Estrategia de pruebas

Pruebas unitarias:

1. Validaciones V001 a V100.
2. Cálculo de costo de lote: insumos, mano de obra, energía, agua, merma e indirectos.
3. Cálculo de costo por litro y costo por unidad con costo de presentación.
4. Cálculo de stock disponible: stock actual menos reservas activas.
5. Lógica de disparo de alerta de stock: umbral, intervalo y stock en cero.
6. Transiciones de estado por módulo: lotes, órdenes de compra, reservas.
7. Cálculo de ganancia de venta por línea.

Pruebas de integración:

1. Entrada de insumo actualiza stock y registra Kardex.
2. Completar lote descuenta insumos, actualiza inventario de productos y calcula costo.
3. Venta descuenta inventario de productos y registra Kardex.
4. Recepción de orden de compra genera entrada de inventario y actualiza estado de orden.
5. Merma descuenta inventario y registra Kardex.
6. Alerta de stock bajo encola notificación y respeta intervalo de 24 horas.
7. Stock en cero fuerza alerta inmediata.
8. Worker de correos procesa reintentos y marca error definitivo tras 5 intentos.

Pruebas E2E:

1. Login, crear insumo, registrar entrada, verificar Kardex.
2. Crear receta, crear lote, completar lote, verificar inventario de productos.
3. Registrar venta, verificar stock descontado y Kardex de producto.
4. Crear orden de compra, recepcionar, verificar stock de insumo.
5. Reporte de producción exportado a XLSX con filtros de fecha.

## J.11 Trazabilidad macro

| requisito | fuente | prueba requerida | evidencia |
|---|---|---|---|
| REQ-INS | UC-INS-01..06 | unit + integración insumos | Kardex, stock, alertas, correos |
| REQ-REC | UC-REC-01..02 | unit recetas | ingredientes, costo, clonado |
| REQ-PROD | UC-PROD-01..04 | integración producción | lote, calidad, merma, costo |
| REQ-PRO | UC-PRO-01..02 | integración inventario productos | stock, precio, Kardex |
| REQ-VTA | UC-VTA-01..05 | integración ventas | cliente, venta, reserva, stock |
| REQ-COM | UC-COM-01..02 | integración compras | orden, recepción, inventario |
| REQ-EQU | UC-EQU-01..02 | unit equipos | historial, alertas revisión |
| REQ-FIN | UC-FIN-01..03 | integración finanzas | gastos, reportes, metas |
| REQ-REP | UC-REP-01..02 | E2E reportes | exportación, filtros, permisos |
| REQ-ALT | UC-ALT-01..03 | integración alertas | SMTP, cola, reintentos, metas |

## J.12 Ciclo de desarrollo por hitos

| hito | nombre | entregable principal |
|---|---|---|
| 1 | Fundamentos | Auth JWT, usuarios, roles, auditoría, estructura de proyecto |
| 2 | Maestros | Proveedores, insumos, bodegas, recetas, tipos de presentación |
| 3 | Inventario | Entradas de insumos, Kardex, notificaciones email, configuración SMTP |
| 4 | Producción | Lotes, control de calidad, mermas, inventario de productos terminados |
| 5 | Ventas | Clientes, ventas, reservas de stock, precios por tipo de cliente, órdenes de compra |
| 6 | Dashboard | KPIs reales, gráficos, alertas operacionales, reportes exportables |
| 7 | Cierre | Equipos, finanzas, metas, respaldos automáticos, documentación y pruebas |

## J.13 Registro de consumo y optimización

Política de consumo:

1. Modo de este desarrollo: local determinístico sin llamadas externas.
2. Si se usa API real en el futuro, se debe registrar consumo por fase y modelo.
3. Si falta tarifa oficial, el costo queda como no determinable; no se inventa precio.

Optimizaciones obligatorias:

1. Consultar Kardex con filtros de fecha e índices; nunca cargar tabla completa.
2. Alertas de correo asíncronas; no bloquean el flujo de registro de movimientos.
3. Dashboard calcula KPIs con agregaciones SQL; no itera en Python sobre colecciones grandes.
4. Reportes pesados se ejecutan como jobs con resultado en archivo; no en respuesta HTTP síncrona.
5. Stock disponible se calcula con una consulta que suma reservas activas; no en lógica de aplicación.
6. Exportaciones XLSX y PDF se generan en background y se notifican al usuario cuando están listas.
7. Índices obligatorios en: `supply_id + created_at` en movimientos, `status` en lotes, `cliente_id + fecha` en ventas.
8. Paginación obligatoria en todos los endpoints de listado.

## J.14 Riesgos y decisiones

| riesgo | impacto | mitigación |
|---|---|---|
| Stock concurrente en ventas | sobreventa | transacciones con lock por producto en venta y reserva |
| Correo SMTP no configurado | alertas silenciosas | validar config SMTP al iniciar y mostrar advertencia en dashboard |
| Costo de lote incorrecto | márgenes erróneos | validar todos los componentes antes de permitir completar lote |
| Receta modificada post-lote | inconsistencia histórica | bloquear edición si hay lotes activos; guardar snapshot en lote |
| Reportes de alto volumen | latencia alta | jobs diferidos con archivo exportado; límite de rango de fechas |
| Backups fallidos | pérdida de datos | registrar fallo en auditoría y notificar a admin por correo |

## J.15 Gate de cierre de especificación

La especificación queda lista cuando:

1. Los módulos MVP tienen casos de uso, pantallas, reglas, validaciones y endpoints.
2. El modelo de dominio cubre todas las entidades críticas con sus campos y relaciones.
3. Cada requisito macro tiene prueba requerida y evidencia esperada.
4. El plan de hitos de desarrollo está definido y es incremental.
5. Los riesgos principales están identificados con su mitigación.
6. No hay deploy, secretos, correo real ni integraciones externas ejecutadas sin aprobación.
