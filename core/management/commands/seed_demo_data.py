from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounting.models import AccountingEntry
from briefs.models import BriefRequest
from core.models import ContactInfo, Service
from crm.models import Client, Order
from dns_monitor.models import DNSMonitorTarget
from notifications.models import ReminderRule
from portfolio.models import Project, Technology


class Command(BaseCommand):
    help = "Заполняет проект тестовыми данными."

    def add_arguments(self, parser):
        parser.add_argument(
            "--create-manager",
            action="store_true",
            help="Создать тестового менеджера manager / Manager12345!",
        )

    def handle(self, *args, **options):
        today = timezone.localdate()

        ContactInfo.objects.update_or_create(
            email="grachevilia09@yandex.ru",
            defaults={
                "company_name": "Grachev Studio",
                "tagline": "Сайты, CRM и сопровождение цифровых продуктов",
                "phone": "79167950225",
                "telegram": "@grachevstudio",
                "address": "Москва, удаленная команда",
                "working_hours": "Пн-Пт, 10:00-19:00",
                "is_primary": True,
            },
        )

        services = [
            ("Разработка сайтов", "site-build", "bi-window-stack", "Лендинги, корпоративные сайты и каталоги."),
            ("Внутренние кабинеты", "private-office", "bi-speedometer2", "CRM, личные кабинеты и рабочие панели."),
            ("Поддержка и сопровождение", "support", "bi-shield-check", "Домены, серверы, оплаты, DNS и развитие проекта."),
        ]
        for index, (title, slug, icon, description) in enumerate(services, start=1):
            Service.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "icon": icon,
                    "short_description": description,
                    "description": description,
                    "order": index,
                    "is_active": True,
                },
            )

        technologies = []
        for name in ["Django", "Bootstrap 5", "JavaScript", "PostgreSQL", "Docker"]:
            tech, _ = Technology.objects.get_or_create(name=name)
            technologies.append(tech)

        project_1, _ = Project.objects.update_or_create(
            slug="autoparts-catalog",
            defaults={
                "title": "AutoParts Catalog",
                "short_description": "Каталог автозапчастей с фильтрами и заявками.",
                "description": "Корпоративный сайт с каталогом, формами заявок и базовой CRM для отдела продаж.",
                "completion_date": today - timedelta(days=120),
                "stack_notes": "Django, Bootstrap 5, SQLite",
                "color_palette": "#14344c, #c96f3b, #f4f1ea, #2b506b",
                "external_url": "",
                "is_featured": True,
                "is_published": True,
            },
        )
        project_1.technologies.set(technologies[:3])

        project_2, _ = Project.objects.update_or_create(
            slug="clinic-booking",
            defaults={
                "title": "Clinic Booking",
                "short_description": "Сайт клиники с онлайн-записью и услугами.",
                "description": "Многостраничный медицинский сайт с личными сценариями, расписанием и автоматизацией заявок.",
                "completion_date": today - timedelta(days=60),
                "stack_notes": "Django, Bootstrap 5, JavaScript",
                "color_palette": "#0f4c5c, #1b9aaa, #edf6f9, #ff7d00",
                "external_url": "",
                "is_featured": True,
                "is_published": True,
            },
        )
        project_2.technologies.set(technologies[:3])

        brief, _ = BriefRequest.objects.update_or_create(
            business_name="Nova Trade",
            defaults={
                "client_type": BriefRequest.ClientType.LEGAL_ENTITY,
                "site_type": BriefRequest.SiteType.CATALOG,
                "contact_phone": "+7 (900) 111-22-33",
                "preferred_contact_app": BriefRequest.ContactApp.WHATSAPP,
                "contact_email": "client@example.com",
                "work_region": "Москва и Московская область",
                "color_mode": BriefRequest.ColorMode.TEMPLATE,
                "color_template_name": "AutoParts Catalog",
                "color_preference": "#c96f3b",
                "color_accent": "#14344c",
                "color_background": "#f4f1ea",
                "color_extra": "#2b506b",
                "reference_sites": "https://example-site-1.ru\nhttps://example-site-2.ru",
                "need_hosting": True,
                "need_domain": True,
                "estimated_price": Decimal("13300"),
                "privacy_accepted": True,
                "status": BriefRequest.Status.NEW,
            },
        )

        client_1, _ = Client.objects.update_or_create(
            company_name="Nova Trade",
            defaults={
                "name": "Илья Новиков",
                "email": "client@example.com",
                "phone": "+7 (900) 111-22-33",
                "telegram": "@nova_trade",
                "website": "https://novatrade.example",
                "notes": "Основной клиент по корпоративному сайту.",
                "status": Client.Status.IN_PROGRESS,
            },
        )

        client_2, _ = Client.objects.update_or_create(
            company_name="MedCare Plus",
            defaults={
                "name": "Мария Сергеева",
                "email": "medcare@example.com",
                "phone": "+7 (900) 555-11-77",
                "telegram": "@medcare_plus",
                "website": "https://medcare.example",
                "notes": "Проект на поддержке.",
                "status": Client.Status.DNS_PENDING,
            },
        )

        order_1, _ = Order.objects.update_or_create(
            slug="nova-corporate-site",
            defaults={
                "client": client_1,
                "brief": brief,
                "title": "Nova Corporate Site",
                "description": "Разработка корпоративного сайта и настройка инфраструктуры.",
                "status": Order.Status.IN_PROGRESS,
                "start_date": today - timedelta(days=10),
                "subscription_term_months": 12,
                "subscription_end_date": today + timedelta(days=28),
                "domain": "example.com",
                "domain_expiration_date": today + timedelta(days=14),
                "server_ip": "127.0.0.1",
                "server_username": "deploy",
                "server_expiration_date": today + timedelta(days=30),
                "payment_status": Order.PaymentStatus.PARTIAL,
                "next_payment_date": today + timedelta(days=5),
                "price": Decimal("180000"),
                "comments": "Ждем финальный контент от клиента.",
            },
        )
        order_1.set_server_password("StrongDemoPassword123!")
        order_1.save()

        order_2, _ = Order.objects.update_or_create(
            slug="medcare-support",
            defaults={
                "client": client_2,
                "title": "MedCare Support",
                "description": "Поддержка сайта клиники и продление инфраструктуры.",
                "status": Order.Status.IN_PROGRESS,
                "start_date": today - timedelta(days=180),
                "end_date": today - timedelta(days=5),
                "subscription_term_months": 12,
                "subscription_end_date": today + timedelta(days=7),
                "domain": "iana.org",
                "domain_expiration_date": today + timedelta(days=3),
                "server_ip": "127.0.0.2",
                "server_username": "root",
                "server_expiration_date": today + timedelta(days=10),
                "payment_status": Order.PaymentStatus.OVERDUE,
                "next_payment_date": today - timedelta(days=2),
                "price": Decimal("45000"),
                "comments": "Нужно напомнить клиенту об оплате и продлении.",
            },
        )
        order_2.set_server_password("SupportDemoPassword123!")
        order_2.save()

        AccountingEntry.objects.update_or_create(
            date=today - timedelta(days=3),
            category="Оплата проекта",
            amount=Decimal("90000"),
            defaults={
                "operation_type": AccountingEntry.OperationType.INCOME,
                "client": client_1,
                "order": order_1,
                "comment": "Предоплата по проекту Nova Corporate Site.",
            },
        )
        AccountingEntry.objects.update_or_create(
            date=today - timedelta(days=1),
            category="Хостинг и сервисы",
            amount=Decimal("12000"),
            defaults={
                "operation_type": AccountingEntry.OperationType.EXPENSE,
                "client": client_2,
                "order": order_2,
                "comment": "Продление сервисов и администрирование.",
            },
        )

        DNSMonitorTarget.objects.update_or_create(
            order=order_1,
            defaults={
                "domain": order_1.domain,
                "record_type": DNSMonitorTarget.RecordType.A,
                "expected_value": order_1.server_ip,
                "is_active": True,
            },
        )
        DNSMonitorTarget.objects.update_or_create(
            order=order_2,
            defaults={
                "domain": order_2.domain,
                "record_type": DNSMonitorTarget.RecordType.A,
                "expected_value": order_2.server_ip,
                "is_active": True,
            },
        )

        for days_before in [30, 14, 7, 3, 1]:
            ReminderRule.objects.update_or_create(
                days_before=days_before,
                defaults={"name": f"Напомнить за {days_before} дн.", "is_active": True},
            )

        if options["create_manager"]:
            User = get_user_model()
            user, created = User.objects.get_or_create(
                username="manager",
                defaults={
                    "email": "manager@example.com",
                    "is_staff": True,
                },
            )
            if created:
                user.set_password("Manager12345!")
                user.save()
                self.stdout.write(
                    self.style.WARNING("Создан тестовый менеджер: manager / Manager12345!")
                )

        self.stdout.write(self.style.SUCCESS("Тестовые данные успешно загружены."))
