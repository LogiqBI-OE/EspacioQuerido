# BUILD_PLAN.md — Espacio Querido

Backlog técnico. Stack **Django + HTMX + Alpine + Tailwind + Flowbite** (server-rendered). Cada tarea
traza a una hoja/función del producto (`PROJECT_PLAN.md`) y respeta la ley de diseño (`UI_RULES.md`)
y de acceso (`PERMISSIONS.md`). Toma la siguiente tarea **sin marcar** de la fase activa. Marca su
checkbox al cerrarla y actualiza §9 de `PROJECT_PLAN.md` al terminar una fase.

Convención: cada tarea tiene un **Verify** (criterio verificable) — no está lista hasta que pasa.

**Nota de datos:** cada app arranca con una **capa de servicios/mock en Python** (`services.py`
devolviendo datos seed, tenant-scoped) y **formaliza modelos Django + SQLite** cuando la pantalla
estabiliza su data. Permisos **server-side** siempre; nada de decidir acceso en el template solo por
ocultar.

---

## F0 — Esqueleto + tenancy

Base del proyecto Django y el sistema de vistas. Es lo más pesado del arranque.

- [ ] **Proyecto Django**: `manage.py`, proyecto + settings (dev SQLite), `theme/` app para layout
  base + Tailwind (`theme/static_src/` con el watcher), Flowbite integrado. App `core` (base:
  tenants, roles, permisos, context processors). *Verify:* `manage.py runserver` sirve una página
  base con Tailwind/Flowbite cargados.
- [ ] **Design tokens + tema**: `theme/static_src/src/styles.css` con CSS-vars (light/dark + acentos
  de vista guindo/morado) mapeadas en `tailwind.config.js`; toggle de tema (Alpine + `localStorage`).
  *Verify:* toggle light/dark cambia el tema y persiste.
- [ ] **i18n Django**: activar `USE_I18N`, `LocaleMiddleware`, catálogos `es` (base) + `en` (`.po`),
  selector de idioma. *Verify:* cambiar idioma re-renderiza textos; nada hardcodeado en lo construido.
- [ ] **Modelos base de tenancy** (`core`): `Tenant` (categoria/capa), `Role` (catálogo global +
  matriz), `Usuario` (rol + asignaciones), `RegionAgencia`. Migraciones + seed (LOGIQ, ADMIN,
  MONTERREY1 + catálogo global de roles de `PERMISSIONS.md`). *Verify:* `migrate` + seed cargan sin
  error; se ven en el admin de Django.
- [ ] **Permisos server-side** (`core/permissions.py`): helper `puede(user, recurso, op)` y
  `accion(user, nombre)` que leen la matriz del rol; decorador para vistas + tag/filtro para
  templates (`{% if puede ... %}`). *Verify:* un usuario sin `leer` en un recurso recibe 403 en su
  vista y no ve el item de menú.
- [ ] **Capa de servicios/mock** (`services.py` por app): funciones **tenant-scoped** que devuelven
  datos seed. *Verify:* una función devuelve datos filtrados por el tenant/scope activo.
- [ ] **Login**: pantalla de login (usuario/correo + password; **campo Agencia condicional** por
  conteo de tenants de capa pública); al autenticar, detecta categoría del tenant → vista por
  defecto. *Verify:* con 1 tenant público NO aparece el campo Agencia; con >1 (seed) sí.
- [ ] **Layout base + shell** (`theme/templates/`): base con **Sidebar** (off-canvas móvil vía
  Flowbite/Alpine, `md:sticky`) + **Topbar** (título + info/alertas/idioma/usuario). Navegación
  centralizada (context processor + partial de nav filtrado por permiso/vista). *Verify:* navegar
  entre hojas placeholder; sidebar colapsa en móvil.
- [ ] **ViewChips + ScopeSelector**: chips de vista (derecha del topbar, según permiso) que cambian
  sidebar/contenido y pintan el acento de vista; scope selector (izquierda, Region/Admin) con
  `<Region> (todas)` / `All` + buscador. Cambio de vista/scope vía HTMX (recarga parcial).
  *Verify:* un usuario Admin ve chips y el acento guindo en vista Admin; un solo-Agencia no ve chips;
  Region no ve chips (solo scope).
- [ ] **Footer "Powered by"**: bottom del sidebar, alimentado desde `DeveloperInfo` + versión activa.
  *Verify:* muestra logo + "Monterrey, NL" + versión.
- [ ] **Detalle de operación (partial)**: partial HTMX que abre en un **Drawer de Flowbite** desde
  una tarjeta placeholder. *Verify:* abre y cierra desde el Pipeline placeholder.

**Fase lista cuando:** login → detección de vista → navegación por todas las hojas (aunque vacías)
→ cambio de chip con acento → abrir el detalle de operación en drawer.

---

## F1 — Núcleo operativo (vista Operativa)

- [ ] **Pipeline** (`pipeline` app): tablero **kanban** por etapa (Nuevos → Calificados → Citas →
  Negociación → Cierre → Reactivación) con tarjetas; tira de KPIs arriba; sección **"Por aprobar"**
  (aprobar/rechazar propuestas de IA vía HTMX). Drag entre columnas con Alpine o botones de avanzar
  etapa (definir al construir). **Incluye una vista de "Funnel"** (embudo etapa por etapa con
  conversión entre pasos) como segunda lectura de la misma data — Funnel NO es hoja aparte.
  *Verify:* se ve el negocio de un vistazo (kanban y embudo), se aprueba/rechaza y se abre una
  operación.
- [ ] **Detalle de operación** (partial completo): sugerencia del copiloto → **scoring de dos ejes**
  (badges calificación A/B/C + BANT, temperatura + porqué) → siguiente acción → propiedades
  asociadas → actividad/trazabilidad → motivo de rechazo. *Verify:* desde una tarjeta se entiende
  todo y qué hacer con ella.
- [ ] **Leads** (`leads` app): directorio (fuente, etapa, asesor, calificación, temperatura) con
  buscar/filtrar (HTMX, preservando query params); entrar al detalle. Tabla estándar Flowbite.
  *Verify:* encontrar cualquier lead y abrirlo.
- [ ] **Scope por asignación (clientes → asesor)**: los servicios filtran por `clientes_asignados`;
  el asesor solo ve/edita **sus** clientes (a los demás ni verlos salvo `leer_clientes_de_otros`);
  líder/coordinador ve los suyos + los del equipo. UI de **asignar cliente a asesor** para roles con
  `asignar_clientes`. *Verify:* un asesor no ve clientes de otro; un líder sí ve los del equipo; se
  reasigna un cliente.

**Fase lista cuando:** se vive el día a día operativo (pipeline + detalle + leads) con el scope por
asignación funcionando.

---

## F2 — Conversaciones

- [ ] **Conversaciones** (`conversaciones` app): 3 zonas (lista de chats · hilo · perfil del lead a
  la derecha). Perfil en orden: scoring de la IA (arriba) → de dónde viene → qué busca →
  comportamiento. **Respuesta sugerida** por la IA con nivel de confianza → aprobar/ajustar y enviar
  (HTMX). *Verify:* leer una conversación, ver el perfil/scoring y aprobar una respuesta.

---

## F3 — Agentes IA (el motor)

- [ ] **Agentes IA** (`agentes` app, una hoja con **tabs de Flowbite**): Listing Manager ·
  Calificador · Love Bomber (límite diario, solo-hot, empujar a cita) · Scheduler · Reminder ·
  Inventario Easy Broker (% de match) · Integraciones (conectores + bitácora) · **Reglas** (diales
  de autonomía IA vs aprobación humana). *Verify:* cada pestaña explica qué hace su agente y se ve la
  frontera humano/IA.

---

## F4 — Analítica (con ApexCharts)

- [ ] **Ventas — Dashboard de comisiones** (`ventas` app, 4 tabs): **Cierres** (KPIs, cumplimiento de
  meta, embudo de comisiones, top asesores, tendencia por semana) · **Por cobrar** (pendiente por
  asesor + urgencia por días de separación) · **Ofrecimientos** (por asesor + tabla de detalle) ·
  **Soporte & FAQ**. Gráficas ApexCharts con colores de tokens. *Verify:* se entiende cómo va el
  dinero del mes en sus tres ángulos.
- [ ] **Team performance** (`team` app, 2 tabs): **Resumen** (KPIs del equipo, ranking por meta, el
  "por qué" de cada sugerencia) · **Por asesor** (métricas duras + habilidades blandas + foco + nota
  de 1:1). *Verify:* se ve el desempeño del equipo y de cada asesor con su foco.
- [ ] ~~Funnel performance~~ → **combinado dentro de Pipeline** (F1) como vista de embudo. No hoja
  aparte. (El widget "pipeline funnel" también aparece en el dashboard de Ventas.)

---

## F5 — Rituales + administración operativa

- [ ] **Libros** (`libros` app, 2 tabs): **Libro de comisiones** — registro maestro con **timestamp
  de cada cambio de etapa** (`EtapaEvento`), **fecha oficial de venta** y **de cobro**, cliente,
  propiedad (nombre/tipo/municipio/zona), monto de venta, comisión total y su **reparto** (asesor /
  EQ-agencia / coordinador con %/monto), contrato del asesor, tipo (venta/renta), status de cierre y
  de pago; agregar históricas. · **Objetivos** (meta del equipo y por asesor). *Verify:* registrar
  una operación, mover su etapa (queda el evento) y ver el reparto de comisión.
- [ ] **Junta semanal** (`junta_semanal` app; antes Money Monday): reporte semanal, una fila por
  consultor — asistencia, clientes hot, seguimiento de leads + a quién, reales de la semana pasada
  (ofrecimientos/separaciones/citas) vs plan de esta semana (citas), evaluación (asignar leads / OK /
  feedback coordinador) y comentarios. *Verify:* se ve la tabla semanal con reales vs plan.
- [ ] **1:1** (`uno_a_uno` app): **evaluación semanal de KPIs por asesor** vs objetivo (asistencia
  1:1, actualización status/comentarios, citas, evaluación junta, conversión citas y global), con
  semáforo, **punto a reforzar del embudo** y comentario al asesor. *Verify:* abrir el 1:1 de un
  asesor y ver sus KPIs vs objetivo y su punto a reforzar.
- [ ] **Asesores** (`asesores` app): directorio (pipeline activo, vendido, % meta) + alta de asesor
  (Drawer Flowbite). *Verify:* alta y listado de asesores.
- [ ] **Configuración** (`configuracion` app): ajustes generales. *Verify:* guardar un ajuste.

---

## F6 — Vista Region

- [ ] **Hoja "Agencias"** (region): lista de las agencias que administra la region. *Verify:* se
  listan las agencias de la region activa.
- [ ] **Columna "Agencia"** en las listas operativas cuando la vista es Region. *Verify:*
  cartera/leads muestran a qué agencia pertenece cada fila.
- [ ] **Scope dropdown Region**: `<Region> (todas)` + agencias; filtra todos los servicios/queries.
  *Verify:* elegir una agencia filtra el cockpit a esa agencia.
- [ ] **Scope por asignación (agencias → usuario)**: roles restringidos ven solo `agencias_asignadas`;
  de Administrador para arriba ven todas + UI de **asignar agencias** (`asignar_agencias`). *Verify:*
  un usuario restringido solo ve sus agencias; un Administrador reasigna agencias.

---

## F7 — Vista Admin (acento guindo)

- [ ] **Sidebar + acento Admin**: menú de control propio; banda guindo bajo el topbar. Browse "All"
  + buscador; **columna "Region"** en listas cuando existan regions. *Verify:* entrar a Admin cambia
  sidebar y pinta el acento; se busca/filtra por region/agencia.
- [ ] **Licencia de login** (admin). *Verify:* ver/editar estado de licencia.
- [ ] **Tokens de IA** (admin): saldo comprado/consumido por agencia. *Verify:* ver saldo por agencia.
- [ ] **Roles + matriz de permisos** (admin): gestión del **catálogo GLOBAL** de roles, cada rol con
  editor de matriz recurso × **Crear/Leer/Editar** (sin borrar) + permisos de acción. *Verify:*
  crear/editar un rol y que un usuario con ese rol vea/oculte hojas según "leer" y respete el CRUD.
- [ ] **Usuarios** (admin): crear, **asignar rol** (global) y agencia. *Verify:* alta + asignación;
  la vista del usuario refleja su matriz y su scope.
- [ ] **Brand** (admin): logo, favicon, fotos del login (carrusel, logo, textos). *Verify:* editar el
  brand de una agencia.
- [ ] **Agencias** (admin): **promover una agencia a "Region"** (dropdown + checkboxes de qué
  agencias administra). *Verify:* una agencia promovida aparece como region con sus agencias.

---

## F8 — Vista Developer (LOGIQ, acento morado vibrante)

- [ ] **Sidebar + acento Developer** (morado); invisible al Admin (solo el usuario developer ve el
  chip). *Verify:* el chip Developer solo aparece para el usuario developer.
- [ ] **SYSTEM → Version control**: tabla versión / fecha / dueño / comentario / timestamp; marcar
  versión activa. *Verify:* la versión activa se refleja en el footer "Powered by".
- [ ] **SYSTEM → System settings → Developer info**: logo, empresa, nombre, origen. *Verify:* editar
  la Developer info actualiza el footer en todas las vistas.

---

## Notas de ejecución

- **Vistas delgadas**: parsing/permiso/respuesta en la view; reglas de dominio en modelos/servicios
  (`services.py`). Sin lógica de negocio en templates.
- **Hojas nuevas**: registrar en la nav centralizada con su **`recurso` (`RecursoKey`)**; el gate de
  visibilidad sale de `puede(user, recurso, 'leer')` (además del filtro por vista/chip). Ver
  `PERMISSIONS.md` §3.
- **HTMX** para parciales (filtros, drawers, tabs, refresh de tablas); devolver templates parciales
  enfocados, preservando query params.
- **Flowbite** para drawers/modales/tabs/tablas/badges; al hacer swaps HTMX que traen componentes
  Flowbite, reinicializarlos (ver `UI_RULES.md`).
- Todo texto traducible; cero hex (usar tokens); tablas con el patrón estándar de `UI_RULES.md`.
- **Migraciones** nativas de Django; una por cambio de modelo. Ruff-clean antes de cerrar.
- Al resolver un bug no trivial del stack, agregar cicatriz técnica a `UI_RULES.md` (Parte B).
