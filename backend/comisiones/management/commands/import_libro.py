"""Importa (limpiando) el Libro de comisiones desde el Excel a la base.

Uso: python manage.py import_libro [--file data/Libro de comisiones.xlsx]

- Normaliza catálogos (trim, colapso de espacios, casing) con get_or_create cacheado.
- Convierte fechas serial de Excel; las inválidas quedan en null.
- Reconstruye el reparto (Participacion) desde los montos reales del Excel
  (asesor / EQ / coordinador), preservando el histórico.
- Es idempotente: borra los datos previos de comisiones antes de cargar.
"""

import datetime
from decimal import Decimal, InvalidOperation

import openpyxl
from django.core.management.base import BaseCommand
from django.db import transaction

from comisiones import models as m

EXCEL_EPOCH = datetime.datetime(1899, 12, 30)


def norm(v):
    if v is None:
        return ""
    return " ".join(str(v).split()).strip()


def to_decimal(v):
    if v is None or isinstance(v, str) and not v.strip():
        return None
    try:
        return Decimal(str(v))
    except (InvalidOperation, ValueError):
        return None


def serial_to_date(v):
    if isinstance(v, datetime.datetime):
        return v.date()
    if isinstance(v, (int, float)) and 30000 < v < 60000:
        return (EXCEL_EPOCH + datetime.timedelta(days=int(v))).date()
    return None


def norm_metodo(v):
    s = norm(v).lower()
    if not s:
        return ""
    rp = "rp" in s
    cred = "cred" in s
    if rp and cred:
        return "RP + Crédito"
    if rp:
        return "RP"
    if cred:
        return "Crédito"
    if "contado" in s:
        return "Contado"
    return norm(v).title()


class Command(BaseCommand):
    help = "Importa el Libro de comisiones desde el Excel."

    def add_arguments(self, parser):
        parser.add_argument("--file", default="data/Libro de comisiones.xlsx")

    @transaction.atomic
    def handle(self, *args, **opts):
        path = opts["file"]
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb["Sheet1"]
        rows = [r for r in ws.iter_rows(values_only=True)][2:]
        rows = [r for r in rows if r[0] is not None]
        self.stdout.write(f"Filas a importar: {len(rows)}")

        # limpieza previa (idempotente)
        for Model in (m.Participacion, m.EtapaEvento, m.Operacion, m.Propiedad,
                      m.Cliente, m.Colonia, m.Zona, m.Municipio, m.Estado,
                      m.TipoPropiedad, m.MetodoPago, m.ContratoModelo, m.TipoOperacion,
                      m.StatusCierre, m.StatusPago, m.Asesor):
            Model.objects.all().delete()

        # cachés de get_or_create
        cache = {}

        def get(Model, key, **kw):
            ck = (Model.__name__, key)
            if ck not in cache:
                cache[ck] = Model.objects.get_or_create(**kw)[0]
            return cache[ck]

        estado_nl = m.Estado.objects.create(nombre="Nuevo León")

        def geo(municipio, zona, colonia):
            municipio = norm(municipio).title() or "Sin municipio"
            zona = norm(zona).title() or municipio  # zona faltante -> usa municipio
            mun = get(m.Municipio, ("mun", municipio),
                      nombre=municipio, estado=estado_nl)
            zn = get(m.Zona, ("zona", municipio, zona), nombre=zona, municipio=mun)
            colonia = norm(colonia).title()
            if not colonia:
                return None
            return get(m.Colonia, ("col", zona, municipio, colonia), nombre=colonia, zona=zn)

        creadas = 0
        for r in rows:
            asesor = m.Asesor.objects.get_or_create(nombre=norm(r[1]) or "Sin asesor")[0]

            contrato = None
            if norm(r[2]):
                contrato = get(m.ContratoModelo, ("cm", norm(r[2])), nombre=norm(r[2]))

            # tipo operación / dead
            op_raw = norm(r[11]).lower()
            tipo_op = None
            if "venta" in op_raw:
                tipo_op = get(m.TipoOperacion, ("to", "Venta"), nombre="Venta")
            elif "renta" in op_raw:
                tipo_op = get(m.TipoOperacion, ("to", "Renta"), nombre="Renta")

            sc_raw = norm(r[12])
            status_cierre = None
            if sc_raw:
                name = "Dead" if "dead" in sc_raw.lower() else sc_raw.title()
                status_cierre = get(m.StatusCierre, ("sc", name), nombre=name)

            sp_raw = norm(r[13])
            status_pago = None
            if sp_raw and "dead" not in sp_raw.lower():
                status_pago = get(m.StatusPago, ("sp", sp_raw.title()), nombre=sp_raw.title())

            tipo_prop = None
            if norm(r[23]):
                tp = norm(r[23]).title()
                tipo_prop = get(m.TipoPropiedad, ("tp", tp), nombre=tp)

            metodo = None
            if norm_metodo(r[31]):
                mp = norm_metodo(r[31])
                metodo = get(m.MetodoPago, ("mp", mp), nombre=mp)

            colonia = geo(r[25], r[26], r[27])
            propiedad = m.Propiedad.objects.create(
                tipo=tipo_prop, nombre=norm(r[24]), colonia=colonia,
                calle=norm(r[28]), numero_interior=norm(r[29]),
            )

            cliente = None
            if norm(r[30]):
                cliente = m.Cliente.objects.create(nombre=norm(r[30]), comentario=norm(r[33]))

            op = m.Operacion.objects.create(
                external_id=int(r[0]) if isinstance(r[0], (int, float)) else None,
                asesor=asesor, cliente=cliente, propiedad=propiedad, contrato_modelo=contrato,
                tipo_operacion=tipo_op, status_cierre=status_cierre, status_pago=status_pago,
                facturacion=to_decimal(r[14]), pct_comision=to_decimal(r[15]),
                comision_total=to_decimal(r[16]), portafolio=to_decimal(r[17]),
                metodo_pago=metodo,
                fecha_separacion=serial_to_date(r[3]), fecha_cobro=serial_to_date(r[6]),
                flag_semanal=bool(r[10]) if isinstance(r[10], (int, float)) else False,
                comentarios=norm(r[40]),
            )

            # reparto (snapshot desde los montos reales del Excel)
            parts = []
            if to_decimal(r[20]) is not None:
                parts.append(("asesor", asesor, to_decimal(r[19]), to_decimal(r[20]), False))
            if to_decimal(r[22]) is not None:
                parts.append(("eq", None, to_decimal(r[21]), to_decimal(r[22]), False))
            if to_decimal(r[37]) is not None:
                parts.append(("coordinador", None, None, to_decimal(r[37]), norm(r[34]).lower() == "si"))
            for tipo, ase, pct, monto, pagado in parts:
                m.Participacion.objects.create(
                    operacion=op, beneficiario_tipo=tipo, asesor=ase,
                    pct_aplicado=pct, monto=monto, pagado=pagado,
                )
            creadas += 1

        self.stdout.write(self.style.SUCCESS(f"OK: {creadas} operaciones importadas."))
