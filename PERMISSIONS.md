# PERMISSIONS.md — Espacio Querido

**Fuente única de reglas de acceso.** Ningún otro documento ni comentario de código duplica reglas
de permisos: si una regla de acceso no está aquí, no existe. La UI puede ocultar cosas, pero el
control real se valida **server-side** en Django (decorador de permiso en la view + querysets/
servicios `for_user`). Ocultar un botón nunca basta.

> Marcas: **[DEFINIDO]** = regla acordada. **[POR CONFIRMAR]** = pendiente de aterrizar con el
> dueño; no inventar en silencio, preguntar.

---

## 1. Dos dimensiones de acceso

El acceso se decide por **dos ejes independientes**:

1. **Categoría del tenant** → qué **vistas** puede ver el usuario (Operativa / Region / Admin /
   Developer) y qué **scope** de datos alcanza.
2. **Nivel del usuario dentro de su tenant** → qué **pantallas** y qué **CRUD** puede hacer dentro
   de la vista que le toca.

---

## 2. Categorías de tenant → vistas y chips  **[DEFINIDO]**

Al entrar, la app detecta la categoría del tenant del usuario y le asigna su vista por defecto. Los
**chips** en el top bar (derecha) permiten cambiar de vista solo si el usuario tiene permiso.

| Categoría | Capa | Vista por defecto | Chips visibles | Scope de datos |
|---|---|---|---|---|
| `Agencia` (Client) | pública | Operativa | ninguno | solo su agencia |
| `Region` | pública | Region | ninguno (solo scope dropdown) | sus agencias (`<Region> (todas)` + cada agencia) |
| `Admin` | plataforma | Admin | Admin (+ browse operativo "All") | toda la plataforma (`All` + buscador) |
| `Developer` (LOGIQ) | plataforma | Admin | Admin · Developer | toda la plataforma; el Developer es invisible al Admin |

Reglas duras:
- **Un usuario solo-Agencia no ve chips.** Solo existe su vista operativa.
- **El Developer es el top tenant:** el Admin no sabe que existe, no lo ve ni ve a sus usuarios.
- **Login condicional:** el campo **Agencia** aparece solo cuando hay **>1 tenant de capa pública**.
  Con 1 (hoy: MONTERREY1) el login pide solo usuario/correo + password. La capa Developer se
  reconoce por el usuario developer.

---

## 3. Roles globales + matriz de permisos (RBAC)  **[DEFINIDO]**

El acceso a pantallas y datos se decide por **rol**. Los roles son un **catálogo GLOBAL**: el Admin
define los nombres y sus permisos **una sola vez**, y **todas las agencias (y regions) usan los
mismos nombres con los mismos permisos**. Los roles **no** son por-agencia.

**Mecánica:**
- **El Admin define el catálogo global de roles** (nombres de puesto + su matriz de permisos).
  Aplica idéntico a todos los tenants públicos.
- Cada rol tiene una **matriz de permisos**: por cada **recurso (hoja)**, qué operaciones concede.
  Las operaciones son **Crear / Leer / Editar** — **Borrar NO existe a nivel agencia** (ver abajo).
- **La visibilidad de una hoja se deriva de la matriz:** un usuario ve una hoja si su rol tiene al
  menos **Leer** en ese recurso. La nav (context processor + partial) filtra los items con
  `puede(user, recurso, 'leer')`; la view valida el mismo permiso server-side.
- Cada usuario tiene **un rol** (del catálogo global) + pertenece a un tenant + tiene un **scope de
  datos asignado** (qué clientes o qué agencias ve — ver "Asignaciones").
- **Los recursos (hojas) están definidos en código** (estables); **los roles y sus permisos son
  datos** (definidos por Admin). El código nunca decide acceso por nombre de rol — decide por lo que
  la matriz concede sobre un recurso, más el scope asignado.

### Regla de Borrado  **[DEFINIDO]**

- A nivel **agencia** nadie borra: las operaciones máximas son **Crear / Leer / Editar**. Solo se
  edita, no se elimina.
- **[POR CONFIRMAR]** si el **Borrado** existe en algún nivel superior (Admin/plataforma) y para qué
  entidades. Por ahora, ninguna vista operativa expone "eliminar".

### Recursos (filas de la matriz) — vista Operativa

`pipeline` · `leads` · `conversaciones` · `libros` · `ventas` · `team_performance` · `funnel` ·
`agentes` · `money_monday` · `uno_a_uno` · `asesores` · `configuracion`.
*(Vista Region agrega el recurso `agencias`.)*

### Matriz propuesta (recurso × rol)  **[PROPUESTA — ajustable]**

Operaciones: `✕` sin acceso · `L` leer · `CLE` crear/leer/editar (nunca borrar). El **scope**
(propios / equipo / agencia) lo dan las asignaciones, no la matriz.

Headers: **Jr**=Asesor junior · **Esp**=especialista · **Pro**=pro · **Exp**=experto ·
**Líd**=Líder de equipos · **Adm**=Administrador · **Ger**=Gerentes · **Dir**=Director.

| Recurso (hoja) | Jr | Esp | Pro | Exp | Líd | Adm | Ger | Dir |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| pipeline | CLE | CLE | CLE | CLE | CLE | CLE | CLE | CLE |
| leads | CLE | CLE | CLE | CLE | CLE | CLE | CLE | CLE |
| conversaciones | CLE | CLE | CLE | CLE | CLE | CLE | CLE | CLE |
| libros | L | L | L | L | CLE | CLE | CLE | CLE |
| ventas | L | L | L | L | L | L | L | L |
| team_performance | ✕ | ✕ | L | L | CLE | CLE | CLE | CLE |
| funnel | ✕ | L | L | L | L | L | L | L |
| agentes | L | L | L | L | L | CLE | CLE | CLE |
| money_monday | L | L | L | L | CLE | CLE | CLE | CLE |
| uno_a_uno | L | L | L | L | CLE | CLE | CLE | CLE |
| asesores | ✕ | ✕ | ✕ | ✕ | L | CLE | CLE | CLE |
| configuracion | ✕ | ✕ | ✕ | ✕ | ✕ | CLE | CLE | CLE |
| agencias *(region)* | ✕ | ✕ | ✕ | ✕ | ✕ | L | L | L |

**Permisos de acción** (interacción *dentro* de las hojas; también por rol):

| Acción | Jr | Esp | Pro | Exp | Líd | Adm | Ger | Dir |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| `leer_clientes_de_otros` — leer (no editar) clientes ajenos | ✕ | ✕ | ✕ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `ver_resultados_equipo` — analítica del equipo a cargo | ✕ | ✕ | ✕ | ✕ | ✓ | ✓ | ✓ | ✓ |
| `asignar_clientes` — asignar clientes a asesores | ✕ | ✕ | ✕ | ✕ | ✓ | ✓ | ✓ | ✓ |
| `asignar_agencias` — asignar agencias a usuarios (region) | ✕ | ✕ | ✕ | ✕ | ✕ | ✓ | ✓ | ✓ |

> Nota: los 4 tiers de **Asesor** comparten casi toda la matriz; su diferencia real es de
> **seniority/límites** (calidad y volumen de leads asignados, presupuesto de tokens de IA,
> autonomía) más un ligero escalón de visibilidad analítica (funnel → team_performance) y, en el
> tier **experto**, la lectura de clientes ajenos. **Adm / Ger / Dir** comparten matriz de pantalla
> (control casi total, sin borrar); se diferencian por **scope** (una agencia → varias agencias →
> todo) y jerarquía. Todo esto es punto de partida — el Admin lo ajusta desde la hoja de Roles.

### Asignaciones (scope a nivel de fila)

El scope de datos no lo da solo la matriz, sino **a quién tiene asignado** cada usuario. Patrón que
se repite hacia arriba:

- **En agencia:** los **clientes se asignan a asesores**.
  - **Asesor**: **Crear/Editar** la info de **sus** clientes; a los demás **ni ver ni leer**, salvo
    que su rol tenga `leer_clientes_de_otros` (entonces solo lectura).
  - **Líder / coordinador (y arriba)**: **Crear/Editar** sobre **sus** clientes **y los de su
    equipo**, y **ver los resultados** del equipo (`ver_resultados_equipo`).
- **En region:** las **agencias se asignan a usuarios** (igual que se asignan clientes a asesores).
  - Roles restringidos: solo ven **sus agencias asignadas**.
  - **Administrador para arriba** (Administrador, Gerentes, Director): ven **todas** las agencias de
    la region y pueden **asignar agencias** (`asignar_agencias`).

### Catálogo global de roles (definido por Admin)  **[PROPUESTA — ajustable]**

Mismos nombres y permisos en todas las agencias. Descripciones propuestas (a validar con el dueño):

| Nombre de rol | Descripción y scope |
|---|---|
| **Asesor junior** | Ejecutivo en formación. Opera su propio pipeline (leads, conversaciones) sobre **sus** clientes asignados; ve sus números y su 1:1/Money Monday. Sin funnel ni analítica de equipo. **No ve clientes de otros.** |
| **Asesor especialista** | Asesor de experiencia media. Igual que junior **+ ve el funnel** del negocio. Mayor volumen/calidad de leads asignados. |
| **Asesor pro** | Asesor consolidado. **+ ve team_performance** (contexto de equipo, lectura). Mayor autonomía y presupuesto de tokens de IA. |
| **Asesor experto** | Asesor senior / mentor. **+ puede leer (no editar) clientes de otros** asesores para cobertura y mentoría. Máxima autonomía operativa. No administra equipo. |
| **Líder de equipos** | Conduce un equipo. CRUD (sin borrar) sobre **sus** clientes **y los de su equipo**; ve resultados del equipo; conduce Money Monday y 1:1; **asigna clientes** a sus asesores. Scope = su equipo. |
| **Administrador** | Administra una agencia. Control casi total (sin borrar) de la operación + configuración + roster de asesores + ajuste de agentes de IA. En region: ve las agencias asignadas y **asigna agencias**. Scope = su agencia (o agencias asignadas). |
| **Gerentes** | Supervisa **varias** agencias/equipos. Mismas pantallas que Administrador, con scope más amplio y visión consolidada. Asigna agencias. |
| **Director** | Máxima autoridad. Control total y **scope completo** (toda la region/capa pública que le corresponde). Asigna agencias y define estructura. |

*(La matriz de pantalla de cada rol está en la tabla de arriba. "Descripción" y matriz son propuesta
inicial; el Admin las edita desde la hoja de Roles.)*

### Gestión del catálogo — vive en la vista Admin

El Admin puede: **crear** un rol (nombre + matriz), **leer/listar** el catálogo global, **editar**
la matriz de un rol, y **asignar** el rol a usuarios. (Borrar un rol: sujeto a la regla de borrado /
validación de usuarios asignados — **[POR CONFIRMAR]**.) Ver §5.

---

## 4. Vista Region  **[DEFINIDO]**

- Usa el **mismo catálogo global de roles** que las agencias; el CRUD del rol aplica **por cada
  agencia** que el usuario tiene asignada.
- Ve la vista operativa de sus agencias, con una **columna "Agencia"** en las listas.
- Hoja adicional **"Agencias"**: lista las agencias que administra.
- **Scope**: dropdown con `<Region> (todas)` (agregado) + cada agencia individual.
- **Asignación de agencias**: los roles restringidos ven solo **sus agencias asignadas**; de
  **Administrador para arriba** ven **todas** las agencias de la region y pueden **asignar agencias**
  a otros usuarios (`asignar_agencias`, §3).
- **Region NO muestra chips de vista** — solo el scope dropdown. (Un usuario de region no cambia a
  vista Admin/Developer.)

---

## 5. Vista Admin (acento guindo)  **[DEFINIDO]**

Browse global (`All` + buscador); ve todo como Region + **columna "Region"** en listas (solo cuando
existan regions). Controla, desde su sidebar de control:

- **Licencia de login** — estado de licencia/acceso de la plataforma.
- **Tokens de IA** — saldo **comprado / consumido por agencia** para los agentes de IA. (Recurso de
  negocio, no design tokens.)
- **Permisos / Roles** — gestión del **catálogo global de roles** (nombres de puesto + matriz de
  permisos por hoja + acciones, §3). Mismo catálogo para todas las agencias/regions.
- **Usuarios** — **crear** usuarios, **asignar** su **rol** (del catálogo global) y su agencia.
- **Brand** — logo, favicon y fotos del login (carrusel, logo, textos) por agencia.
- **Agencias** — **promover una agencia a "Region"**: dropdown + checkboxes de qué agencias
  administra esa region.

**[POR CONFIRMAR]**: si hay más de un nivel de usuario dentro del tenant Admin (ej. admin pleno vs
admin de solo-lectura).

---

## 6. Vista Developer (LOGIQ, acento morado)  **[DEFINIDO]**

Todo lo de Admin **+** la sección **"SYSTEM"**, y es **invisible al Admin**:

- **Version control** — tabla versión / fecha / dueño / comentario / timestamp; marca la **versión
  activa** (la que muestra el footer "Powered by").
- **System settings → Developer info** — logo, empresa, nombre y origen del developer; alimenta el
  footer del sidebar en **todas** las vistas.

Solo el **usuario developer** ve el chip Developer y esta sección.

---

## 7. Reglas de login (base)  **[DEFINIDO base + POR CONFIRMAR fino]**

- **[DEFINIDO]** Llaves de login: **Agencia (condicional) · Usuario o correo · Password**. El campo
  Agencia aparece solo con >1 tenant de capa pública.
- **[DEFINIDO]** Al autenticar: detectar categoría del tenant → asignar vista por defecto (§2).
- **[POR CONFIRMAR]**: validaciones exactas, recuperación de contraseña, "recuérdame", bloqueo por
  intentos.

---

## 8. Regla de oro

- Permisos **lógicos** siempre, **server-side**: la view (decorador de permiso) y los
  servicios/querysets validan vista, scope y CRUD. **Ocultar UI nunca es control de acceso.**
- Todo dato de dominio es **tenant-scoped** (`for_user(user)`): una consulta jamás devuelve datos
  fuera del scope del usuario.
- El código **no** menciona nombres de tenants concretos para decidir acceso: decide por
  **categoría + scope + nivel**, no por "si es MONTERREY1".
