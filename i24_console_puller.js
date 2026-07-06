/* =========================================================================
   Inmuebles24 — Lead Puller (snippet de consola)
   -------------------------------------------------------------------------
   USO:
   1. Abre y logueate en tu panel: https://www.inmuebles24.com/  (panel de leads)
   2. Abre la consola del navegador (F12 -> pestaña "Console").
   3. Pega TODO este archivo y presiona Enter.
   4. Aparece un mini-panel arriba a la derecha. Verifica sesión, elige fechas, Extraer.

   Corre DENTRO de la propia página (mismo-origen): usa tu sesión viva,
   sin CORS, sin servidor local, sin instalar nada.
   ========================================================================= */
(() => {
  if (window.__i24Puller) window.__i24Puller.remove();

  const BASE = location.origin; // mismo-origen: https://www.inmuebles24.com
  const PAGE_SIZE = 20;
  const MAX_PAGES = 50;         // tope de seguridad
  const cfg = { delayMs: 600 }; // delay entre requests (anti rate-limit)

  // ---- Auto-detección de sessionId + email desde storage/cookies -----------
  const reSession = /session[_-]?id|^sid$|token/i;
  const reEmail = /e-?mail|correo|username|user[_-]?name/i;

  function deepFind(obj, found, depth = 0) {
    if (depth > 5 || obj == null || typeof obj !== "object") return found;
    for (const k of Object.keys(obj)) {
      const v = obj[k];
      if (typeof v === "string") {
        if (!found.sessionId && reSession.test(k) && v.length > 8) found.sessionId = v;
        if (!found.email && reEmail.test(k) && /@/.test(v)) found.email = v;
      } else {
        deepFind(v, found, depth + 1);
      }
    }
    return found;
  }

  function autodetect() {
    const found = { sessionId: "", email: "" };
    // Cookies
    document.cookie.split(";").forEach((c) => {
      const [k, ...rest] = c.split("=");
      const key = (k || "").trim();
      const val = decodeURIComponent(rest.join("=").trim());
      if (!found.sessionId && reSession.test(key) && val.length > 8) found.sessionId = val;
      if (!found.email && reEmail.test(key) && /@/.test(val)) found.email = val;
    });
    // Storage (valores planos + JSON anidado)
    for (const store of [localStorage, sessionStorage]) {
      for (let i = 0; i < store.length; i++) {
        const key = store.key(i);
        const raw = store.getItem(key);
        if (!found.sessionId && reSession.test(key) && raw && raw.length > 8) found.sessionId = raw;
        if (!found.email && reEmail.test(key) && raw && /@/.test(raw)) found.email = raw;
        if (raw && (raw[0] === "{" || raw[0] === "[")) {
          try { deepFind(JSON.parse(raw), found); } catch (_) {}
        }
      }
    }
    return found;
  }

  // ---- Cliente HTTP --------------------------------------------------------
  function headers() {
    return {
      "sessionId": el("sid").value.trim(),
      "email": el("email").value.trim(),
      "x-panel-portal": "24MX",
      "accept": "application/json",
    };
  }

  async function apiGet(path) {
    const res = await fetch(BASE + path, { headers: headers(), credentials: "include" });
    if (!res.ok) throw new Error(`${res.status} en ${path}`);
    return res.json();
  }

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // ---- Normalización (esquema único de salida) -----------------------------
  function normalize(lead, profile) {
    const li = (profile && profile.lead_info) || {};
    const pf = (profile && profile.property_features) || {};
    const price = li.price || {};
    const stype = li.search_type || {};
    const post = lead.posting || {};
    const user = lead.lead_user || {};
    const msg = lead.last_message || {};
    const zonas = (((profile || {}).searched_locations || {}).neighborhoods || [])
      .map((n) => ({ nombre: n.name, peso: n.amount }));
    return {
      contact_id: lead.contact_publisher_user_id,
      nombre: user.name || "",
      email: user.email || "",
      telefono: user.phone || "",
      fecha_lead: lead.last_lead_date || "",
      mensaje: msg.text || "",
      inmueble: { titulo: post.title || "", operacion: post.operation_type || "", precio: post.price ?? null },
      busca: {
        tipo: stype.type || "", operacion: stype.operation || "",
        presupuesto_min: price.min ?? null, presupuesto_max: price.max ?? null,
        moneda: price.currency || "",
      },
      caracteristicas: {
        recamaras: pf.bedrooms ?? null, banos: pf.baths ?? null,
        area_total: pf.total_area_xm2 ?? null, garage_pct: pf.pct_of_postings_with_garage ?? null,
      },
      zonas,
      fuente: "api",
    };
  }

  // ---- Pull incremental ----------------------------------------------------
  async function pull(desde, hasta, incluirPerfil) {
    const out = [];
    let offset = 0;
    log(`Rango: ${desde.toISOString().slice(0, 10)} → ${hasta.toISOString().slice(0, 10)}`);
    while (offset < MAX_PAGES * PAGE_SIZE) {
      const path =
        `/leads-api/publisher/leads?offset=${offset}&limit=${PAGE_SIZE}` +
        `&spam=false&status=nondiscarded&action_type=6&sort=last_activity`;
      log(`Página offset=${offset}…`);
      const page = await apiGet(path);
      const rows = (page && page.result) || [];
      if (!rows.length) break;

      for (const lead of rows) {
        const f = new Date(lead.last_lead_date);
        if (f > hasta) continue;          // es de HOY / futuro → saltar
        if (f < desde) {                  // ya pasamos el rango (viene desc) → fin
          log(`Corte: lead ${f.toISOString().slice(0, 10)} < inicio de rango.`);
          return out;
        }
        let profile = null;
        if (incluirPerfil) {
          try {
            profile = await apiGet(`/leads-api/publisher/contact/${lead.contact_publisher_user_id}/user-profile`);
          } catch (e) { log(`⚠ perfil ${lead.contact_publisher_user_id}: ${e.message}`); }
          await sleep(cfg.delayMs);
        }
        out.push(normalize(lead, profile));
        setCount(out.length);
      }
      offset += PAGE_SIZE;
      await sleep(cfg.delayMs);
    }
    return out;
  }

  // ---- Descargas -----------------------------------------------------------
  function download(name, mime, text) {
    const url = URL.createObjectURL(new Blob([text], { type: mime }));
    const a = document.createElement("a");
    a.href = url; a.download = name; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  function toCSV(rows) {
    const cols = [
      "contact_id", "nombre", "email", "telefono", "fecha_lead", "mensaje",
      "inmueble_titulo", "inmueble_operacion", "inmueble_precio",
      "busca_tipo", "busca_operacion", "presupuesto_min", "presupuesto_max", "moneda",
      "recamaras", "banos", "area_total", "garage_pct", "zonas", "fuente",
    ];
    const esc = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
    const line = (r) => [
      r.contact_id, r.nombre, r.email, r.telefono, r.fecha_lead, r.mensaje,
      r.inmueble.titulo, r.inmueble.operacion, r.inmueble.precio,
      r.busca.tipo, r.busca.operacion, r.busca.presupuesto_min, r.busca.presupuesto_max, r.busca.moneda,
      r.caracteristicas.recamaras, r.caracteristicas.banos, r.caracteristicas.area_total, r.caracteristicas.garage_pct,
      r.zonas.map((z) => `${z.nombre} (${z.peso}%)`).join("; "), r.fuente,
    ].map(esc).join(",");
    return "﻿" + cols.join(",") + "\n" + rows.map(line).join("\n");
  }

  // ---- UI ------------------------------------------------------------------
  const el = (id) => document.getElementById("i24_" + id);
  const log = (m) => {
    const box = el("log");
    box.textContent += (box.textContent ? "\n" : "") + m;
    box.scrollTop = box.scrollHeight;
  };
  const setCount = (n) => { el("count").textContent = n; };

  const det = autodetect();
  const yday = new Date(); yday.setDate(yday.getDate() - 1);
  const weekAgo = new Date(); weekAgo.setDate(weekAgo.getDate() - 7);
  const d2s = (d) => d.toISOString().slice(0, 10);

  const panel = document.createElement("div");
  window.__i24Puller = panel;
  panel.innerHTML = `
    <style>
      #i24_panel * { box-sizing: border-box; font-family: system-ui, sans-serif; }
      #i24_panel { position: fixed; top: 16px; right: 16px; z-index: 999999; width: 340px;
        background: #0f172a; color: #e2e8f0; border: 1px solid #334155; border-radius: 12px;
        box-shadow: 0 12px 40px rgba(0,0,0,.5); font-size: 13px; overflow: hidden; }
      #i24_panel header { display:flex; justify-content:space-between; align-items:center;
        padding: 10px 12px; background: #1e293b; font-weight: 600; cursor: move; }
      #i24_panel .body { padding: 12px; display: flex; flex-direction: column; gap: 8px; }
      #i24_panel label { font-size: 11px; color: #94a3b8; display:block; margin-bottom: 2px; }
      #i24_panel input { width:100%; padding:6px 8px; background:#1e293b; border:1px solid #334155;
        border-radius:6px; color:#e2e8f0; font-size:12px; }
      #i24_panel .row { display:flex; gap:8px; } #i24_panel .row > div { flex:1; }
      #i24_panel button { padding:7px 10px; border:0; border-radius:7px; font-weight:600; cursor:pointer; font-size:12px; }
      #i24_panel .primary { background:#6366f1; color:#fff; } #i24_panel .primary:hover { background:#4f46e5; }
      #i24_panel .ghost { background:#334155; color:#e2e8f0; } #i24_panel .ghost:hover { background:#475569; }
      #i24_panel .x { background:none; color:#94a3b8; font-size:16px; padding:0 4px; }
      #i24_panel .log { background:#020617; border:1px solid #1e293b; border-radius:6px; padding:8px;
        height:110px; overflow:auto; white-space:pre-wrap; font-family:ui-monospace,monospace; font-size:11px; color:#cbd5e1; }
      #i24_panel .status { font-size:11px; } #i24_panel .ok { color:#4ade80; } #i24_panel .bad { color:#f87171; }
    </style>
    <div id="i24_panel">
      <header id="i24_drag">📥 Inmuebles24 · Lead Puller <button class="x" id="i24_close">✕</button></header>
      <div class="body">
        <div><label>email de la cuenta</label><input id="i24_email" value="${det.email || ""}" placeholder="correo@…"></div>
        <div><label>sessionId</label><input id="i24_sid" value="${det.sessionId || ""}" placeholder="token de sesión…"></div>
        <button class="ghost" id="i24_validate">1 · Validar sesión</button>
        <div class="status" id="i24_sess">—</div>
        <div class="row">
          <div><label>Desde</label><input type="date" id="i24_desde" value="${d2s(weekAgo)}"></div>
          <div><label>Hasta (incl.)</label><input type="date" id="i24_hasta" value="${d2s(yday)}"></div>
        </div>
        <div class="row" style="align-items:end">
          <div><label>Delay (ms)</label><input type="number" id="i24_delay" value="${cfg.delayMs}"></div>
          <div><label>Perfil de búsqueda</label>
            <select id="i24_perfil" style="width:100%;padding:6px 8px;background:#1e293b;border:1px solid #334155;border-radius:6px;color:#e2e8f0;font-size:12px">
              <option value="1">Sí (más lento)</option><option value="0">No, solo lista</option>
            </select></div>
        </div>
        <button class="primary" id="i24_pull">2 · Extraer  (<span id="i24_count">0</span>)</button>
        <div class="row">
          <div><button class="ghost" id="i24_json" style="width:100%">Descargar JSON</button></div>
          <div><button class="ghost" id="i24_csv" style="width:100%">Descargar CSV</button></div>
        </div>
        <div class="log" id="i24_log">Listo. Verifica email + sessionId (autodetectados si aparecen) y valida la sesión.</div>
      </div>
    </div>`;
  document.body.appendChild(panel);

  let RESULTS = [];

  el("close").onclick = () => panel.remove();

  el("validate").onclick = async () => {
    const s = el("sess"); s.textContent = "Validando…"; s.className = "status";
    try {
      const me = await apiGet("/leads-api/users/me");
      s.textContent = "✔ Sesión válida" + (me && me.email ? ` · ${me.email}` : "");
      s.className = "status ok";
    } catch (e) {
      s.textContent = `✗ ${e.message} — revisa sessionId/email (o cópialos de la pestaña Network).`;
      s.className = "status bad";
    }
  };

  el("pull").onclick = async () => {
    cfg.delayMs = Math.max(0, parseInt(el("delay").value || "600", 10));
    const desde = new Date(el("desde").value + "T00:00:00");
    const hasta = new Date(el("hasta").value + "T23:59:59");
    const incluirPerfil = el("perfil").value === "1";
    if (!(desde <= hasta)) { log("⚠ Rango de fechas inválido."); return; }
    el("pull").disabled = true; setCount(0);
    log("── Iniciando extracción ──");
    try {
      RESULTS = await pull(desde, hasta, incluirPerfil);
      log(`✔ Listo: ${RESULTS.length} leads. Ya puedes descargar JSON/CSV.`);
    } catch (e) {
      log(`✗ Error: ${e.message}`);
    } finally {
      el("pull").disabled = false;
    }
  };

  el("json").onclick = () => {
    if (!RESULTS.length) return log("Nada que descargar todavía.");
    download(`leads_i24_${el("desde").value}_a_${el("hasta").value}.json`, "application/json", JSON.stringify(RESULTS, null, 2));
  };
  el("csv").onclick = () => {
    if (!RESULTS.length) return log("Nada que descargar todavía.");
    download(`leads_i24_${el("desde").value}_a_${el("hasta").value}.csv`, "text/csv", toCSV(RESULTS));
  };

  // Arrastrar el panel
  (() => {
    const head = el("drag"); let sx, sy, ox, oy, drag = false;
    head.onmousedown = (e) => { drag = true; sx = e.clientX; sy = e.clientY;
      const r = el("panel").getBoundingClientRect(); ox = r.left; oy = r.top; e.preventDefault(); };
    document.onmousemove = (e) => { if (!drag) return; const p = el("panel");
      p.style.left = ox + e.clientX - sx + "px"; p.style.top = oy + e.clientY - sy + "px"; p.style.right = "auto"; };
    document.onmouseup = () => { drag = false; };
  })();

  console.log("%c📥 Inmuebles24 Lead Puller cargado.", "color:#6366f1;font-weight:bold");
})();
