from __future__ import annotations

from decimal import Decimal


SITE_TYPE_PRICES = {
    "single_page": Decimal("3000.00"),
    "catalog": Decimal("4000.00"),
}

EXTRA_PAGE_PRICE = Decimal("1000.00")

HOSTING_PLAN_PRICES = {
    "monthly": Decimal("750.00"),
    "quarterly": Decimal("1687.50"),
}

OPTIONAL_SERVICE_PRICES = {
    "need_domain": Decimal("550.00"),
    "need_logo_design": Decimal("500.00"),
    "need_basic_seo": Decimal("500.00"),
    "need_photo_selection": Decimal("2000.00"),
    "need_email_form": Decimal("1500.00"),
    "need_reviews_section": Decimal("250.00"),
}

OPTIONAL_SERVICE_LABELS = {
    "need_domain": "Регистрация домена 550 ₽",
    "need_logo_design": "Создание логотипа 500 ₽",
    "need_basic_seo": "Базовое SEO продвижение 500 ₽",
    "need_photo_selection": "Подбор фото и картинок 2 000 ₽",
    "need_email_form": "Форма с отправкой писем на почту 1 500 ₽",
    "need_reviews_section": "Секция с отзывами 250 ₽",
}

HOSTING_PLAN_SUMMARIES = {
    "monthly": "Хостинг сайта 750 ₽/мес",
    "quarterly": "Хостинг сайта на 3 месяца 1 687,50 ₽",
}

HOME_SERVICE_BUNDLES = [
    {
        "key": "site_development",
        "field_name": "site_development",
        "icon": "bi-code-slash",
        "title": "Написание сайта",
        "price": "от 3 000 ₽",
        "short_description": "Обычно стартуем именно с сайта, а затем добираем нужные опции.",
        "description": "Пишем сайт под ваш бизнес: от простого одностраничника до каталога с дополнительными разделами.",
        "details": [
            "Одностраничник — 3 000 ₽",
            "Сайт-каталог — 4 000 ₽",
            "Доп. страница — 1 000 ₽",
        ],
        "cta_target": "home-service-site-details",
        "cta_label": "Подробнее",
    },
    {
        "key": "hosting",
        "field_name": "need_hosting",
        "icon": "bi-hdd-stack",
        "title": "Хостинг сайта",
        "price": "750 ₽/мес",
        "short_description": "Сразу подключаем площадку для публикации сайта.",
        "description": "Можно выбрать оплату на 1 или 3 месяца, как удобнее для запуска проекта.",
        "details": [],
        "cta_target": "",
        "cta_label": "",
    },
    {
        "key": "domain",
        "field_name": "need_domain",
        "icon": "bi-globe2",
        "title": "Регистрация домена",
        "price": "550 ₽",
        "short_description": "Подбираем и регистрируем адрес сайта.",
        "description": "Поможем выбрать домен, чтобы сайт выглядел аккуратно и запоминался.",
        "details": [],
        "cta_target": "",
        "cta_label": "",
    },
    {
        "key": "logo",
        "field_name": "need_logo_design",
        "icon": "bi-vector-pen",
        "title": "Создание логотипа",
        "price": "500 ₽",
        "short_description": "Делаем 4 варианта, вы выбираете лучший.",
        "description": "Логотип — это лицо сайта, поэтому подбираем вариант, который будет смотреться убедительно.",
        "details": [],
        "cta_target": "",
        "cta_label": "",
    },
    {
        "key": "seo",
        "field_name": "need_basic_seo",
        "icon": "bi-graph-up-arrow",
        "title": "Базовое SEO продвижение",
        "price": "500 ₽",
        "short_description": "Базовая оптимизация без Яндекс Директа.",
        "description": "Подготовим основные SEO-настройки, чтобы сайт был аккуратнее для поисковых систем.",
        "details": [],
        "cta_target": "",
        "cta_label": "",
    },
    {
        "key": "photos",
        "field_name": "need_photo_selection",
        "icon": "bi-images",
        "title": "Подбор фото и картинок",
        "price": "2 000 ₽",
        "short_description": "Находим изображения под нишу и стиль сайта.",
        "description": "Собираем подборку визуалов, чтобы сайт не выглядел пустым и случайным.",
        "details": [],
        "cta_target": "",
        "cta_label": "",
    },
    {
        "key": "email_form",
        "field_name": "need_email_form",
        "icon": "bi-envelope-paper",
        "title": "Форма с отправкой писем",
        "price": "1 500 ₽",
        "short_description": "Заявки будут приходить прямо на вашу почту.",
        "description": "Подключаем форму обратной связи и настраиваем отправку писем без лишней ручной работы.",
        "details": [],
        "cta_target": "",
        "cta_label": "",
    },
    {
        "key": "reviews",
        "field_name": "need_reviews_section",
        "icon": "bi-chat-square-quote",
        "title": "Секция с отзывами",
        "price": "250 ₽",
        "short_description": "Добавим аккуратный блок с отзывами на сайт.",
        "description": "Поможем придумать реалистичные отзывы и оформить их так, чтобы блок выглядел живо.",
        "details": [],
        "cta_target": "",
        "cta_label": "",
    },
]

HOME_COMMON_BUNDLE_KEYS = (
    "site_development",
    "hosting",
    "domain",
)


def get_hosting_price(hosting_plan: str | None) -> Decimal:
    return HOSTING_PLAN_PRICES.get(hosting_plan or "monthly", HOSTING_PLAN_PRICES["monthly"])


def normalize_extra_pages(value) -> int:
    try:
        normalized = int(value or 0)
    except (TypeError, ValueError):
        return 0
    return max(0, normalized)


def get_selected_extra_services(
    *,
    extra_pages=0,
    need_hosting=False,
    hosting_plan="monthly",
    need_domain=False,
    need_logo_design=False,
    need_basic_seo=False,
    need_photo_selection=False,
    need_email_form=False,
    need_reviews_section=False,
) -> list[str]:
    services = []
    extra_pages = normalize_extra_pages(extra_pages)

    if extra_pages:
        services.append(f"Доп. страницы: {extra_pages} x 1 000 ₽")
    if need_hosting:
        services.append(HOSTING_PLAN_SUMMARIES.get(hosting_plan or "monthly", HOSTING_PLAN_SUMMARIES["monthly"]))

    for field_name, is_selected in (
        ("need_domain", need_domain),
        ("need_logo_design", need_logo_design),
        ("need_basic_seo", need_basic_seo),
        ("need_photo_selection", need_photo_selection),
        ("need_email_form", need_email_form),
        ("need_reviews_section", need_reviews_section),
    ):
        if is_selected:
            services.append(OPTIONAL_SERVICE_LABELS[field_name])

    return services


def calculate_estimated_price(
    *,
    site_type: str | None,
    extra_pages=0,
    need_hosting=False,
    hosting_plan="monthly",
    need_domain=False,
    need_logo_design=False,
    need_basic_seo=False,
    need_photo_selection=False,
    need_email_form=False,
    need_reviews_section=False,
) -> Decimal:
    total = SITE_TYPE_PRICES.get(site_type or "", Decimal("0.00"))
    total += EXTRA_PAGE_PRICE * normalize_extra_pages(extra_pages)

    if need_hosting:
        total += get_hosting_price(hosting_plan)

    for field_name, is_selected in (
        ("need_domain", need_domain),
        ("need_logo_design", need_logo_design),
        ("need_basic_seo", need_basic_seo),
        ("need_photo_selection", need_photo_selection),
        ("need_email_form", need_email_form),
        ("need_reviews_section", need_reviews_section),
    ):
        if is_selected:
            total += OPTIONAL_SERVICE_PRICES[field_name]

    return total.quantize(Decimal("0.01"))
