from django.core.management.base import BaseCommand
from backend.PartnerYAMLImporter import PartnerYAMLImporter


class Command(BaseCommand):
    help = 'Импортирует товары из shop.yaml'

    def handle(self, *args, **kwargs):
        importer = PartnerYAMLImporter()
        importer.run()  # предполагаем, что метод run() внутри делает всё
        self.stdout.write(self.style.SUCCESS('Импорт успешно завершён'))
