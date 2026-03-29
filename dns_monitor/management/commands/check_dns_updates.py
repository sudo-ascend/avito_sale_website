from django.core.management.base import BaseCommand

from dns_monitor.services import run_dns_checks


class Command(BaseCommand):
    help = "Проверяет DNS-обновления для активных проектов."

    def handle(self, *args, **options):
        result = run_dns_checks()
        self.stdout.write(self.style.SUCCESS(str(result)))
