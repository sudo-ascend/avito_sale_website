from django.core.management.base import BaseCommand

from notifications.services import send_expiry_notifications


class Command(BaseCommand):
    help = "Отправляет email-напоминания по срокам подписок, доменов и серверов."

    def handle(self, *args, **options):
        result = send_expiry_notifications()
        self.stdout.write(self.style.SUCCESS(str(result)))
