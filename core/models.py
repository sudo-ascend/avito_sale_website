from django.db import models
from django.urls import reverse


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        abstract = True


class Service(TimeStampedModel):
    title = models.CharField("Название", max_length=150)
    slug = models.SlugField("Слаг", unique=True)
    icon = models.CharField(
        "Иконка Bootstrap",
        max_length=100,
        default="bi-layers",
        help_text="Например: bi-globe2, bi-window, bi-phone.",
    )
    short_description = models.CharField("Краткое описание", max_length=255)
    description = models.TextField("Подробное описание")
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активно", default=True)

    class Meta:
        ordering = ("order", "title")
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("home")


class SiteContent(TimeStampedModel):
    company_name = models.CharField("Название компании", max_length=150, default="Grachev Studio")
    company_tagline = models.CharField("Подзаголовок компании", max_length=255, blank=True)
    email = models.EmailField("Email", default="grachevilia09@yandex.ru")
    phone = models.CharField("Телефон", max_length=50, default="79167950225")
    telegram = models.CharField("Telegram", max_length=100, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=100, blank=True)
    address = models.CharField("Адрес", max_length=255, blank=True)
    working_hours = models.CharField("Время работы", max_length=150, blank=True)
    map_embed_url = models.URLField("Ссылка на карту", blank=True)
    primary_manager_name = models.CharField("Имя первого менеджера", max_length=120, default="Илья")
    secondary_manager_name = models.CharField("Имя второго менеджера", max_length=120, default="Алексей")
    secondary_manager_phone = models.CharField("Телефон второго менеджера", max_length=50, default="+79261879852")
    footer_description = models.TextField(
        "Текст в футере",
        default="Разрабатываем сайты с удобной админкой, понятной структурой и поддержкой после запуска.",
    )
    home_case_kicker = models.CharField("Кикер кейса на главной", max_length=120, default="Опыт с админкой")
    home_case_title = models.CharField(
        "Заголовок кейса на главной",
        max_length=255,
        default="Aquaklon.ru: сайт, которым владелец управляет сам",
    )
    home_case_body = models.TextField(
        "Текст кейса на главной",
        default=(
            "На сайте Aquaklon реализована удобная админ-панель на Django, которая позволяет "
            "владельцу самостоятельно управлять контентом без программиста."
        ),
    )
    home_case_image_primary = models.ImageField("Первая картинка кейса", upload_to="home/case/", blank=True, null=True)
    home_case_image_primary_alt = models.CharField("Alt первой картинки кейса", max_length=255, blank=True)
    home_case_image_secondary = models.ImageField("Вторая картинка кейса", upload_to="home/case/", blank=True, null=True)
    home_case_image_secondary_alt = models.CharField("Alt второй картинки кейса", max_length=255, blank=True)
    process_section_kicker = models.CharField("Кикер секции Как работаем", max_length=120, default="Как работаем")
    process_section_title = models.CharField("Заголовок секции Как работаем", max_length=255, default="Как идёт работа по проекту")
    process_step_1_title = models.CharField("Шаг 1 заголовок", max_length=255, default="Составление ТЗ")
    process_step_1_body = models.TextField("Шаг 1 текст", default="Собираем вводные, структуру сайта, блоки и пожелания по стилю, чтобы на старте зафиксировать задачу без потерь.")
    process_step_2_title = models.CharField("Шаг 2 заголовок", max_length=255, default="Сборка сайта")
    process_step_2_body = models.TextField("Шаг 2 текст", default="Показываем рабочий макет и собираем страницы так, чтобы ими можно было пользоваться сразу после запуска.")
    process_step_3_title = models.CharField("Шаг 3 заголовок", max_length=255, default="Правки и наполнение")
    process_step_3_body = models.TextField("Шаг 3 текст", default="Доводим тексты, изображения, каталог и другие блоки до финального состояния перед публикацией.")
    process_step_4_title = models.CharField("Шаг 4 заголовок", max_length=255, default="Публикация")
    process_step_4_body = models.TextField("Шаг 4 текст", default="Подключаем домен, хостинг, почтовые формы и передаём сайт с удобной админкой для дальнейшей работы.")
    process_highlight_label = models.CharField("Правая карточка label", max_length=120, default="Фокус проекта")
    process_highlight_value = models.CharField("Правая карточка value", max_length=255, default="Сайт + админка")
    process_highlight_body = models.TextField("Правая карточка текст", default="Оставляем только то, что нужно клиенту: публичные страницы, портфолио, заявки и удобное администрирование.")
    process_cta_kicker = models.CharField("CTA кикер", max_length=120, default="Составление ТЗ")
    process_cta_title = models.CharField("CTA заголовок", max_length=255, default="Сначала фиксируем задачу в ТЗ")
    process_cta_body = models.TextField("CTA текст", default='Или <a href="#contacts">напишите нам</a>, если удобнее обсудить задачу в чате.')
    contact_page_kicker = models.CharField("Кикер страницы контактов", max_length=120, default="Контакты")
    contact_page_title = models.CharField("Заголовок страницы контактов", max_length=255, default="Свяжись с нами удобным способом")
    contact_page_cta_kicker = models.CharField("Кикер CTA на странице контактов", max_length=120, default="Новый проект")
    contact_page_cta_title = models.CharField("Заголовок CTA на странице контактов", max_length=255, default="Сразу перейти к структуре задачи")
    contact_page_cta_body = models.TextField("Текст CTA на странице контактов", default="Чтобы не терять детали на старте, мы просим клиентов заполнять бриф. Так проект быстрее переходит в оценку и разработку.")
    contact_page_cta_button = models.CharField("Текст кнопки CTA", max_length=120, default="Заполнить форму ТЗ")

    class Meta:
        verbose_name = "Контент сайта"
        verbose_name_plural = "Контент сайта"

    def __str__(self) -> str:
        return "Контент сайта"


class HomePageCaseSection(TimeStampedModel):
    kicker = models.CharField("Кикер секции", max_length=120, default="Опыт с админкой")
    title = models.CharField("Заголовок", max_length=255)
    body = models.TextField("Текст секции")
    image_primary = models.ImageField("Первая картинка", upload_to="home/case/", blank=True, null=True)
    image_primary_alt = models.CharField("Alt первой картинки", max_length=255, blank=True)
    image_secondary = models.ImageField("Вторая картинка", upload_to="home/case/", blank=True, null=True)
    image_secondary_alt = models.CharField("Alt второй картинки", max_length=255, blank=True)
    is_active = models.BooleanField("Показывать на главной", default=True)

    class Meta:
        verbose_name = "Секция кейса на главной"
        verbose_name_plural = "Секция кейса на главной"

    def __str__(self) -> str:
        return self.title


class ContactInfo(TimeStampedModel):
    company_name = models.CharField("Название компании", max_length=150)
    tagline = models.CharField("Подзаголовок", max_length=255, blank=True)
    email = models.EmailField("Email")
    phone = models.CharField("Телефон", max_length=50)
    telegram = models.CharField("Telegram", max_length=100, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=100, blank=True)
    address = models.CharField("Адрес", max_length=255, blank=True)
    working_hours = models.CharField("Часы работы", max_length=150, blank=True)
    map_embed_url = models.URLField("Ссылка на карту", blank=True)
    is_primary = models.BooleanField("Основной контакт", default=True)

    class Meta:
        verbose_name = "Контактная информация"
        verbose_name_plural = "Контактная информация"

    def __str__(self) -> str:
        return self.company_name
