# UI_RULES.md — Espacio Querido

Ley de diseño y convenciones técnicas del frontend. **Es ley, no sugerencia.** Stack **Django +
HTMX + Alpine.js + Tailwind + Flowbite** (server-rendered), alineado con la plantilla base del folder
(`CLAUDE.md` raíz). Léela antes de tocar cualquier UI.

- **Parte A** — reglas de diseño e implementación (siempre activas).
- **Parte B** — cicatrices técnicas: bugs resueltos y trampas del stack. Consúltala ante síntomas
  raros (tablas con `thead sticky`, swaps HTMX con componentes Flowbite, popovers/tooltips en
  tablas, templates de PDF/print) y **agrega una entrada** cuando resuelvas un bug no trivial
  (plantilla al final).

---

# PARTE A — Reglas

## 1. Stack y progressive enhancement

- **Server-rendered primero**: las páginas funcionan con respuestas Django; luego mejoran con HTMX
  (parciales) y Alpine (estado de interacción ligero). **No** introducir React/Vue/Vite ni SPA.
- **HTMX** para updates parciales: filtros, drawers, contenido de modales, refresh de tablas, tabs,
  flujos de formulario incrementales. Devolver **templates parciales enfocados**, no re-renderizar
  la página. Preservar query params (filtros, sort, paginación, scope).
- **Alpine** solo para estado client-side pequeño (abrir/cerrar, toggles, tabs locales).

## 2. Flowbite es el kit por defecto

- Usa **Flowbite** para drawers, modales, popovers, dropdowns, tabs, tablas, badges y tooltips. No
  construyas reemplazos custom salvo que el componente no exista en Flowbite.
- Nada de hacks one-off, JS inline aleatorio ni manipulación manual del DOM cuando Flowbite ya da el
  patrón.
- **Reinicialización tras swaps HTMX**: cuando HTMX reemplaza DOM que contiene componentes Flowbite
  (drawers, dropdowns, tooltips), re-inicialízalos de forma controlada (ver Parte B). No asumas que
  siguen "vivos" tras el swap.

## 3. Design tokens y tema (cero hex hardcodeado)

- Colores como **CSS variables** en `theme/static_src/src/styles.css`, referenciados vía Tailwind
  (`bg-card`, `text-text-primary`, `border-border`, `bg-accent`, …). **Nunca** un hex en un template.
- Tema light/dark por clase en `<html>` (Alpine + `localStorage`).
- Tokens semánticos: `page`, `card`, `elevated`, `table-header`, `border`, `accent`, `text-primary`,
  `info`, `warning`, `danger`.
- **"tokens" aquí = design tokens (CSS).** No confundir con los **tokens de IA** (saldo de negocio de
  la vista Admin). Ver `PROJECT_PLAN.md` §6.

## 4. Acentos de vista (multi-tenant)

- Cada vista superior pinta un **acento identificador** como banda bajo el topbar: **Admin = guindo /
  rojo oscuro**, **Developer = morado vibrante**. Operativa/Region usan el accent normal.
- El acento es un **token** (`--accent-view`) que aplica el layout según la vista activa. No
  hardcodear guindo/morado en las páginas.

## 5. Iconografía

- Iconos **outline** (set de Flowbite / heroicons-style), tamaño consistente. **Nunca emojis** en UI
  (inconsistentes en Windows). Banderas de idioma como **SVG inline** (los emoji de bandera no
  renderizan en Windows).

## 6. Layout y shell

- **Layout base único** (`theme/templates/`): `Sidebar` + `Topbar` + `<main>` con gutter parejo. El
  Sidebar **adapta su contenido** según la vista activa (Operativa / Region / Admin / Developer).
- **Topbar (derecha)**: info · alertas · idioma · usuario · **ViewChips** (según permiso).
- **Topbar (izquierda)**: **ScopeSelector** (solo Region/Admin/Developer) — `<Region> (todas)` o
  `All` + buscador.
- **Sidebar** off-canvas en móvil (drawer Flowbite/Alpine, abre con hamburguesa + backdrop),
  `md:sticky` en desktop. Cierra al navegar.
- **Footer del sidebar** ("Powered by" + versión activa) sale de `DeveloperInfo` + Version control,
  no hardcodeado.
- Páginas usan todo el ancho (sin `max-w` que deje hueco). Tablas y tabs con `overflow-x-auto`.
- Reutiliza el layout base y los partials compartidos (prefijo `_`). No dupliques markup estructural.

## 7. Patrón de página estándar (lista)

Header de página (`h2` + `p`) → barra de acciones (contador + botón "+ Nuevo") → tabla estándar
Flowbite → `Drawer` de formulario. Estados claros de **empty / loading / error**. Skeleton o
placeholder mientras carga (no dejar la tabla vacía sin señal).

## 8. Tabla estándar

- Marco `rounded-xl border border-border overflow-hidden` con `overflow-x-auto` adentro.
- Header con banda `bg-table-header` + `border-b`, sin iconos. Filas `hover:bg-elevated`.
- **Multi-tenant**: en vista Region, primera columna **"Agencia"**; en vista Admin, columna
  **"Region"** (solo cuando existan regions).
- Antes de `thead sticky` o popovers/tooltips dentro de tablas, revisa **Parte B**.

## 9. Feedback de UI (usar el patrón correcto)

- **Toasts** — confirmaciones efímeras (éxito de submit/soft-action/transición). Disparar desde el
  server vía `HX-Trigger`. Abajo-derecha, auto-dismiss 4–7s. Todo submit exitoso dispara toast
  (silencio tras un click = bug de UX).
- **Modales** — input enfocado o lectura importante.
- **Drawers** — panel de edición contextual (editar entidad, ver detalle lateral). Lado derecho. El
  **detalle de operación** es el drawer canónico del producto (partial HTMX).
- **`hx-confirm`** — sí/no rápido antes de acción sensible.
- **Errores inline de form** — por campo, texto rojo debajo del campo, renderizados server-side desde
  los errores del form. NO toasts.

## 10. i18n (regla dura)

- **Todo** texto de UI es traducible: `{% trans %}` / `{% blocktrans %}` en templates, `gettext` en
  Python. Catálogos `es` (base) + `en` (`.po`). Nunca hardcodear texto suelto.
- Selector de idioma tipo dropdown (bandera SVG + nombre), no un botón que cicla.

## 11. Datos y multi-tenant (server-side)

- **Fase actual**: datos desde `services.py` (mock seed) por app; se formalizan modelos Django +
  SQLite por pantalla. **Todo servicio/queryset es tenant-scoped** (`for_user(user)` / filtro por
  scope activo). La UI nunca asume "un solo tenant".
- **Sin lógica de negocio en templates.** Math, totales y transiciones de estado en modelos/servicios,
  en un solo lugar reutilizable.
- **Permisos server-side siempre**: ocultar un botón/hoja **no** es control de acceso (ver §13).

## 12. Dinero, gráficas y componentes de dominio

- **Una sola función/utilidad de dinero** (formato consistente). No inventes varias.
- **Gráficas**: **ApexCharts** (charts nativos de Flowbite); colores desde los design tokens del
  tema. Nada de paletas ad hoc. (No Recharts — eso es React.)
- **Componentes/partials de dominio reutilizables**:
  - Badges de **scoring**: calificación A/B/C (+ 0–100, BANT) y temperatura caliente/tibio/frío.
  - **Detalle de operación**: partial transversal único (drawer), se incluye desde Pipeline/Leads/
    Conversaciones — no se duplica.
  - **Tarjeta kanban** de operación en el Pipeline.

## 13. Permisos en UI (nunca suficientes por sí solos)

- Ocultar una hoja/botón **no** es control de acceso. La visibilidad se deriva de la **matriz del
  rol** (`puede(user, recurso, 'leer')`) en la nav; el alcance de datos lo dan además las
  **asignaciones** (clientes/agencias). La regla real se valida en la **view** (decorador de
  permiso) y en los **servicios/querysets**.
- Roles = **catálogo global** (definido por Admin, mismos nombres/permisos en todas las agencias);
  recursos = **código**. **Sin Borrar a nivel agencia** (solo Crear/Leer/Editar). El código decide
  por **permiso atómico** (recurso × op) y scope, **nunca por nombre de rol**. Ver `PERMISSIONS.md`.

---

# PARTE B — Cicatrices técnicas

> Índice de síntomas → entrada. Escanéalo antes de trabajar en tablas con `thead sticky`, swaps HTMX
> que traen componentes Flowbite, popovers/tooltips en tablas, o templates de PDF/print. Agrega una
> entrada (plantilla abajo) al resolver un bug no trivial del stack.

*(Sin entradas todavía — el proyecto arranca en F0. Documenta la primera trampa que encuentres. Las
más probables en este stack: reinicialización de Flowbite tras swaps HTMX, filas de tabla
clickeables vs forms/HTMX, y `thead sticky` dentro de contenedores con `overflow`.)*

### Plantilla para nuevas entradas

```
## §N. <Título corto del síntoma>

**Síntoma:** <qué se ve / qué falla>
**Causa:** <por qué pasa (la trampa real del stack)>
**Solución:** <el patrón correcto, con archivo/línea de referencia>
**Aplica a:** <cuándo revisar esto en el futuro>
```
