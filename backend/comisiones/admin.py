from django.contrib import admin

from . import models

# Catálogos simples
for _m in (models.Estado, models.Municipio, models.Zona, models.Colonia,
           models.TipoPropiedad, models.MetodoPago, models.ContratoModelo,
           models.TipoOperacion, models.StatusCierre, models.StatusPago):
    admin.site.register(_m)


@admin.register(models.TarifaReparto)
class TarifaRepartoAdmin(admin.ModelAdmin):
    list_display = ("beneficiario_tipo", "contrato_modelo", "pct", "vigencia_inicio", "vigencia_fin")
    list_filter = ("beneficiario_tipo",)


@admin.register(models.Asesor)
class AsesorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo", "coordinador")
    search_fields = ("nombre",)


@admin.register(models.Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(models.Propiedad)
class PropiedadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "colonia")
    search_fields = ("nombre",)


class ParticipacionInline(admin.TabularInline):
    model = models.Participacion
    extra = 0


@admin.register(models.Operacion)
class OperacionAdmin(admin.ModelAdmin):
    list_display = ("external_id", "asesor", "tipo_operacion", "status_cierre",
                    "status_pago", "comision_total", "fecha_cobro")
    list_filter = ("tipo_operacion", "status_cierre", "status_pago")
    search_fields = ("external_id", "asesor__nombre", "cliente__nombre")
    inlines = [ParticipacionInline]
