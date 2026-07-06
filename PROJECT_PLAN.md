# PROJECT_PLAN.md — Espacio Querido

Plan del proyecto: **producto** (qué pantallas, en qué orden) + **arquitectura técnica** (con qué
se construye y cómo escala). Para el modelo mental del producto (cómo se piensa la app, vocabulario
y reglas de tono), ver `CLAUDE.md`. La ley de diseño vive en `UI_RULES.md`; las reglas de acceso en
`PERMISSIONS.md`; el backlog ejecutable en `BUILD_PLAN.md`.

> **Este documento es el estado vivo del proyecto.** Al completar algo grande, actualiza §9.

---

## 1. Objetivo

Que el equipo de una correduría inmobiliaria lleve toda la operación —del lead al cierre y al
cobro— en un solo lugar, con agentes de IA haciendo el trabajo repetitivo y el humano aprobando lo
importante. El producto se ofrece como **plataforma multi-tenant**: el mismo cockpit se vende a
varias agencias, administradas por capas (Region / Admin / Developer).

## 2. Stack y arquitectura

**Stack: Django + HTMX + Alpine.js + Tailwind + Flowbite** (server-rendered). Es la plantilla base
del folder (`CLAUDE.md` raíz) y la misma familia de convenciones. **No SPA** (sin React/Vue/Vite).

- **Backend / render**: Django (vistas delgadas + templates server-rendered). Interacciones parciales
  con **HTMX**; estado de interacción ligero con **Alpine.js**.
- **UI**: Tailwind CSS + **Flowbite** (drawers, modales, popovers, dropdowns, tabs, tablas, badges,
  tooltips). Design tokens vía CSS variables + Tailwind. Iconos outline (Flowbite/heroicons-style),
  **sin emojis**.
- **Gráficas**: **ApexCharts** (charts nativos de Flowbite) para la Analítica; colores desde los
  design tokens del tema. *(No Recharts — eso es React.)*
- **i18n**: framework de traducción de **Django** (`{% trans %}` / `gettext`, catálogos `.po`) —
  **Español base + Inglés**. Todo texto de UI traducible (regla dura en `UI_RULES.md`).
- **Datos (fase actual)**: para ver pantallas rápido sin congelar el modelo, cada app arranca con
  una **capa de servicios/mock en Python** (`services.py` devolviendo datos seed) y **se formalizan
  modelos Django + SQLite** conforme cada pantalla estabiliza su data. **Multi-tenant desde el día
  1**: todo queryset/servicio filtra por tenant/scope. Permisos **server-side** siempre.
- **DB**: SQLite en dev; PostgreSQL en prod (Railway) a futuro. Cuidar tipos/migraciones que difieren
  entre motores.

**Ruta a producción** (cuando el modelo esté confirmado): reemplazar los servicios mock por modelos
Django + querysets `for_user(user)` tenant-scoped; los templates, HTMX y la capa de vistas quedan
intactos. Deploy en Railway con Docker (patrón de `01 LogiQ Management`), más adelante.

## 3. Modelo de tenants (núcleo de la arquitectura)

**4 categorías de tenant**, en 2 capas. Al entrar, la app detecta la categoría del tenant del
usuario y le asigna su vista por defecto.

| Categoría | Instancia hoy | Capa | Vista por defecto |
|---|---|---|---|
| `Developer` (LOGIQ) | LOGIQ | plataforma (invisible al Admin) | Admin, con chip Developer |
| `Admin` | ADMIN | plataforma | Admin (browse "All") |
| `Region` | — (ninguna aún) | pública | Region |
| `Agencia` / `Client` | MONTERREY1 | pública | Operativa |

Reglas del modelo:
- El **dato de dominio** (leads, operaciones, conversaciones, comisiones, asesores) pertenece a un
  tenant `Agencia`. Un `Region` administra el agregado de sus agencias asignadas (relación
  Region ↔ Agencia, muchos-a-muchos). `Admin`/`Developer` operan sobre toda la plataforma.
- **Capa pública** = `Region` + `Agencia` (workspaces operativos, elegibles en el login).
  **Capa plataforma** = `Developer` + `Admin` (interna).
- El **Developer** es el top tenant: el Admin no sabe que existe, no lo ve ni ve a sus usuarios.

## 4. Sistema de VISTAS (chips + scope)

**Chips de VIEW** en el top bar (derecha, junto a info / alertas / idioma / usuario): indican en qué
vista estás y permiten cambiar **según el permiso del usuario** — `Agencia · Region · Admin ·
Developer`.
- Un usuario **solo-Agencia** no ve chips (solo existe su vista operativa).
- `Region` entra automático en vista Region; `Admin` en vista Admin; `Developer/LOGIQ` entra en
  vista Admin con el chip Developer disponible.
- Cambiar de chip cambia el sidebar + el contenido y pinta un **acento identificador bajo el top
  bar**: **Admin = guindo / rojo oscuro**, **Developer = morado vibrante**.

**Dropdown de scope** (top bar, lado izquierdo — solo Region / Admin / Developer): elige **de quién**
son los datos que se ven.
- **Region**: primer opción siempre `<Nombre de la region> (todas)`, luego cada agencia que administra.
- **Admin**: primer opción `All`; de ahí selecciona regions o agencias, **con buscador**.

### Vista Operativa (Agencia)
Ve el cockpit (las 13 hojas). Qué pantallas y qué CRUD según su **nivel de usuario dentro del
tenant** → `PERMISSIONS.md`.

### Vista Region
Igual a la operativa **+** una hoja **"Agencias"** (lista de las agencias que administra). En las
listas de datos aparece una **primera columna "Agencia"**. Usa el dropdown de scope. **No muestra
chips** (solo el scope dropdown).

### Vista Admin (acento guindo)
"Global Regions" con permisos especiales. Browse global (`All` + buscador); ve todo como Region
**+** columna **"Region"** en las listas (solo cuando existan regions). Sidebar de control:
- **Licencia de login** · **Tokens de IA** (saldo comprado por agencia) · **Permisos por agencia**
  (+ crear) · **Usuarios** (+ crear y asignar) · **Brand** (logo, favicon, fotos del login:
  carrusel, logo y textos) · **Agencias** (promover una agencia a "Region": dropdown + checkboxes
  de qué agencias administra).

### Vista Developer (LOGIQ, acento morado vibrante)
Todo lo de Admin **+** una sección **"SYSTEM"**:
- **Version control** — tabla: versión, fecha, dueño, comentario, timestamp.
- **System settings → Developer info** — logo, empresa, nombre y origen del developer.

La **Developer info alimenta el footer del sidebar** en TODAS las vistas:
```
Powered by (logo del developer)
Monterrey, NL
version 1.2.0   ← última versión activa (de Version control)
```

## 5. Login

- Al entrar: detectar categoría del tenant → asignar vista por defecto (§3).
- **Campo Agencia condicional** por conteo de tenants de **capa pública** (flag runtime estilo
  `multitenant_enabled`):
  - **1** tenant público (hoy: MONTERREY1) → login pide **Usuario/correo + Password** (sin Agencia).
  - **>1** → aparece el campo **Agencia**.
- La capa **Developer** se reconoce por el **usuario developer**.
- Detalle fino (validaciones, recuperación, etc.) → `PERMISSIONS.md`.

## 6. Dos significados de "tokens" (no confundir)

- **Design tokens** — variables CSS del tema (`--bg-card`, `--accent`, …). Concepto de UI. Regla:
  cero hex hardcodeado. Ver `UI_RULES.md`.
- **Tokens de IA** — saldo **comprado** para el uso de los agentes de IA de cada agencia. Concepto
  de negocio que administra la vista Admin. Ver §7 y `PERMISSIONS.md`.

## 7. Boceto de modelo de datos (entidades, no migración final)

Guía para los modelos Django (empiezan como datos mock en `services.py` y se formalizan por app). No
es contrato final; se afina al construir cada hoja. Todas las entidades de dominio cuelgan de una
**Agencia** (tenant) y se filtran por scope.

- **Tenant**: `nombre`, `categoria` (`developer`/`admin`/`region`/`agencia`), `capa`
  (`plataforma`/`publica`).
- **RegionAgencia**: M2M — qué agencias administra una region.
- **Usuario**: FK `tenant`, `nombre`, `correo`, FK `role` (global), M2M `clientes_asignados`, M2M
  `agencias_asignadas`. Ver `PERMISSIONS.md`.
- **Role** (catálogo **global**, definido por Admin): `nombre` + matriz `permisos` por
  `RecursoKey` (`crear`/`leer`/`editar` — **sin borrar** a nivel agencia) + `acciones`
  (`leer_clientes_de_otros`, `ver_resultados_equipo`, `asignar_clientes`, `asignar_agencias`).
- **RecursoKey** (constante en código, no dato): `leads` (internos), `pipeline` (incluye funnel),
  `muro` (comentarios internos), `libros`, `conversaciones` (externo), `leads_inmuebles` (externo),
  `integraciones`, `ventas`, `team_performance`, `agentes`, `junta_semanal`, `uno_a_uno`, `asesores`,
  `configuracion`, `agencias`.
- **Leads internos vs externos**: `leads` = directorio de clientes ya dentro del CRM (Operación).
  `leads_inmuebles` = leads externos del portal Inmuebles24 que se **extraen e importan** (Lead
  management). Conversaciones y Muro son distintos: **Muro de comentarios** = notas INTERNAS del
  equipo; **Conversaciones** = chat EXTERNO con leads.
- **API Keys** (dentro de Agentes IA) y config sensible: **gated a Administrador+** del tenant.
- **Lead / Operación**: FK `agencia`, `fuente`, `etapa`, FK `asesor`, `calificacion`, `temperatura`.
- **Etapa**: `nuevos`/`calificados`/`citas`/`negociacion`/`cierre`/`reactivacion`.
- **Calificacion (fit)**: `grado` (A/B/C), `score` (0–100), `bant` (presupuesto, financiamiento,
  necesidad, horizonte).
- **Temperatura**: `caliente`/`tibio`/`frio`.
- **Conversacion / Mensaje**: hilo por lead + respuesta sugerida (`texto`, `confianza`).
- **Propiedad**: inventario con `match_pct` contra lo que busca el lead.
- **Asesor**: FK `agencia`, `nombre`, `pipeline_activo`, `vendido`, `pct_meta`, `contrato_modelo`.
- **Operacion / Comision** (registro maestro del Libro de comisiones): FK `agencia`, FK `asesor`,
  FK `lead`, FK `propiedad`; `tipo` (venta/renta), `status_cierre`, `status_pago`
  (facturado/por_cobrar/ofrecimiento/separacion), `monto_venta`/`facturacion`, `pct_comision`,
  `comision_total`, `portafolio`; **reparto**: `pct_asesor`+`comision_asesor`, `pct_eq`+`comision_eq`,
  `comision_coordinador`; **fechas oficiales**: `fecha_venta`, `fecha_separacion`, `fecha_cobro`.
- **EtapaEvento** (auditoría): `operacion`, `etapa`, `timestamp` — se registra **cada** transición
  de etapa (el Libro conserva las fechas oficiales derivadas de estos eventos).
- **Propiedad**: `nombre`, `tipo` (departamento/casa/oficina/terreno), `municipio`, `zona`,
  `colonia`, `match_pct`.
- **JuntaSemanal** (fila por consultor/semana): `consultor`, `semana`, `asistencia`,
  `clientes_hot`, `seguimiento_leads`, reales `{ofrecimientos, separaciones, citas}`, plan
  `{citas}`, `evaluacion` (asignar_leads/ok/feedback_coordinador), `comentarios`.
- **EvaluacionUnoAUno** (KPIs por asesor/semana vs objetivo): `asesor`, `periodo`, y por métrica
  (asistencia_1a1, actualizacion_status, actualizacion_comentarios, citas, evaluacion_junta,
  conversion_citas, conversion_global) su `valor`/`objetivo`/`nivel`; más `punto_a_reforzar` y
  `comentario`.
- **Agente**: pieza de IA (`tipo`, `autonomia`) — diales en la hoja Reglas.
- **SaldoTokensIA**: FK `agencia`, `comprados`, `consumidos`.
- **Brand**: FK `tenant`, `logo`, `favicon`, `login_fotos`, `login_textos`.
- **VersionControl**: `version`, `fecha`, `dueño`, `comentario`, `timestamp`, `activa`.
- **DeveloperInfo**: `logo`, `empresa`, `nombre`, `origen`.

---

## 8. Orden de construcción (fases)

El detalle ejecutable (tareas + criterio "listo cuando…") vive en `BUILD_PLAN.md`. Resumen:

1. **Fase 0** — Esqueleto + tenancy: proyecto Django, layout base + navegación, sistema de vistas
   (chips/scope), login condicional, detalle de operación transversal (partial HTMX), capa de
   servicios/mock, footer "Powered by".
2. **Fase 1** — Núcleo operativo: Pipeline (kanban), Detalle de operación, Leads.
3. **Fase 2** — Conversaciones.
4. **Fase 3** — Agentes IA (motor).
5. **Fase 4** — Analítica (Ventas, Team performance, Funnel).
6. **Fase 5** — Rituales + admin operativa (Libros, Money Monday, 1:1, Asesores, Configuración).
7. **Fase 6** — Vista Region.
8. **Fase 7** — Vista Admin.
9. **Fase 8** — Vista Developer.

### Orden de las hojas del cockpit (vista Operativa)
1. **Operación**: **Leads** *(internos, landing)* · Pipeline *(kanban + vista funnel)* · **Muro de
   comentarios** *(interno)* · Libros
2. **Lead management** *(externo)*: Conversaciones · Leads Inmuebles24 · Integraciones
3. **Analítica**: Ventas *(dashboards: tabs + filtros)* · Team performance   *(Funnel dentro de Pipeline)*
4. **Automatizaciones + IA**: Agentes IA *(pestañas por agente + API Keys gated)*
5. **Sistema operativo**: Junta semanal *(antes Money Monday)* · 1:1
6. **Administración**: Asesores · Configuración

---

## 9. Estado vivo del proyecto

**Fase actual: planeación técnica cerrada.** Documentos de arranque escritos y **alineados al stack
Django/HTMX/Alpine/Flowbite** (`PROJECT_PLAN`, `BUILD_PLAN`, `UI_RULES`, `PERMISSIONS`). Aún no hay
código.

**Siguiente:** arrancar `BUILD_PLAN.md` → **F0** (proyecto Django + tenancy).

---

## 10. Decisiones por confirmar (afectan hojas/funciones)

Del producto (heredadas de la spec original):
- **1:1**: ¿hoja propia o se integra en Team performance?
- **Objetivos**: ¿metas por trimestre / etapa / fuente, además de por asesor?
- **Calificación**: confirmar criterios reales de BANT con el dueño de la correduría.
- **Agentes**: unificar vocabulario (agentes por etapa del pipeline vs agentes operativos).

De la arquitectura / acceso (detalle en `PERMISSIONS.md`):
- Matriz de roles: **propuesta ya cargada** en `PERMISSIONS.md` §3 — falta validar descripciones y
  celdas con el dueño.
- Alcance del **Borrado** (por ahora inexistente a nivel agencia) — se irá definiendo.
- Reglas exactas de **login** (validaciones, recuperación de contraseña).

## 11. Criterio de "terminado" del producto (v1)

Se puede: ver el pipeline y aprobar lo de la IA, abrir cualquier operación y entender qué sigue,
conversar con el lead aprobando respuestas, leer cómo va el dinero (Ventas) y el equipo (Team
performance), ajustar hasta dónde actúa la IA (Reglas), y —en las capas superiores— administrar
agencias, regions, licencias, tokens de IA, usuarios y brand desde las vistas Admin/Developer.
