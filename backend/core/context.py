"""Context processor del shell: inyecta nav, iconos y datos de vista/footer.

Por ahora los datos de tenant/vista/developer son placeholders. Cuando llegue la
capa de tenancy (siguiente tramo de F0) esto leera el tenant/rol reales.
"""

from core import nav


def shell(request):
    return {
        "nav_groups": nav.NAV_OPERATIVA,
        "nav_icons": nav.ICONS,
        "views": nav.VIEWS,
        # placeholders de sesion/tenant/developer
        "brand": {"nombre": "Espacio Querido", "sigla": "EQ", "tenant": "MONTERREY1"},
        "developer_info": {"empresa": "LogiQ", "sigla": "L", "origen": "Monterrey, NL", "version": "1.2.0"},
        "usuario": {"nombre": "Orlando Elizondo", "iniciales": "OE"},
    }
