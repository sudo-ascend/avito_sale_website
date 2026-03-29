from django.core.management.base import BaseCommand

from notifications.services import send_expiry_notifications, send_hosting_income_notifications


class Command(BaseCommand):
    help = "Отправляет напоминания по срокам и ежемесячным поступлениям от хостинга."

    def handle(self, *args, **options):
        result = {
            "expiry": send_expiry_notifications(),
            "hosting_income": send_hosting_income_notifications(),
        }
        self.stdout.write(self.style.SUCCESS(str(result)))
