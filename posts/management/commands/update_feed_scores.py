from django.core.management.base import BaseCommand
from posts.feed_algorithm import actualizar_pesos_masivos

class Command(BaseCommand):
    help = 'Actualiza los pesos de todos los posts para el feed algorítmico'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Actualizando pesos de posts...'))
        total = actualizar_pesos_masivos()
        self.stdout.write(self.style.SUCCESS(f'Pesos actualizados para {total} posts'))