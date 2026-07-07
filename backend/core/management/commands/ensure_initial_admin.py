"""Crea un superusuario inicial desde variables de entorno, si no existe.

Se corre en cada arranque (idempotente). Lee:
  INITIAL_ADMIN_USERNAME (default 'admin')
  INITIAL_ADMIN_EMAIL
  INITIAL_ADMIN_PASSWORD

Si faltan email o password, no hace nada. Si el usuario ya existe, no lo toca.
Tras el primer login, borra estas variables del entorno (la contraseña ya quedó
hasheada en la base).
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea un superusuario inicial desde INITIAL_ADMIN_* si no existe."

    def handle(self, *args, **options):
        email = os.environ.get("INITIAL_ADMIN_EMAIL", "").strip()
        password = os.environ.get("INITIAL_ADMIN_PASSWORD", "").strip()
        username = os.environ.get("INITIAL_ADMIN_USERNAME", "admin").strip()

        if not email or not password:
            self.stdout.write("INITIAL_ADMIN_* incompletas; no se crea admin.")
            return

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(f'El usuario "{username}" ya existe; sin cambios.')
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Superusuario "{username}" creado.'))
