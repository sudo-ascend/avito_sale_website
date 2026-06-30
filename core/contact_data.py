from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError

from .models import SiteContent


def get_fallback_contact():
    return SiteContent(
        company_name=settings.SITE_BRAND_NAME,
        company_tagline="Сайты с понятной админкой и поддержкой после запуска",
        email="grachevilia09@yandex.ru",
        phone="79167950225",
        primary_manager_name="Илья",
        secondary_manager_name="Алексей",
        secondary_manager_phone="+79261879852",
        footer_description="Разрабатываем сайты с удобной админкой, понятной структурой и поддержкой после запуска.",
        home_case_kicker="Опыт с админкой",
        home_case_title="Aquaklon.ru: сайт, которым владелец управляет сам",
        home_case_body=(
            "На сайте Aquaklon реализована удобная админ-панель на Django, которая позволяет "
            "владельцу самостоятельно управлять контентом без программиста."
        ),
        process_step_1_body="Собираем вводные, структуру сайта, блоки и пожелания по стилю, чтобы на старте зафиксировать задачу без потерь.",
        process_step_2_body="Показываем рабочий макет и собираем страницы так, чтобы ими можно было пользоваться сразу после запуска.",
        process_step_3_body="Доводим тексты, изображения, каталог и другие блоки до финального состояния перед публикацией.",
        process_step_4_body="Подключаем домен, хостинг, почтовые формы и передаём сайт с удобной админкой для дальнейшей работы.",
        process_highlight_body="Оставляем только то, что нужно клиенту: публичные страницы, портфолио, заявки и удобное администрирование.",
        contact_page_cta_body="Чтобы не терять детали на старте, мы просим клиентов заполнять бриф. Так проект быстрее переходит в оценку и разработку.",
    )


def get_primary_contact():
    try:
        content = SiteContent.objects.first()
    except (OperationalError, ProgrammingError):
        content = None
    return content or get_fallback_contact()
