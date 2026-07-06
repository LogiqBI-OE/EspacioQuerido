"""Modelo de datos del Libro de comisiones (Fase libro).

Diseño normalizado a partir del Excel real:
- Geografía jerárquica: Estado -> Municipio -> Zona -> Colonia (municipio se deriva
  de la zona; la calle es texto libre en Propiedad).
- Catálogos editables.
- TarifaReparto: %s de reparto por beneficiario/contrato, versionados por vigencia
  (la "bitácora de fechas"); la tarifa que aplica es la vigente a la fecha de cierre.
- Operacion es el hecho central; Participacion es el snapshot del reparto.
"""

from django.db import models


# ---------------------------------------------------------------- Geografía ---
class Estado(models.Model):
    nombre = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Municipio(models.Model):
    nombre = models.CharField(max_length=120)
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT, related_name="municipios")

    class Meta:
        ordering = ["nombre"]
        unique_together = ("nombre", "estado")

    def __str__(self):
        return self.nombre


class Zona(models.Model):
    nombre = models.CharField(max_length=120)
    municipio = models.ForeignKey(Municipio, on_delete=models.PROTECT, related_name="zonas")

    class Meta:
        ordering = ["nombre"]
        unique_together = ("nombre", "municipio")

    def __str__(self):
        return f"{self.nombre} ({self.municipio})"


class Colonia(models.Model):
    """Catálogo agregable al vuelo (se crea si no existe al capturar propiedad)."""
    nombre = models.CharField(max_length=160)
    zona = models.ForeignKey(Zona, on_delete=models.PROTECT, related_name="colonias")

    class Meta:
        ordering = ["nombre"]
        unique_together = ("nombre", "zona")

    def __str__(self):
        return self.nombre


# ---------------------------------------------------------------- Catálogos ---
class _Catalogo(models.Model):
    nombre = models.CharField(max_length=80, unique=True)

    class Meta:
        abstract = True
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class TipoPropiedad(_Catalogo):
    pass


class MetodoPago(_Catalogo):
    pass


class ContratoModelo(_Catalogo):
    """Modelo 1 / Modelo 2. El % del asesor se define en TarifaReparto por modelo."""
    pass


class TipoOperacion(_Catalogo):
    """Venta / Renta."""
    pass


class StatusCierre(_Catalogo):
    """Cerrado / Separación / Ofrecimiento / Dead."""
    pass


class StatusPago(_Catalogo):
    """Facturado / Por cobrar / Sin status."""
    pass


# ---------------------------------------------- Reparto (tarifas versionadas) --
class TarifaReparto(models.Model):
    """% de reparto por beneficiario, con vigencia (bitácora de fechas).

    - Para el asesor, el % depende del ContratoModelo.
    - Para coordinador y coordinador_leads son inputs de la agencia.
    - EQ (Espacio Querido) recibe el resto; no lleva tarifa.
    La tarifa aplicable a una operación es la vigente a su fecha de cierre.
    """
    ASESOR = "asesor"
    COORDINADOR = "coordinador"
    COORDINADOR_LEADS = "coordinador_leads"
    BENEFICIARIO = [
        (ASESOR, "Asesor"),
        (COORDINADOR, "Coordinador"),
        (COORDINADOR_LEADS, "Coordinadora de leads"),
    ]

    beneficiario_tipo = models.CharField(max_length=20, choices=BENEFICIARIO)
    contrato_modelo = models.ForeignKey(
        ContratoModelo, on_delete=models.PROTECT, null=True, blank=True,
        related_name="tarifas", help_text="Solo aplica al beneficiario 'asesor'.",
    )
    pct = models.DecimalField(max_digits=6, decimal_places=4, help_text="Fracción sobre la comisión total (ej. 0.60).")
    vigencia_inicio = models.DateField()
    vigencia_fin = models.DateField(null=True, blank=True, help_text="Vacío = vigente.")

    class Meta:
        ordering = ["beneficiario_tipo", "-vigencia_inicio"]

    def __str__(self):
        return f"{self.get_beneficiario_tipo_display()} {self.pct} desde {self.vigencia_inicio}"


# --------------------------------------------------------------------- Núcleo --
class Asesor(models.Model):
    nombre = models.CharField(max_length=160)
    activo = models.BooleanField(default=True)
    # cada gestor tiene un coordinador (team leader), que también es Asesor.
    coordinador = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="equipo",
    )

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    nombre = models.CharField(max_length=200)
    comentario = models.TextField(blank=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Propiedad(models.Model):
    tipo = models.ForeignKey(TipoPropiedad, on_delete=models.PROTECT, null=True, blank=True, related_name="propiedades")
    nombre = models.CharField(max_length=200, blank=True)
    colonia = models.ForeignKey(Colonia, on_delete=models.PROTECT, null=True, blank=True, related_name="propiedades")
    calle = models.CharField(max_length=200, blank=True, help_text="Calle y número exterior (texto libre).")
    numero_interior = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.nombre or f"Propiedad #{self.pk}"


class Operacion(models.Model):
    external_id = models.IntegerField(null=True, blank=True, db_index=True, help_text="ID original del Excel.")
    asesor = models.ForeignKey(Asesor, on_delete=models.PROTECT, related_name="operaciones")
    coordinador_leads = models.ForeignKey(
        Asesor, on_delete=models.SET_NULL, null=True, blank=True, related_name="operaciones_leads",
    )
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name="operaciones")
    propiedad = models.ForeignKey(Propiedad, on_delete=models.SET_NULL, null=True, blank=True, related_name="operaciones")
    contrato_modelo = models.ForeignKey(ContratoModelo, on_delete=models.SET_NULL, null=True, blank=True)

    tipo_operacion = models.ForeignKey(TipoOperacion, on_delete=models.PROTECT, null=True, blank=True)
    status_cierre = models.ForeignKey(StatusCierre, on_delete=models.PROTECT, null=True, blank=True)
    status_pago = models.ForeignKey(StatusPago, on_delete=models.PROTECT, null=True, blank=True)

    facturacion = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    pct_comision = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    comision_total = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    portafolio = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)

    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_separacion = models.DateField(null=True, blank=True)
    fecha_cobro = models.DateField(null=True, blank=True)
    flag_semanal = models.BooleanField(default=False)
    comentarios = models.TextField(blank=True)

    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_cobro", "-id"]

    def __str__(self):
        return f"Op #{self.external_id or self.pk} · {self.asesor}"


class Participacion(models.Model):
    """Snapshot del reparto: se congela al cerrar con la tarifa vigente."""
    operacion = models.ForeignKey(Operacion, on_delete=models.CASCADE, related_name="participaciones")
    beneficiario_tipo = models.CharField(max_length=20, choices=TarifaReparto.BENEFICIARIO + [("eq", "Espacio Querido")])
    asesor = models.ForeignKey(Asesor, on_delete=models.SET_NULL, null=True, blank=True, related_name="participaciones")
    tarifa = models.ForeignKey(TarifaReparto, on_delete=models.SET_NULL, null=True, blank=True)
    pct_aplicado = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    monto = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    pagado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_beneficiario_tipo_display()} · {self.monto}"


class EtapaEvento(models.Model):
    """Bitácora de cambios de etapa (nuevo; arranca en el CRM)."""
    operacion = models.ForeignKey(Operacion, on_delete=models.CASCADE, related_name="eventos")
    etapa = models.CharField(max_length=40)
    timestamp = models.DateTimeField()
    usuario = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.operacion} -> {self.etapa} @ {self.timestamp}"
