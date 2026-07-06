"""Navegacion centralizada del cockpit (vista Operativa).

Cada item declara su `recurso` (RecursoKey) para que mas adelante el gate de
permiso sea `puede(user, recurso, 'leer')`. Por ahora es solo visual/navegable.
Los iconos son SVG inline (outline) — nunca emojis (no renderizan en Windows).
"""

# Iconos outline (viewBox 24, stroke currentColor). Se renderizan con |safe.
ICONS = {
    "board": '<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="18" rx="1"/><rect x="14" y="3" width="7" height="11" rx="1"/></svg>',
    "users": '<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><circle cx="9" cy="8" r="3"/><path d="M3 20a6 6 0 0112 0M16 6a3 3 0 010 6M21 20a6 6 0 00-4-5.7"/></svg>',
    "chat": '<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><path d="M4 5h16v11H8l-4 3z"/></svg>',
    "book": '<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><path d="M4 5a2 2 0 012-2h13v16H6a2 2 0 00-2 2z"/></svg>',
    "chart": '<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></svg>',
    "gauge": '<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><path d="M12 13l4-3M4 18a8 8 0 1116 0"/></svg>',
    "funnel": '<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><path d="M3 4h18l-7 8v6l-4 2v-8z"/></svg>',
    "spark": '<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2 2M16 16l2 2M18 6l-2 2M8 16l-2 2"/></svg>',
    "calendar": '<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 9h18M8 3v4M16 3v4"/></svg>',
    "user": '<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><circle cx="12" cy="8" r="3.2"/><path d="M5 20a7 7 0 0114 0"/></svg>',
    "id": '<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="8" cy="12" r="2"/><path d="M13 10h5M13 14h5"/></svg>',
    "cog": '<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/></svg>',
    "note": '<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><path d="M4 5h16v11H8l-4 3z"/><path d="M8 9h8M8 12h5"/></svg>',
    "inbox": '<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><path d="M4 13h4l2 3h4l2-3h4M4 13V6a2 2 0 012-2h12a2 2 0 012 2v7M4 13v5a2 2 0 002 2h12a2 2 0 002-2v-5"/></svg>',
    "download": '<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><path d="M12 3v12M7 10l5 5 5-5M5 21h14"/></svg>',
    "plug": '<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><path d="M9 2v5M15 2v5M7 7h10v4a5 5 0 01-10 0zM12 16v6"/></svg>',
}

# Grupos del menu (vista Operativa). `url` es el name de la ruta; `icon` es el SVG.
NAV_OPERATIVA = [
    {"title": "Operación", "items": [
        {"label": "Leads", "url": "leads", "icon": ICONS["users"], "recurso": "leads"},
        {"label": "Pipeline", "url": "pipeline", "icon": ICONS["board"], "recurso": "pipeline"},
        {"label": "Muro de comentarios", "url": "muro", "icon": ICONS["note"], "recurso": "muro"},
        {"label": "Libros", "url": "libros", "icon": ICONS["book"], "recurso": "libros"},
    ]},
    {"title": "Lead management", "items": [
        {"label": "Conversaciones", "url": "conversaciones", "icon": ICONS["inbox"], "recurso": "conversaciones", "badge": "5"},
        {"label": "Leads Inmuebles24", "url": "leads_inmuebles", "icon": ICONS["download"], "recurso": "leads_inmuebles"},
        {"label": "Integraciones", "url": "integraciones", "icon": ICONS["plug"], "recurso": "integraciones"},
    ]},
    {"title": "Analítica", "items": [
        {"label": "Ventas", "url": "ventas", "icon": ICONS["chart"], "recurso": "ventas"},
        {"label": "Team performance", "url": "team", "icon": ICONS["gauge"], "recurso": "team_performance"},
        # Funnel se combinó dentro de Pipeline (vista de embudo).
    ]},
    {"title": "Automatizaciones + IA", "items": [
        {"label": "Agentes IA", "url": "agentes", "icon": ICONS["spark"], "recurso": "agentes"},
    ]},
    {"title": "Sistema operativo", "items": [
        {"label": "Junta semanal", "url": "junta_semanal", "icon": ICONS["calendar"], "recurso": "junta_semanal"},
        {"label": "1:1", "url": "uno_a_uno", "icon": ICONS["user"], "recurso": "uno_a_uno"},
    ]},
    {"title": "Administración", "items": [
        {"label": "Asesores", "url": "asesores", "icon": ICONS["id"], "recurso": "asesores"},
        {"label": "Configuración", "url": "configuracion", "icon": ICONS["cog"], "recurso": "configuracion"},
    ]},
]

# Chips de vista (top bar). Placeholder visual; el switching real llega con tenancy.
VIEWS = [
    {"key": "agencia", "label": "Agencia", "accent": "var(--accent-operativa)"},
    {"key": "region", "label": "Region", "accent": "var(--accent-operativa)"},
    {"key": "admin", "label": "Admin", "accent": "var(--accent-admin)"},
    {"key": "developer", "label": "Developer", "accent": "var(--accent-developer)"},
]
