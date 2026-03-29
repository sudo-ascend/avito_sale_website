import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Вызывает внутренние API-эндпоинты проверки DNS и отправки уведомлений."

    def add_arguments(self, parser):
        parser.add_argument("--base-url", default=settings.APP_BASE_URL)
        parser.add_argument("--token", default=settings.INTERNAL_API_TOKEN)

    def handle(self, *args, **options):
        base_url = options["base_url"].rstrip("/")
        token = options["token"]
        headers = {"X-Internal-Api-Key": token}
        endpoints = [
            ("DNS", f"{base_url}/dashboard/dns/api/internal/dns-check/"),
            ("Напоминания", f"{base_url}/dashboard/notifications/api/internal/notifications/run/"),
        ]

        for label, url in endpoints:
            try:
                response = requests.post(url, headers=headers, timeout=60)
                response.raise_for_status()
            except requests.RequestException as exc:
                raise CommandError(f"{label}: не удалось выполнить запрос к {url}: {exc}") from exc

            self.stdout.write(self.style.SUCCESS(f"{label}: {response.json()}"))
