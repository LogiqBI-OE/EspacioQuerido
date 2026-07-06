"""Vistas del shell (checkpoint F0).

Home = Pipeline (con datos mock inline para que se vea el lenguaje visual).
El resto de hojas usan un placeholder generico navegable. Los datos reales y
la capa de servicios/tenancy llegan en los siguientes tramos.
"""

from django.shortcuts import render

# --- datos mock inline (temporales) para el Pipeline del checkpoint ----------
KPIS = [
    {"label": "Operaciones activas", "value": "48", "delta": "+6 esta semana", "up": True},
    {"label": "Por aprobar (IA)", "value": "3", "delta": "requieren decisión", "up": False},
    {"label": "Citas esta semana", "value": "12", "delta": "+3 vs anterior", "up": True},
    {"label": "Cierres del mes", "value": "7", "delta": "meta: 10", "up": False},
    {"label": "Comisión proyectada", "value": "$284k", "delta": "+18%", "up": True},
]

COLUMNS = [
    {"name": "Nuevos", "dot": "#94a3b8", "cards": [
        {"nombre": "Laura Mendoza", "busca": "Depto 2 rec · San Pedro", "grado": "A", "temp": "caliente", "fuente": "WhatsApp", "asesor": "A. Ríos"},
        {"nombre": "Diego Salas", "busca": "Casa · Cumbres", "grado": "B", "temp": "tibio", "fuente": "Meta Ads", "asesor": "M. Luna"},
    ]},
    {"name": "Calificados", "dot": "#6366f1", "cards": [
        {"nombre": "Carlos Reyna", "busca": "Depto inversión · Centro", "grado": "A", "temp": "caliente", "fuente": "EasyBroker", "asesor": "A. Ríos"},
        {"nombre": "Paola Cantú", "busca": "Casa 3 rec · Carza", "grado": "C", "temp": "frio", "fuente": "Referido", "asesor": "J. Vega"},
    ]},
    {"name": "Citas", "dot": "#0ea5e9", "cards": [
        {"nombre": "Familia Treviño", "busca": "Casa · Valle Alto", "grado": "A", "temp": "caliente", "fuente": "WhatsApp", "asesor": "M. Luna"},
    ]},
    {"name": "Negociación", "dot": "#f59e0b", "cards": [
        {"nombre": "Roberto Gil", "busca": "Depto · Tec", "grado": "B", "temp": "tibio", "fuente": "EasyBroker", "asesor": "J. Vega"},
    ]},
    {"name": "Cierre", "dot": "#10b981", "cards": [
        {"nombre": "Sofía Marín", "busca": "Casa · Cumbres", "grado": "A", "temp": "caliente", "fuente": "Referido", "asesor": "A. Ríos"},
    ]},
    {"name": "Reactivación", "dot": "#a78bfa", "cards": [
        {"nombre": "Hugo Peña", "busca": "Depto · San Jerónimo", "grado": "C", "temp": "frio", "fuente": "Meta Ads", "asesor": "M. Luna"},
    ]},
]


# --- Leads: directorio con toda la lista de clientes (mock) ------------------
LEADS = [
    {"nombre": "Laura Mendoza", "fuente": "WhatsApp", "etapa": "Nuevos", "asesor": "A. Ríos", "grado": "A", "temp": "caliente"},
    {"nombre": "Diego Salas", "fuente": "Meta Ads", "etapa": "Nuevos", "asesor": "M. Luna", "grado": "B", "temp": "tibio"},
    {"nombre": "Carlos Reyna", "fuente": "EasyBroker", "etapa": "Calificados", "asesor": "A. Ríos", "grado": "A", "temp": "caliente"},
    {"nombre": "Paola Cantú", "fuente": "Referido", "etapa": "Calificados", "asesor": "J. Vega", "grado": "C", "temp": "frio"},
    {"nombre": "Familia Treviño", "fuente": "WhatsApp", "etapa": "Citas", "asesor": "M. Luna", "grado": "A", "temp": "caliente"},
    {"nombre": "Roberto Gil", "fuente": "EasyBroker", "etapa": "Negociación", "asesor": "J. Vega", "grado": "B", "temp": "tibio"},
    {"nombre": "Sofía Marín", "fuente": "Referido", "etapa": "Cierre", "asesor": "A. Ríos", "grado": "A", "temp": "caliente"},
    {"nombre": "Hugo Peña", "fuente": "Meta Ads", "etapa": "Reactivación", "asesor": "M. Luna", "grado": "C", "temp": "frio"},
    {"nombre": "Andrea Lozano", "fuente": "Inmuebles24", "etapa": "Nuevos", "asesor": "J. Vega", "grado": "B", "temp": "tibio"},
    {"nombre": "Miguel Ordaz", "fuente": "Inmuebles24", "etapa": "Calificados", "asesor": "A. Ríos", "grado": "A", "temp": "caliente"},
]


def leads(request):
    return render(request, "pages/leads.html", {
        "page_title": "Leads",
        "page_subtitle": "Directorio de clientes — de dónde viene, en qué etapa, quién lo lleva",
        "leads": LEADS,
    })


def pipeline(request):
    return render(request, "pages/pipeline.html", {
        "page_title": "Pipeline",
        "page_subtitle": "El estado del negocio de un vistazo",
        "kpis": KPIS,
        "columns": COLUMNS,
    })


# --- Junta semanal (antes Money Monday): reporte semanal por consultor -------
JUNTA_SEMANAL = [
    {"consultor": "Pamela Martinez", "asistencia": True, "hot": 1, "seguimiento": "Sonia terreno 3 mdp SUR", "ofrec": 0, "separ": 1, "citas_real": 4, "citas_plan": 0, "evaluacion": "asignar", "comentarios": "Separación valle alto con Mich, renta de Gloria ya se firmó"},
    {"consultor": "Samuel Higareda", "asistencia": True, "hot": 3, "seguimiento": "Edgar Heredia 3.4 mdp Sur // Sebastian Delgado", "ofrec": 1, "separ": 0, "citas_real": 4, "citas_plan": 2, "evaluacion": "ok", "comentarios": "Oferta Edgar Heredia 3.4 mdp a terreno en satélite, está en $3,750,000"},
    {"consultor": "Michelle Iracheta", "asistencia": True, "hot": 1, "seguimiento": "Frida Hdz rnt 45k san pedro", "ofrec": 0, "separ": 2, "citas_real": 6, "citas_plan": 0, "evaluacion": "ok", "comentarios": "Seguimiento operación Hugo"},
    {"consultor": "Diego Cervantes", "asistencia": True, "hot": 2, "seguimiento": "Ivett depa san pedro 20 mdp // René bodega 15", "ofrec": 1, "separ": 1, "citas_real": 9, "citas_plan": 0, "evaluacion": "asignar", "comentarios": "Hoy firma Fundadores // separación depa san jemo 31.5"},
    {"consultor": "Salma Karina Romero", "asistencia": True, "hot": 2, "seguimiento": "Paola Camacho 40k SJ // Josue 90k SP", "ofrec": 0, "separ": 1, "citas_real": 4, "citas_plan": 4, "evaluacion": "asignar", "comentarios": "Separación se firma esta semana, asignar un par de clientes venta"},
    {"consultor": "Perla Sarahi Cavazos", "asistencia": True, "hot": 3, "seguimiento": "Andrea Cuervo 4.7 mdp SN // Alan Silva 15 mdp", "ofrec": 0, "separ": 1, "citas_real": 12, "citas_plan": 3, "evaluacion": "ok", "comentarios": "Ya se separó la casa de Arteaga, crédito con Lily; Julio se firma"},
    {"consultor": "Alexia Lyzet Francke", "asistencia": True, "hot": 1, "seguimiento": "Jaime Peña 40k Sur SJ", "ofrec": 1, "separ": 0, "citas_real": 7, "citas_plan": 0, "evaluacion": "asignar", "comentarios": "Oferta Depa de Levant 37.5 un cliente de Mafer. Asignar cliente"},
    {"consultor": "Ricardo Raziel Tovar", "asistencia": True, "hot": 3, "seguimiento": "Karim depa valle oriente 40-50k // Ilse casa san jemo", "ofrec": 0, "separ": 0, "citas_real": 1, "citas_plan": 0, "evaluacion": "feedback", "comentarios": "Tener 1:1 porque solo ha tenido 1 cita en un mes"},
]


def junta_semanal(request):
    return render(request, "pages/junta_semanal.html", {
        "page_title": "Junta semanal",
        "page_subtitle": "Ritual semanal — cómo cerró la semana pasada y el plan de ésta",
        "reales_fecha": "22 jun 2026",
        "plan_fecha": "29 jun 2026",
        "filas": JUNTA_SEMANAL,
    })


# --- Ventas: dashboards en acordeón ------------------------------------------
TOP_ASESORES = [
    ("Pamela Martinez", 1256), ("A. Mercadillo", 840), ("Gloria Gonzalez", 518),
    ("Esmeralda Romero", 497), ("Michelle Iracheta", 421), ("Melissa Justo", 410),
    ("Diego Cervantes", 326), ("Samuel Higareda", 293), ("Antonio Valdivia", 285),
    ("Diana Salazar", 240), ("Mafer Rios", 237), ("Alma Luevano", 229),
]
TENDENCIA = [("Sem 22", 148), ("Sem 23", 196), ("Sem 24", 40), ("Sem 25", 443), ("Sem 26", 5657)]
POR_COBRAR_ASESOR = [
    ("Pamela Martinez", 1016), ("Michelle Iracheta", 336), ("Diana Salazar", 240),
    ("Mafer Rios", 237), ("Alma Luevano", 229), ("Perla Cavazos", 226),
    ("Melissa Justo", 195), ("Samuel Higareda", 174), ("Raul Garcia", 167), ("Gloria Gonzalez", 105),
]
OFRECIMIENTO_ASESOR = [
    ("A. Mercadillo", 755), ("Esmeralda Romero", 239), ("Antonio Valdivia", 236),
    ("Melissa Justo", 175), ("Alejandra Jaime", 158), ("Gloria Gonzalez", 126),
    ("Samuel Higareda", 104), ("Michelle Iracheta", 85), ("Fernando Martinez", 81),
]
OFRECIMIENTO_DETALLE = [
    {"id": 707, "op": "Venta", "asesor": "Fernando Flores", "comision": "$201,000", "zona": "SPGG", "cliente": "Esthela Cleto", "coment": "El vendedor quiere mínimo $7.2, negociando a $7 mdp"},
    {"id": 711, "op": "Venta", "asesor": "Fernando Martinez", "comision": "$81,000", "zona": "Escobedo", "cliente": "Emmanuel Cantú", "coment": "Separando propiedad, trámite de sucesión"},
    {"id": 780, "op": "Venta", "asesor": "Fernando Flores", "comision": "$103,500", "zona": "Lagos", "cliente": "Rodrigo Garza", "coment": "Esperando contrapropuesta"},
    {"id": 817, "op": "Venta", "asesor": "Alejandra Jaime", "comision": "$103,500", "zona": "Vergel", "cliente": "Claudia y Miguel", "coment": "Necesitan 3 meses para el recurso"},
    {"id": 844, "op": "Renta", "asesor": "Michelle Iracheta", "comision": "$85,000", "zona": "Campestre", "cliente": "Bethzabe R.", "coment": "Ya pagaron investigación"},
]
POR_COBRAR_DETALLE = [
    {"id": 788, "op": "Venta", "asesor": "Mafer Rios", "comision": "$237,000", "sep": "25-May-26", "zona": "Vista Hermosa", "cliente": "Yolanda Bortoni", "coment": "Oferta muy baja, en negociación"},
    {"id": 640, "op": "Venta", "asesor": "Pamela Martinez", "comision": "$310,000", "sep": "12-May-26", "zona": "Valle Alto", "cliente": "Sergio Lima", "coment": "Crédito en revisión"},
    {"id": 655, "op": "Renta", "asesor": "Alma Luevano", "comision": "$64,000", "sep": "02-Jun-26", "zona": "Cumbres", "cliente": "Nora Peña", "coment": "Pendiente firma"},
]
SEPARACION_DETALLE = [
    {"id": 701, "asesor": "Diego Cervantes", "comision": "$105,000", "sep": "20-Jun-26", "zona": "San Jemo", "cliente": "Ivett Ramos", "coment": "Se firma esta semana"},
    {"id": 733, "asesor": "Perla Cavazos", "comision": "$88,000", "sep": "18-Jun-26", "zona": "Arteaga", "cliente": "Andrea Cuervo", "coment": "Crédito con Lily"},
]


def ventas(request):
    return render(request, "pages/ventas.html", {
        "page_title": "Ventas · Dashboards",
        "page_subtitle": "Cómo va el dinero del mes — comisiones y sus ángulos",
        "kpis": [
            {"label": "Total operaciones", "value": "72"},
            {"label": "Facturado", "value": "$1.3M"},
            {"label": "Por cobrar", "value": "$3.1M"},
            {"label": "En separación", "value": "—"},
            {"label": "Ofrecimiento", "value": "$2.4M"},
            {"label": "Portafolio", "value": "$79.1M"},
        ],
        "cumplimiento": 86,
        "top_asesores": TOP_ASESORES,
        "tendencia": TENDENCIA,
        "funnel": [("Facturado", 1.3), ("Por cobrar", 3.1), ("Ofrecimiento", 2.4)],
        "por_cobrar_asesor": POR_COBRAR_ASESOR,
        "por_cobrar_detalle": POR_COBRAR_DETALLE,
        "ofrecimiento_asesor": OFRECIMIENTO_ASESOR,
        "ofrecimiento_detalle": OFRECIMIENTO_DETALLE,
        "separacion_detalle": SEPARACION_DETALLE,
    })


# --- 1:1: evaluación de KPIs por asesor --------------------------------------
UNO_A_UNO_KPIS = [
    {"kpi": "Asistencia 1 a 1", "valor": 100, "objetivo": 75, "nivel": "Excelente"},
    {"kpi": "Actualización status", "valor": 100, "objetivo": 75, "nivel": "Excelente"},
    {"kpi": "Actualización comentarios", "valor": 100, "objetivo": 75, "nivel": "Excelente"},
    {"kpi": "Citas", "valor": 50, "objetivo": 75, "nivel": "Aceptable"},
    {"kpi": "Evaluación de junta semanal", "valor": 75, "objetivo": 75, "nivel": "Bueno"},
    {"kpi": "Conversión Citas (Leads → Citas)", "valor": 50, "objetivo": 75, "nivel": "Aceptable"},
    {"kpi": "Conversión Global (Leads → Cierres)", "valor": 75, "objetivo": 75, "nivel": "Bueno"},
]


def uno_a_uno(request):
    return render(request, "pages/uno_a_uno.html", {
        "page_title": "1:1",
        "page_subtitle": "Evaluación semanal de KPIs del asesor y puntos a reforzar",
        "asesores": ["Raul Garcia Gzz", "Pamela Martinez", "Michelle Iracheta", "Samuel Higareda"],
        "asesor": "Raul Garcia Gzz",
        "periodo": "2025 · Sem 3",
        "kpis": UNO_A_UNO_KPIS,
        "reforzar_opciones": ["Captaciones", "Citas", "Conversión de citas", "Conversión global", "Seguimiento / status"],
        "punto_reforzar": "Captaciones",
        "comentario": "Raul se va a enfocar al cien en captar y también en subir citas a pesar de su buena conversión.",
    })


# --- Libro de comisiones -----------------------------------------------------
LIBRO_COMISIONES = [
    {"asesor": "Andres Quiñones", "contrato": "Modelo 1", "op": "Renta", "cliente": "Obispado", "propiedad": "Torre Obispado", "municipio": "Monterrey", "fecha_venta": "02-Ene-23", "fecha_cobro": "17-Ene-23", "venta": "$19,500", "com_total": "$19,500", "com_asesor": "$15,600", "com_eq": "$3,900"},
    {"asesor": "Martín Valenzuela", "contrato": "Modelo 2", "op": "Venta", "cliente": "Torre UNA", "propiedad": "Torre UNA (IDEI)", "municipio": "Monterrey", "fecha_venta": "17-Ene-23", "fecha_cobro": "—", "venta": "$3,027,246", "com_total": "$90,817", "com_asesor": "$63,572", "com_eq": "$27,245"},
    {"asesor": "Samuel Higareda", "contrato": "Modelo 2", "op": "Venta", "cliente": "Res. Nova", "propiedad": "Residencial Nova", "municipio": "San Nicolás", "fecha_venta": "20-Ene-23", "fecha_cobro": "24-Abr-23", "venta": "$2,700,000", "com_total": "$81,000", "com_asesor": "$64,800", "com_eq": "$16,200"},
    {"asesor": "Luis Morales", "contrato": "Modelo 1", "op": "Venta", "cliente": "Balcones", "propiedad": "Balcones de Anáhuac", "municipio": "San Nicolás", "fecha_venta": "09-Feb-23", "fecha_cobro": "—", "venta": "$1,650,000", "com_total": "$49,500", "com_asesor": "$29,700", "com_eq": "$19,800"},
    {"asesor": "Elizabeth Garza", "contrato": "Modelo 1", "op": "Renta", "cliente": "Roma Sur", "propiedad": "Colonia Roma Sur", "municipio": "Monterrey", "fecha_venta": "13-Feb-23", "fecha_cobro": "13-Feb-23", "venta": "$26,500", "com_total": "$13,250", "com_asesor": "$6,625", "com_eq": "$6,625"},
    {"asesor": "Asael Hernandez", "contrato": "Modelo 1", "op": "Venta", "cliente": "Dream Lagoons", "propiedad": "Dream Lagoons", "municipio": "Apodaca", "fecha_venta": "25-Feb-23", "fecha_cobro": "—", "venta": "$3,855,000", "com_total": "$115,650", "com_asesor": "$92,520", "com_eq": "$23,130"},
]
OBJETIVOS = [
    {"asesor": "Pamela Martinez", "meta": "$1,500,000", "avance": "$1,297,000", "pct": 86},
    {"asesor": "Samuel Higareda", "meta": "$800,000", "avance": "$293,000", "pct": 37},
    {"asesor": "Michelle Iracheta", "meta": "$700,000", "avance": "$421,000", "pct": 60},
    {"asesor": "Perla Cavazos", "meta": "$600,000", "avance": "$226,000", "pct": 38},
]


def libros(request):
    return render(request, "pages/libros.html", {
        "page_title": "Libros",
        "page_subtitle": "Registro maestro de comisiones y objetivos del equipo",
        "libro": LIBRO_COMISIONES,
        "objetivos": OBJETIVOS,
    })


# --- Team performance --------------------------------------------------------
TEAM_RESUMEN = [
    {"asesor": "Pamela Martinez", "avance": 86, "cierres": 7, "citas": 12, "senal": "Va arriba de meta; mantener ritmo"},
    {"asesor": "Michelle Iracheta", "avance": 60, "cierres": 4, "citas": 8, "senal": "Buen pipeline; empujar cierres"},
    {"asesor": "Samuel Higareda", "avance": 37, "cierres": 2, "citas": 5, "senal": "Bajo avance; asignar leads"},
    {"asesor": "Perla Cavazos", "avance": 38, "cierres": 3, "citas": 12, "senal": "Muchas citas, poca conversión"},
    {"asesor": "Raul Garcia", "avance": 42, "cierres": 2, "citas": 3, "senal": "Reforzar captaciones (1:1)"},
]


def team(request):
    return render(request, "pages/team.html", {
        "page_title": "Team performance",
        "page_subtitle": "Desempeño del equipo y foco de cada asesor",
        "resumen": TEAM_RESUMEN,
    })


# --- Conversaciones ----------------------------------------------------------
CONVERSACIONES = [
    {"id": 1, "nombre": "Laura Mendoza", "fuente": "WhatsApp", "ultimo": "¿Sigue disponible el depa de San Pedro?", "hora": "10:32", "grado": "A", "temp": "caliente", "no_leidos": 2},
    {"id": 2, "nombre": "Diego Salas", "fuente": "Meta Ads", "ultimo": "Me interesa agendar una visita", "hora": "09:14", "grado": "B", "temp": "tibio", "no_leidos": 0},
    {"id": 3, "nombre": "Carlos Reyna", "fuente": "EasyBroker", "ultimo": "¿Aceptan crédito Infonavit?", "hora": "Ayer", "grado": "A", "temp": "caliente", "no_leidos": 1},
    {"id": 4, "nombre": "Paola Cantú", "fuente": "Referido", "ultimo": "Gracias, lo pienso y te aviso", "hora": "Ayer", "grado": "C", "temp": "frio", "no_leidos": 0},
]
HILO = [
    {"de": "lead", "texto": "Hola, vi el departamento de San Pedro de 20 mdp. ¿Sigue disponible?", "hora": "10:30"},
    {"de": "asesor", "texto": "¡Hola Laura! Sí, sigue disponible. ¿Te gustaría agendar una visita esta semana?", "hora": "10:31"},
    {"de": "lead", "texto": "Sí, me interesa. ¿Qué días tienes?", "hora": "10:32"},
]


def conversaciones(request):
    return render(request, "pages/conversaciones.html", {
        "page_title": "Conversaciones",
        "page_subtitle": "Bandeja unificada — la IA sugiere, tú apruebas",
        "chats": CONVERSACIONES,
        "hilo": HILO,
        "sugerencia": "Tengo jueves 5 pm y viernes 11 am disponibles. ¿Cuál te acomoda mejor para ver el departamento?",
        "confianza": 92,
    })


# --- Agentes IA --------------------------------------------------------------
AGENTES = [
    {"key": "listing", "nombre": "Listing Manager", "desc": "Capta y gestiona los listings; muestra el proceso completo y dónde entra el humano.", "estado": "Activo", "autonomia": "Con aprobación",
     "reglas": [("Autonomía", "Con aprobación"), ("Publica solo con visto bueno", "Sí"), ("Fuentes", "EasyBroker")],
     "actividad": ["3 listings nuevos hoy", "1 esperando aprobación", "12 activos"]},
    {"key": "calificador", "nombre": "Calificador", "desc": "Toma señales y asigna calificación (A/B/C) y temperatura; registra recalificaciones.", "estado": "Activo", "autonomia": "Autónomo",
     "reglas": [("Autonomía", "Autónomo"), ("Marco", "BANT"), ("Recalifica cada", "24 h")],
     "actividad": ["18 leads calificados hoy", "5 subieron a caliente", "2 recalificados a A"]},
    {"key": "love", "nombre": "Love Bomber", "desc": "Nutre a los leads calientes (límite diario, solo-hot) y empuja a agendar cita.", "estado": "Activo", "autonomia": "Con aprobación",
     "reglas": [("Autonomía", "Con aprobación"), ("Solo leads", "Calientes"), ("Límite diario", "3 mensajes")],
     "actividad": ["9 mensajes enviados hoy", "4 empujados a cita", "1 pendiente de aprobar"]},
    {"key": "scheduler", "nombre": "Scheduler", "desc": "Agenda citas con el asesor y el calendario, y confirma.", "estado": "Activo", "autonomia": "Con aprobación",
     "reglas": [("Autonomía", "Con aprobación"), ("Calendario", "Google"), ("Confirma", "24 h antes")],
     "actividad": ["6 citas agendadas hoy", "12 confirmadas esta semana"]},
    {"key": "reminder", "nombre": "Reminder", "desc": "Tablero de confirmaciones y recordatorios.", "estado": "Activo", "autonomia": "Autónomo",
     "reglas": [("Autonomía", "Autónomo"), ("Recordatorio", "1 día y 1 h antes")],
     "actividad": ["22 recordatorios enviados hoy", "3 sin confirmar"]},
    {"key": "inventario", "nombre": "Inventario Easy Broker", "desc": "Propiedades disponibles con su % de match contra lo que busca el lead.", "estado": "Activo", "autonomia": "Autónomo",
     "reglas": [("Autonomía", "Autónomo"), ("Match mínimo", "70%"), ("Fuente", "EasyBroker")],
     "actividad": ["38 propiedades sincronizadas", "14 con match > 85%"]},
    {"key": "integraciones", "nombre": "Integraciones", "desc": "Conectores con las fuentes (WhatsApp, Meta, EasyBroker, Inmuebles24) y bitácora de sincronizaciones.", "estado": "Parcial", "autonomia": "—",
     "reglas": [("WhatsApp", "Conectado"), ("Inmuebles24", "Parcial"), ("Calendario", "Desconectado")],
     "actividad": ["4 fuentes activas", "Última sync hace 2 min"]},
    {"key": "reglas", "nombre": "Reglas", "desc": "Diales de autonomía: hasta dónde puede actuar sola la IA y qué requiere aprobación.", "estado": "—", "autonomia": "Config",
     "reglas": [("Umbral de aprobación", "Comisión > $50k"), ("Horario de envíos", "9:00–20:00")],
     "actividad": ["Config global de autonomía", "Aplica a todos los agentes"]},
]
API_KEYS = [
    {"nombre": "Anthropic (Claude)", "uso": "Respuestas sugeridas y calificación", "mask": "sk-ant-••••••••3f9a", "estado": "Activa"},
    {"nombre": "WhatsApp Cloud API", "uso": "Envío/recepción de mensajes", "mask": "EAAG••••••••7c21", "estado": "Activa"},
    {"nombre": "EasyBroker API", "uso": "Inventario de propiedades", "mask": "eb_••••••••b8", "estado": "Activa"},
]


def agentes(request):
    return render(request, "pages/agentes.html", {
        "page_title": "Agentes IA",
        "page_subtitle": "El motor de la operación — la IA propone, el humano decide",
        "agentes": AGENTES,
        "api_keys": API_KEYS,
        "es_admin": True,  # placeholder: la pestaña API Keys se gatea a Administrador+ con la capa de permisos
    })


# --- Asesores ----------------------------------------------------------------
ASESORES = [
    {"nombre": "Pamela Martinez", "pipeline": 12, "vendido": "$1.3M", "pct": 86, "contrato": "Modelo 1"},
    {"nombre": "Michelle Iracheta", "pipeline": 8, "vendido": "$421k", "pct": 60, "contrato": "Modelo 2"},
    {"nombre": "Samuel Higareda", "pipeline": 6, "vendido": "$293k", "pct": 37, "contrato": "Modelo 2"},
    {"nombre": "Perla Cavazos", "pipeline": 10, "vendido": "$226k", "pct": 38, "contrato": "Modelo 1"},
    {"nombre": "Raul Garcia Gzz", "pipeline": 4, "vendido": "$167k", "pct": 42, "contrato": "Modelo 1"},
    {"nombre": "Diego Cervantes", "pipeline": 9, "vendido": "$326k", "pct": 54, "contrato": "Modelo 2"},
]


def asesores(request):
    return render(request, "pages/asesores.html", {
        "page_title": "Asesores",
        "page_subtitle": "Directorio del equipo — pipeline, vendido y avance de meta",
        "asesores": ASESORES,
    })


# --- Muro de comentarios (interno) -------------------------------------------
MURO = [
    {"autor": "A. Ríos", "op": "Laura Mendoza · Depto San Pedro", "texto": "Ya confirmó visita para el jueves 5 pm. Preparar 2 opciones más de respaldo.", "hora": "hace 20 min"},
    {"autor": "M. Luna", "op": "Familia Treviño · Valle Alto", "texto": "Piden bajar 5% el precio; hablé con el propietario, lo revisa hoy.", "hora": "hace 1 h"},
    {"autor": "Coordinador", "op": "Diego Cervantes", "texto": "Asignen 2 clientes de venta a Diego, viene llegando pipeline nuevo.", "hora": "hace 3 h"},
    {"autor": "J. Vega", "op": "Paola Cantú · Carza", "texto": "Lead frío, mejor pasar a Reactivación y que Love Bomber la nutra.", "hora": "ayer"},
]


def muro(request):
    return render(request, "pages/muro.html", {
        "page_title": "Muro de comentarios",
        "page_subtitle": "Comentarios internos del equipo sobre las operaciones",
        "muro": MURO,
    })


# --- Leads Inmuebles24 (externo, del scraper) --------------------------------
LEADS_I24 = [
    {"nombre": "Yolanda Bortoni", "busca": "Casa venta", "zona": "Vista Hermosa", "presupuesto": "$4.5M", "mensaje": "Me interesa la casa publicada, ¿sigue disponible?", "fecha": "29-Jun", "status": "nuevo"},
    {"nombre": "Changjun Lee", "busca": "Depto renta", "zona": "Mizza", "presupuesto": "$32k/mes", "mensaje": "¿Aceptan mascotas? Busco para agosto.", "fecha": "29-Jun", "status": "nuevo"},
    {"nombre": "Rodrigo Garza", "busca": "Casa venta", "zona": "Lagos del Bosque", "presupuesto": "$6M", "mensaje": "Quisiera agendar visita este fin de semana.", "fecha": "28-Jun", "status": "importado"},
    {"nombre": "Alicia Quiroga", "busca": "Depto venta", "zona": "Villa Las Fuentes", "presupuesto": "$2.2M", "mensaje": "¿Cuánto de enganche piden?", "fecha": "28-Jun", "status": "importado"},
]


def leads_inmuebles(request):
    return render(request, "pages/leads_inmuebles.html", {
        "page_title": "Leads Inmuebles24",
        "page_subtitle": "Leads externos del panel de Inmuebles24 — extraer e importar al CRM",
        "leads": LEADS_I24,
        "ultimo_pull": "29-Jun 08:15",
    })


# --- Integraciones -----------------------------------------------------------
INTEGRACIONES = [
    {"nombre": "WhatsApp Business", "tipo": "Mensajería", "estado": "Conectado", "sync": "hace 2 min"},
    {"nombre": "Meta Ads (Facebook/IG)", "tipo": "Fuente de leads", "estado": "Conectado", "sync": "hace 15 min"},
    {"nombre": "EasyBroker", "tipo": "Inventario", "estado": "Conectado", "sync": "hace 1 h"},
    {"nombre": "Inmuebles24", "tipo": "Fuente de leads", "estado": "Parcial", "sync": "hace 6 h"},
    {"nombre": "Calendario (Google)", "tipo": "Agenda", "estado": "Desconectado", "sync": "—"},
]
BITACORA = [
    {"fuente": "WhatsApp Business", "detalle": "12 mensajes nuevos sincronizados", "hora": "08:20"},
    {"fuente": "Inmuebles24", "detalle": "4 leads extraídos (fallback a Excel)", "hora": "08:15"},
    {"fuente": "EasyBroker", "detalle": "38 propiedades actualizadas", "hora": "07:40"},
]


def integraciones(request):
    return render(request, "pages/integraciones.html", {
        "page_title": "Integraciones",
        "page_subtitle": "Conectores con las fuentes y bitácora de sincronizaciones",
        "integraciones": INTEGRACIONES,
        "bitacora": BITACORA,
    })


def configuracion(request):
    return render(request, "pages/configuracion.html", {
        "page_title": "Configuración",
        "page_subtitle": "Ajustes generales de la agencia",
    })


def placeholder(request, title="Hoja"):
    return render(request, "pages/placeholder.html", {
        "page_title": title,
        "page_subtitle": "En construcción — llega en su fase del BUILD_PLAN",
    })
