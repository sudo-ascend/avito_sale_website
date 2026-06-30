from django.db import migrations, models


def create_default_site_content(apps, schema_editor):
    SiteContent = apps.get_model("core", "SiteContent")
    ContactInfo = apps.get_model("core", "ContactInfo")
    HomePageCaseSection = apps.get_model("core", "HomePageCaseSection")

    contact = ContactInfo.objects.filter(is_primary=True).first() or ContactInfo.objects.first()
    home_case = HomePageCaseSection.objects.filter(is_active=True).order_by("-updated_at").first()

    SiteContent.objects.get_or_create(
        pk=1,
        defaults={
            "company_name": getattr(contact, "company_name", "Grachev Studio"),
            "company_tagline": getattr(contact, "tagline", "Сайты с понятной админкой и поддержкой после запуска"),
            "email": getattr(contact, "email", "grachevilia09@yandex.ru"),
            "phone": getattr(contact, "phone", "79167950225"),
            "telegram": getattr(contact, "telegram", ""),
            "whatsapp": getattr(contact, "whatsapp", ""),
            "address": getattr(contact, "address", ""),
            "working_hours": getattr(contact, "working_hours", ""),
            "map_embed_url": getattr(contact, "map_embed_url", ""),
            "home_case_kicker": getattr(home_case, "kicker", "Опыт с админкой"),
            "home_case_title": getattr(home_case, "title", "Aquaklon.ru: сайт, которым владелец управляет сам"),
            "home_case_body": getattr(home_case, "body", "На сайте Aquaklon реализована удобная админ-панель на Django."),
            "home_case_image_primary": getattr(home_case, "image_primary", ""),
            "home_case_image_primary_alt": getattr(home_case, "image_primary_alt", ""),
            "home_case_image_secondary": getattr(home_case, "image_secondary", ""),
            "home_case_image_secondary_alt": getattr(home_case, "image_secondary_alt", ""),
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_homepagecasesection"),
    ]

    operations = [
        migrations.CreateModel(
            name="SiteContent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
                ("company_name", models.CharField(default="Grachev Studio", max_length=150, verbose_name="Название компании")),
                ("company_tagline", models.CharField(blank=True, max_length=255, verbose_name="Подзаголовок компании")),
                ("email", models.EmailField(default="grachevilia09@yandex.ru", max_length=254, verbose_name="Email")),
                ("phone", models.CharField(default="79167950225", max_length=50, verbose_name="Телефон")),
                ("telegram", models.CharField(blank=True, max_length=100, verbose_name="Telegram")),
                ("whatsapp", models.CharField(blank=True, max_length=100, verbose_name="WhatsApp")),
                ("address", models.CharField(blank=True, max_length=255, verbose_name="Адрес")),
                ("working_hours", models.CharField(blank=True, max_length=150, verbose_name="Время работы")),
                ("map_embed_url", models.URLField(blank=True, verbose_name="Ссылка на карту")),
                ("primary_manager_name", models.CharField(default="Илья", max_length=120, verbose_name="Имя первого менеджера")),
                ("secondary_manager_name", models.CharField(default="Алексей", max_length=120, verbose_name="Имя второго менеджера")),
                ("secondary_manager_phone", models.CharField(default="+79261879852", max_length=50, verbose_name="Телефон второго менеджера")),
                ("footer_description", models.TextField(default="Разрабатываем сайты с удобной админкой, понятной структурой и поддержкой после запуска.", verbose_name="Текст в футере")),
                ("home_case_kicker", models.CharField(default="Опыт с админкой", max_length=120, verbose_name="Кикер кейса на главной")),
                ("home_case_title", models.CharField(default="Aquaklon.ru: сайт, которым владелец управляет сам", max_length=255, verbose_name="Заголовок кейса на главной")),
                ("home_case_body", models.TextField(default="На сайте Aquaklon реализована удобная админ-панель на Django, которая позволяет владельцу самостоятельно управлять контентом без программиста.", verbose_name="Текст кейса на главной")),
                ("home_case_image_primary", models.ImageField(blank=True, null=True, upload_to="home/case/", verbose_name="Первая картинка кейса")),
                ("home_case_image_primary_alt", models.CharField(blank=True, max_length=255, verbose_name="Alt первой картинки кейса")),
                ("home_case_image_secondary", models.ImageField(blank=True, null=True, upload_to="home/case/", verbose_name="Вторая картинка кейса")),
                ("home_case_image_secondary_alt", models.CharField(blank=True, max_length=255, verbose_name="Alt второй картинки кейса")),
                ("process_section_kicker", models.CharField(default="Как работаем", max_length=120, verbose_name="Кикер секции Как работаем")),
                ("process_section_title", models.CharField(default="Как идёт работа по проекту", max_length=255, verbose_name="Заголовок секции Как работаем")),
                ("process_step_1_title", models.CharField(default="Составление ТЗ", max_length=255, verbose_name="Шаг 1 заголовок")),
                ("process_step_1_body", models.TextField(default="Собираем вводные, структуру сайта, блоки и пожелания по стилю, чтобы на старте зафиксировать задачу без потерь.", verbose_name="Шаг 1 текст")),
                ("process_step_2_title", models.CharField(default="Сборка сайта", max_length=255, verbose_name="Шаг 2 заголовок")),
                ("process_step_2_body", models.TextField(default="Показываем рабочий макет и собираем страницы так, чтобы ими можно было пользоваться сразу после запуска.", verbose_name="Шаг 2 текст")),
                ("process_step_3_title", models.CharField(default="Правки и наполнение", max_length=255, verbose_name="Шаг 3 заголовок")),
                ("process_step_3_body", models.TextField(default="Доводим тексты, изображения, каталог и другие блоки до финального состояния перед публикацией.", verbose_name="Шаг 3 текст")),
                ("process_step_4_title", models.CharField(default="Публикация", max_length=255, verbose_name="Шаг 4 заголовок")),
                ("process_step_4_body", models.TextField(default="Подключаем домен, хостинг, почтовые формы и передаём сайт с удобной админкой для дальнейшей работы.", verbose_name="Шаг 4 текст")),
                ("process_highlight_label", models.CharField(default="Фокус проекта", max_length=120, verbose_name="Правая карточка label")),
                ("process_highlight_value", models.CharField(default="Сайт + админка", max_length=255, verbose_name="Правая карточка value")),
                ("process_highlight_body", models.TextField(default="Оставляем только то, что нужно клиенту: публичные страницы, портфолио, заявки и удобное администрирование.", verbose_name="Правая карточка текст")),
                ("process_cta_kicker", models.CharField(default="Составление ТЗ", max_length=120, verbose_name="CTA кикер")),
                ("process_cta_title", models.CharField(default="Сначала фиксируем задачу в ТЗ", max_length=255, verbose_name="CTA заголовок")),
                ("process_cta_body", models.TextField(default='Или <a href="#contacts">напишите нам</a>, если удобнее обсудить задачу в чате.', verbose_name="CTA текст")),
                ("contact_page_kicker", models.CharField(default="Контакты", max_length=120, verbose_name="Кикер страницы контактов")),
                ("contact_page_title", models.CharField(default="Свяжись с нами удобным способом", max_length=255, verbose_name="Заголовок страницы контактов")),
                ("contact_page_cta_kicker", models.CharField(default="Новый проект", max_length=120, verbose_name="Кикер CTA на странице контактов")),
                ("contact_page_cta_title", models.CharField(default="Сразу перейти к структуре задачи", max_length=255, verbose_name="Заголовок CTA на странице контактов")),
                ("contact_page_cta_body", models.TextField(default="Чтобы не терять детали на старте, мы просим клиентов заполнять бриф. Так проект быстрее переходит в оценку и разработку.", verbose_name="Текст CTA на странице контактов")),
                ("contact_page_cta_button", models.CharField(default="Заполнить форму ТЗ", max_length=120, verbose_name="Текст кнопки CTA")),
            ],
            options={"verbose_name": "Контент сайта", "verbose_name_plural": "Контент сайта"},
        ),
        migrations.RunPython(create_default_site_content, migrations.RunPython.noop),
    ]
