# CLAUDE.md — Espacio Querido (cockpit operativo)

Contexto del producto para construir la app. **Esto describe cómo se piensa la app: el modelo mental, el orden de las hojas y qué hace cada función.** No habla de tecnología, ni de cómo se guardan los datos, ni de cómo se arma por dentro. Solo del producto.

Idioma del producto y del trabajo: **español**.

---

## Stack y documentos del proyecto (leer — son ley)

Este `CLAUDE.md` describe **el producto**. La parte técnica vive en documentos separados que
**debes consultar** antes de trabajar:

| Documento | Qué contiene | Cuándo leerlo |
|---|---|---|
| `PROJECT_PLAN.md` | Arquitectura, modelo de tenants, sistema de vistas, tipos, estado vivo. | Para entender alcance y decisiones. |
| `BUILD_PLAN.md` | Backlog técnico por fase (F0–F8). | Tu backlog: toma la siguiente tarea sin marcar. |
| `UI_RULES.md` | Ley de diseño + convenciones + cicatrices técnicas (Parte B). | ANTES de tocar cualquier UI. |
| `PERMISSIONS.md` | Reglas de acceso (categorías de tenant, vistas, niveles, login). | ANTES de tocar accesos o scope. Fuente única. |

**Stack:** Django + HTMX + Alpine.js + Tailwind + Flowbite (server-rendered) — la plantilla base del
folder. Gráficas con ApexCharts; i18n de Django (es base + en). Datos: capa de servicios/mock en
Python que se formaliza en modelos Django + SQLite por pantalla; multi-tenant y permisos
**server-side**. Detalle en `PROJECT_PLAN.md` §2.

**Nota:** "tokens" tiene dos significados en esta app — *design tokens* (CSS, UI) y *tokens de IA*
(saldo de negocio que administra el Admin). No confundir. Ver `PROJECT_PLAN.md` §6.

---

## 1. Qué es y para quién

Es la app operativa de una correduría inmobiliaria. La usan el coordinador y los asesores para llevar el día a día: leads, conversaciones, citas, ofertas, cierres y comisiones. Detrás de cada etapa hay agentes de IA que hacen el trabajo repetitivo; el humano supervisa y aprueba.

## 2. El modelo mental en una frase

> **El lead es la unidad de operación. Los agentes de IA son el motor que lo mueve por el embudo. El humano decide.**

## 3. Las cuatro ideas que rigen todo

1. **Operación-céntrica, no agente-céntrica.** Lo central es la operación (un lead en proceso de compra o renta), no la herramienta. Todo gira alrededor de "¿en qué etapa está esta operación y qué sigue?".
2. **La IA es el motor; el humano aprueba.** Los agentes proponen (redactan respuestas, califican, agendan), pero las acciones que importan pasan por una aprobación humana. El humano nunca pierde el control.
3. **Doble eje de scoring.** Cada lead se lee en dos dimensiones:
   - **Calificación / fit** → qué tan buen candidato es. Grado **A / B / C** (más un 0–100). Se explica con **BANT**: presupuesto, financiamiento/decisor, necesidad/zona, horizonte de tiempo.
   - **Temperatura / engagement** → qué tan activo/interesado está ahora. **Caliente / tibio / frío**, por comportamiento.
4. **Todo termina en "qué hago ahora".** Cada hoja no solo informa: apunta a la siguiente acción. La combinación de los dos ejes la define (p. ej. A + caliente = prioridad; A + frío = nutrir; C + caliente = revisar inventario).

## 4. Cómo está ordenada la app (y por qué)

El menú agrupa las hojas por **intención**, de lo más cotidiano a lo más administrativo:

- **Operación** → el día a día (donde se vive la app).
- **Analítica** → cómo vamos (el dinero y el desempeño).
- **Automatizaciones + IA** → el motor (los agentes y sus reglas).
- **Sistema operativo** → los rituales del equipo.
- **Administración** → el equipo y los ajustes.

---

## 5. Recorrido de cada hoja (propósito + qué se hace ahí)

### OPERACIÓN

**Pipeline** *(home)*
- Tablero kanban de operaciones por etapa. Las columnas son las etapas que mueven los agentes: Nuevos → Calificados → Citas → Negociación → Cierre → Reactivación.
- Arriba, una tira de indicadores del estado del negocio.
- Sección **"Por aprobar"**: lo que la IA propone y espera el visto bueno del humano.
- Funciones: ver el negocio de un vistazo, aprobar o rechazar lo que sugiere la IA, abrir una operación para ver el detalle.

**Leads**
- Directorio de todos los leads: de dónde viene cada uno (fuente), en qué etapa está, qué asesor lo lleva, su calificación y su temperatura.
- Funciones: buscar y filtrar, entrar al detalle de cualquier lead.

**Conversaciones**
- Bandeja tipo chat (WhatsApp y otras fuentes). Tres zonas: lista de conversaciones, el hilo, y a la derecha el **perfil del lead**.
- El perfil muestra, en este orden: **scoring de la IA** (arriba, destacado), de dónde viene, qué busca y su comportamiento.
- La IA **redacta una respuesta sugerida** con un nivel de confianza; el humano la aprueba y se envía.
- Funciones: leer la conversación, entender el perfil/scoring, aprobar (o ajustar) la respuesta sugerida.

**Libros** *(dos pestañas)*
- **Libro de comisiones**: el registro maestro de operaciones. Guarda el **timestamp de cada cambio
  de etapa** (se registran TODAS las transiciones), y conserva la **fecha oficial de venta** y la
  **fecha oficial de cobro** (recibo del dinero). Por operación: info del lead/cliente, la propiedad
  comprada (nombre, tipo, municipio), a cuánto se vendió, comisión total y su **reparto**
  (vendedor/asesor, agencia/EQ, coordinador), con %/monto por cada uno; contrato del asesor (modelo),
  tipo de operación (venta/renta), status de cierre y status de pago. Incluye agregar operaciones
  históricas.
- **Objetivos**: meta del equipo y meta por asesor.

### ANALÍTICA

**Ventas — Dashboard de comisiones** *(cuatro pestañas)*
- Es el reporte de cómo va el dinero del mes.
- **Cierres**: indicadores (operaciones, facturado, por cobrar, en separación, ofrecimiento, portafolio), cumplimiento de la meta, embudo de comisiones, top asesores y tendencia por semana.
- **Por cobrar**: cuánto y de quién está pendiente de cobro, con qué urgencia (más urgente entre más días lleva separada la propiedad).
- **Ofrecimientos**: operaciones en oferta por asesor y el detalle de cada una (cliente, zona, comisión, comentarios).
- **Soporte & FAQ**: ayuda del reporte.

**Team performance** *(dos pestañas)*
- **Resumen**: indicadores del equipo, ranking por avance hacia la meta y el "por qué" de cada sugerencia (las señales que la generan).
- **Por asesor**: métricas duras + habilidades blandas + el foco de mejora + la nota de su 1:1.

**Funnel performance** *(se combina dentro de Pipeline)*
- El embudo del negocio etapa por etapa con la conversión entre pasos **vive como una vista dentro
  de Pipeline** (kanban + embudo son dos lecturas de la misma data de etapas). No es hoja aparte.

### AUTOMATIZACIONES + IA

**Agentes IA** *(pestañas — el motor de la operación)*
- **Listing Manager**: capta y gestiona los listings; muestra el proceso completo y dónde entra el humano.
- **Calificador**: toma señales y asigna calificación y temperatura; lleva un registro de recalificaciones.
- **Love Bomber**: nutre a los leads calientes (con límite diario y regla de "solo calientes"); puede empujar a agendar cita.
- **Scheduler**: agenda citas con el asesor y el calendario, y confirma.
- **Reminder**: tablero de confirmaciones y recordatorios.
- **Inventario Easy Broker**: propiedades disponibles con su % de match contra lo que busca el lead.
- **Integraciones**: conectores con las fuentes y la bitácora de sincronizaciones.
- **Reglas**: hasta dónde puede actuar sola la IA y qué requiere aprobación (diales de autonomía).

### SISTEMA OPERATIVO

**Junta semanal** *(antes "Money Monday")*
- Reporte semanal del ritual: una fila por consultor con **asistencia**, **cant. clientes hot**,
  **seguimiento de leads + a quién se está trabajando**, y los conteos **reales de la semana pasada**
  (ofrecimientos, separaciones, citas) vs el **plan de esta semana** (citas). Cierra con la
  **evaluación al consultor** (Asignar leads / OK / Feedback c/ coordinador) y **comentarios
  generales**. Encabezado con las fechas de "reales semana pasada" y "plan de esta semana".

**1:1**
- **Evaluación semanal de KPIs por asesor** para ver cómo va y decidir sus **puntos a reforzar**.
  Muestra, contra su **objetivo**: asistencia 1:1, actualización de status y de comentarios, citas,
  evaluación de la junta semanal, **conversión de citas** (leads→citas) y **conversión global**
  (leads→cierres), cada uno con su % y semáforo (Excelente/Bueno/Aceptable). Además el **punto a
  reforzar del embudo** (p. ej. captaciones) y un **comentario al asesor**. Cubre asistencia, ventas,
  qué tiene por vender / por cobrar, cantidad de clientes y atención a leads.

### ADMINISTRACIÓN

**Asesores**
- Directorio del equipo (pipeline activo, vendido, % de meta) y alta de un nuevo asesor.

**Configuración**
- Ajustes generales.

---

## 6. El detalle de una operación (pieza transversal)

Al abrir cualquier operación se ve, en este orden mental:
1. La **sugerencia del copiloto** (qué conviene hacer).
2. El **scoring de dos ejes**: calificación (con su desglose BANT) y temperatura (con su porqué).
3. La **siguiente acción** recomendada.
4. Las **propiedades** asociadas.
5. La **actividad y trazabilidad** (de dónde vino el lead, su id en la fuente, qué asesor lo lleva).
6. Si se descarta, el **motivo de rechazo**.

---

## 7. Vocabulario (conceptos, no detalles técnicos)

- **Operación**: un lead en proceso de compra o renta. Unidad central.
- **Etapas**: Nuevos, Calificados, Citas, Negociación, Cierre, Reactivación.
- **Calificación (fit)**: A/B/C, explicada por BANT.
- **Temperatura (engagement)**: caliente, tibio, frío.
- **Siguiente acción**: lo que dispara la combinación de los dos ejes.
- **Agente**: pieza de IA que hace una parte del trabajo (captar, calificar, nutrir, agendar, recordar).

## 8. Reglas de producto / tono

- Lenguaje claro y operativo, en español.
- Cada hoja debe responder "¿qué hago ahora?", no solo mostrar datos.
- La IA **explica** sus sugerencias (transparencia): siempre hay un "por qué".
- La IA propone, el humano aprueba lo importante.
- Los datos de contacto de los leads son sensibles: se tratan con cuidado como principio (no exponerlos de más).
