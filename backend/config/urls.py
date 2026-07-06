from django.contrib import admin
from django.urls import path

from core import views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", views.leads, name="leads"),
    path("pipeline/", views.pipeline, name="pipeline"),
    path("muro/", views.muro, name="muro"),
    path("conversaciones/", views.conversaciones, name="conversaciones"),
    path("leads-inmuebles/", views.leads_inmuebles, name="leads_inmuebles"),
    path("integraciones/", views.integraciones, name="integraciones"),
    path("libros/", views.libros, name="libros"),
    path("ventas/", views.ventas, name="ventas"),
    path("team/", views.team, name="team"),
    path("agentes/", views.agentes, name="agentes"),
    path("junta-semanal/", views.junta_semanal, name="junta_semanal"),
    path("1a1/", views.uno_a_uno, name="uno_a_uno"),
    path("asesores/", views.asesores, name="asesores"),
    path("configuracion/", views.configuracion, name="configuracion"),
]
