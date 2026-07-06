# Inmuebles24 — Lead Puller (Build Plan)

> Automatización para extraer leads/interesados desde el panel de Inmuebles24
> hacia un CRM propio, disparado por un botón. Pull incremental + fallback a Excel.

---

## 0. Contexto y objetivo

Construir un servicio que, al presionarse un **botón en el CRM**, extraiga los leads
nuevos del panel de interesados de **Inmuebles24** desde el último pull, con el perfil
de búsqueda de cada cliente (qué busca, zonas, características, presupuesto, mensaje),
y los guarde en el CRM.

- **Volumen esperado:** <300 leads/semana.
- **Estrategia de fecha:** traer desde `last_read_date` (guardada en el CRM) hasta
  **ayer** (día -1), dejando el día de HOY "vivo" para que sigan cargando leads en el sitio de Inmuebles24
- **Resiliencia:** si la API se bloquea, caer a la descarga de Excel (mismo dataset).

---

## 1. Hallazgos técnicos (base del diseño)

Todo esto ya está verificado contra el sitio real.

### 1.1 Autenticación
- La API interna vive bajo `https://www.inmuebles24.com/leads-api/...`.
- Cada request lleva estos headers:
  - `sessionId: <token>`  ← token de sesión, **proviene de una cookie de sesión**.
  - `x-panel-portal: 24MX`
  - `email: <email de la cuenta>`
- Sin estos headers, la API responde **401**. Las cookies solas NO bastan si el
  cliente HTTP no reenvía el header `sessionId`.

### 1.2 Protecciones del sitio
- **Cloudflare** al frente (`server: cloudflare`, `cf-ray`). Riesgo de rate-limit
  y de detección de navegador automatizado (`navigator.webdriver`).
- **reCAPTCHA en el login** (aparece cuando NO hay sesión). Es el punto frágil:
  automatizar el login desde cero choca con el captcha.

### 1.3 Endpoints clave

| Propósito | Método | Endpoint |
|---|---|---|
| Listado de leads (paginado) | GET | `/leads-api/publisher/leads?offset={o}&limit={l}&spam=false&status=nondiscarded&action_type=6&sort=last_activity` |
| Detalle de contacto | GET | `/leads-api/publisher/contact/{contact_id}` |
| **Perfil de búsqueda** | GET | `/leads-api/publisher/contact/{contact_id}/user-profile` |
| Conversación/chat | GET | `/leads-api/leads/{contact_id}/chat` |
| Avisos relacionados | GET | `/leads-api/publisher/leads/{contact_id}/related` |
| Usuario actual (validar sesión) | GET | `/leads-api/users/me` |
| **Fallback Excel** | GET | `/leads-api/leads/v3/export/{YYYY-MM-DD}/to/{YYYY-MM-DD}` |

Notas:
- `action_type=6` = mensajes. Otros tipos: `10`/`11` = teléfono/WhatsApp, etc.
  (ajustar según qué canales quieras incluir).
- `sort=last_activity` → los más recientes primero (ideal para pull incremental).
- El `contact_id` que necesitas para el detalle es el campo
  `contact_publisher_user_id` de cada item del listado.

### 1.4 Estructura de datos (lo que devuelve cada endpoint)

**Listado** → `{ total_count, paging:{offset,limit,total}, result:[ lead ] }`
donde cada `lead` trae:
- `contact_publisher_user_id` (ID para el detalle)
- `last_lead_date` (timestamp ISO → filtro de fecha)
- `lead_user` `{ name, email, phone, user_id }`
- `last_message` `{ text, date, from_seeker }`  ← el mensaje que envió
- `posting` `{ title, address, price, operation_type, location, ... }`

**user-profile** → lo más valioso para perfilar:
- `lead_info` `{ price:{min,max,currency}, search_type:{type,operation}, views, contacts, started_search_days }`
- `property_features` `{ bedrooms, baths, total_area_xm2, covered_area_xm2, pet_friendly, pct_of_postings_with_garage, ... }`
- `searched_locations` `{ neighborhoods:[{name,amount}], streets:[{city,name,percent}] }`

---

## 2. Arquitectura recomendada

**Principio clave: separar LOGIN de EXTRACCIÓN.**

El reCAPTCHA vive en el login. Automatizar login repetido es frágil y arriesgado.
Por eso:
┌─────────────┐   1. Login manual/asistido (1 vez)   ┌──────────────────┐

│   Usuario   │ ───────────────────────────────────► │ Captura sessionId │

└─────────────┘        (resuelve reCAPTCHA)           │ + email guardados │

│   en el CRM       │

└────────┬─────────┘

│

┌─────────────┐   2. Click botón → pull incremental            │

│  Botón CRM  │ ───────────────────────────────────────────────┘

└─────────────┘   usa sessionId guardado (requests HTTP, sin navegador)

│

├── OK  → API JSON (rápido, granular)

└── FAIL→ Fallback Excel export

- **Extracción vía `requests` (HTTP puro), NO Selenium.** Una vez que tienes el
  `sessionId`, no necesitas navegador. Es más rápido, más barato y no dispara la
  detección de `webdriver` de Cloudflare.
- **Selenium sólo (y opcionalmente) para el login**, cuando el `sessionId` expire
  y quieras renovarlo semi-automático. Ver §6.

---

## 3. Estructura del proyecto
inmuebles24_puller/

├── config.py            # portal, base URL, límites, delays

├── session.py           # manejo de sessionId (cargar, validar, refrescar)

├── api_client.py        # llamadas HTTP a la leads-api

├── excel_fallback.py    # descarga y parseo del Excel de respaldo

├── normalize.py         # mapea JSON/Excel → esquema único del CRM

├── incremental.py       # lógica de pull desde last_read_date hasta ayer

├── main.py              # endpoint que el botón del CRM invoca

└── requirements.txt

`requirements.txt`:
requests

python-dateutil

openpyxl          # leer el Excel de fallback

selenium          # solo para el flujo de login/refresh de sesión

undetected-chromedriver   # opcional, login stealth

---

## 4. Componentes — qué hace cada uno

### 4.1 `config.py`
- `BASE = "https://www.inmuebles24.com"`
- Headers base: `x-panel-portal: 24MX`, `accept: application/json`,
  un `User-Agent` de navegador real y consistente.
- `PAGE_SIZE = 20`, `REQUEST_DELAY = 1.5` seg (anti rate-limit),
  `MAX_PAGES = 50` (tope de seguridad).

### 4.2 `session.py`
- `load_session()` → lee `sessionId` + `email` desde el store del CRM.
- `is_valid(session)` → llama `GET /leads-api/users/me`; si 200, la sesión vive;
  si 401, hay que renovar.
- `save_session(...)` / señal al CRM de "sesión expirada, renovar".

### 4.3 `api_client.py`
Un `requests.Session` con los headers fijos + `sessionId`. Métodos:
- `list_leads(offset, limit, action_type=6)` → una página del listado.
- `get_user_profile(contact_id)` → perfil de búsqueda.
- `get_contact(contact_id)` / `get_chat(contact_id)` (opcionales).
- Cada método: manejar 401 (→ refresh), 429/403 (→ backoff), respetar `REQUEST_DELAY`.

### 4.4 `incremental.py` — el corazón
pull_incremental(last_read_date):

cutoff_desde = last_read_date

cutoff_hasta = ayer 23:59:59   # deja HOY vivo

leads = []

offset = 0

while offset < MAX_PAGES * PAGE_SIZE:

page = api.list_leads(offset, PAGE_SIZE)          # sort=last_activity

for lead in page.result:

fecha = parse(lead.last_lead_date)

if fecha > cutoff_hasta:   continue           # es de HOY → saltar

if fecha < cutoff_desde:   return leads       # ya pasamos el rango → fin

profile = api.get_user_profile(lead.contact_publisher_user_id)

leads.append(normalize(lead, profile))

offset += PAGE_SIZE

sleep(REQUEST_DELAY)

return leads
Como el listado viene ordenado por `last_activity` (desc), en cuanto encuentras
una fecha anterior a `cutoff_desde` puedes cortar: no hace falta recorrer todo.

### 4.5 `excel_fallback.py`
- `GET /leads-api/leads/v3/export/{desde}/to/{hasta}` con el mismo `sessionId`.
- Guardar el `.xlsx`, parsear con `openpyxl`, mapear columnas → `normalize()`.
- Se invoca cuando la API JSON falla (401 tras refresh, 403, o Cloudflare).

### 4.6 `normalize.py`
Esquema único de salida (mismo formato para JSON y Excel), p. ej.:
```json
{
  "contact_id": "...",
  "nombre": "...", "email": "...", "telefono": "...",
  "fecha_lead": "2026-07-05T...",
  "mensaje": "...",
  "inmueble": {"titulo": "...", "operacion": "...", "precio": ...},
  "busca": {"tipo": "...", "operacion": "...", "presupuesto_min": ..., "presupuesto_max": ...},
  "caracteristicas": {"recamaras": ..., "banos": ..., "area_total": ..., "garage_pct": ...},
  "zonas": [{"nombre": "...", "peso": ...}],
  "fuente": "api" | "excel"
}
```

### 4.7 `main.py`
Endpoint HTTP (Flask/FastAPI) que el botón del CRM llama:
POST /pull

body: { last_read_date }

→ valida sesión

→ intenta pull_incremental()   (fuente="api")

→ si falla, excel_fallback()   (fuente="excel")

→ devuelve leads normalizados + nueva last_read_date (= ayer)
El CRM guarda la nueva `last_read_date` sólo si el pull fue exitoso.

---

## 5. Estrategia anti-bloqueo (Cloudflare)

- **No uses navegador para la extracción** → evita `navigator.webdriver`.
- **Delay de 1–2 s** entre requests. Con ~250 leads/semana son pocas llamadas.
- **User-Agent realista y estable**, igual al de tu navegador de login.
- **Backoff exponencial** ante 429/403; si Cloudflare bloquea, cae a Excel.
- **No corras en paralelo** ni con múltiples IPs raras; una corrida secuencial.
- **Reutiliza la misma sesión** el mayor tiempo posible (menos logins = menos captcha).

---

## 6. Login / refresh de sessionId (cuando expire)

Dos opciones, de menor a mayor automatización:

**A) Manual asistido (recomendado para empezar):**
El usuario entra a Inmuebles24 en su navegador, y una pequeña extensión/bookmarklet
o copiar-pegar toma el header `sessionId` + `email` y los guarda en el CRM.
Cero captcha automatizado, cero riesgo.

**B) Selenium stealth (si quieres refresh automático):**
- Usar `undetected-chromedriver` (o Playwright con args anti-detección).
- Navegar al login, ingresar credenciales del CRM.
- **reCAPTCHA:** aquí está el riesgo. Si aparece la versión invisible y la reputación
  de la IP es buena, puede pasar solo; si aparece el checkbox/challenge, requiere
  intervención humana. NO integrar solvers de captcha de terceros (viola ToS y sube costo/riesgo).
- Tras login, extraer la cookie `sessionId` de las cookies del driver → guardar en CRM.

> Recomendación: arranca con (A). Migra a (B) sólo si el mantenimiento manual te molesta.

---

## 7. Consideraciones legales / de riesgo

- Es una **API interna no documentada**; puede cambiar sin aviso → aislar los
  endpoints en `api_client.py` para arreglar rápido si rompen.
- Automatizar el acceso probablemente **roza los Términos de Servicio** de Inmuebles24.
  El riesgo de bloqueo de cuenta nunca es 0.
- Maneja **datos personales de terceros** (contactos): cumple tu política de datos.
- **En paralelo, sigue solicitando el acceso oficial / API para clientes** a tu
  ejecutivo de cuenta. Es el camino sostenible; esto es el puente mientras tanto.

---

## 8. Fases de construcción (checklist)

- [ ] **Fase 0** — Capturar manualmente un `sessionId` válido y probar `GET /users/me` (200).
- [ ] **Fase 1** — `api_client.list_leads()` + paginación; imprimir leads crudos.
- [ ] **Fase 2** — `get_user_profile()` + `normalize()`; validar el esquema de salida.
- [ ] **Fase 3** — `incremental.pull_incremental()` con lógica de fechas (desde/hasta ayer).
- [ ] **Fase 4** — `excel_fallback()` y prueba forzando un fallo de la API.
- [ ] **Fase 5** — `main.py` endpoint + integración del botón del CRM + guardar `last_read_date`.
- [ ] **Fase 6** — Manejo de sesión (validar/expirar/refrescar) y alertas.
- [ ] **Fase 7** — Hardening anti-bloqueo (delays, backoff, UA) y logging.

---

## 9. Datos de prueba (referencia real capturada)

Lead de ejemplo (`SÁNCHEZ`, contact_id `261876730`):
- Mensaje: "¡Hola! Quiero que se comuniquen conmigo por este inmueble en renta…"
- Busca: Casa en Alquiler, MXN 40,000–48,000, 13 avisos vistos, 4 contactos.
- Features: 3 recámaras, 3–4 baños, 280–380 m² totales, 75% de avisos con cochera.
- Zonas: Contry Sol (67%), Contry (33%), Nuevo León.
- (Nota: la API devuelve las zonas aunque la UI las muestre vacías.)