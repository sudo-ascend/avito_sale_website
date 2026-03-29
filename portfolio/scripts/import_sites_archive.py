import os
import shutil
import zipfile
from datetime import date
from pathlib import Path, PurePosixPath

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.conf import settings
from django.core.files.base import ContentFile

from portfolio.models import Project, ProjectImage, Technology


def normalized_name(raw_name: str) -> str:
    try:
        return raw_name.encode("cp437").decode("cp866")
    except Exception:
        return raw_name


def find_archive() -> Path:
    desktop = Path.home() / "OneDrive" / "Desktop"
    candidates = [path for path in desktop.glob("*.zip") if path.name != "registry_drf_refactor.zip"]
    if not candidates:
        raise FileNotFoundError("Не найден архив с сайтами на рабочем столе.")
    return candidates[0]


def ensure_technologies() -> dict[str, Technology]:
    specs = {
        "HTML": "#e34f26",
        "CSS": "#1572b6",
        "JavaScript": "#f7df1e",
    }
    result = {}
    for name, color in specs.items():
        technology, _ = Technology.objects.get_or_create(name=name, defaults={"color": color})
        if technology.color != color:
            technology.color = color
            technology.save(update_fields=["color"])
        result[name] = technology
    return result


PROJECTS = [
    {
        "zip_prefix": "сайтики/первый шаблон/",
        "slug": "expert-landing",
        "title": "Landing page для частного специалиста",
        "short_description": "Адаптивный одностраничный сайт услуг частного специалиста с оффером, услугами, отзывами, FAQ и демо-формой заявки.",
        "description": (
            "Адаптивный landing page для частного специалиста или ИП. "
            "В проекте есть первый экран с оффером, блок услуг, этапы работы, "
            "преимущества, отзывы, FAQ и контактная форма с базовой валидацией. "
            "Шаблон рассчитан на быструю адаптацию под эксперта, консультанта "
            "или небольшую сервисную компанию."
        ),
        "completion_date": date(2026, 3, 25),
        "stack_notes": "HTML, CSS, JavaScript, адаптивная вёрстка, демо-форма.",
        "external_url": "/portfolio/site/expert-landing/",
        "color_palette": "#24554f, #c2905e, #f5f0e7, #18252d",
        "cover": "assets/img/og-cover.svg",
        "gallery": [
            ("assets/img/specialist-portrait.svg", "Портретная графика для первого экрана"),
        ],
    },
    {
        "zip_prefix": "сайтики/второй шаблон/",
        "slug": "math-tutor-landing",
        "title": "Мария Лаврентьева | Репетитор по математике",
        "short_description": "Одностраничный сайт репетитора по математике с программами занятий, FAQ, отзывами и прямыми контактами без формы.",
        "description": (
            "Нишевый одностраничный сайт для репетитора по математике. "
            "В проекте сделан акцент на спокойную подачу, понятный маршрут для записи "
            "и прямые контакты через мессенджеры, телефон и email. "
            "Внутри есть блоки о занятиях, программах, процессе работы, отзывах и частых вопросах."
        ),
        "completion_date": date(2026, 3, 26),
        "stack_notes": "HTML, CSS, JavaScript, адаптивная вёрстка, прямые CTA без формы.",
        "external_url": "/portfolio/site/math-tutor-landing/",
        "color_palette": "#2250a3, #ffb84d, #f7f8fc, #15203d",
        "cover": "assets/img/og-cover.svg",
        "gallery": [
            ("assets/img/math-workspace.svg", "Тематическая графика под математику"),
        ],
    },
    {
        "zip_prefix": "сайтики/цветочки/",
        "slug": "bloom-atelier",
        "title": "Bloom Atelier | Цветочный магазин",
        "short_description": "Эстетичный одностраничный сайт цветочного магазина с каталогом букетов, блоком доверия, FAQ и формой быстрого заказа.",
        "description": (
            "Яркий landing page для цветочного магазина с упором на визуал, каталог букетов "
            "и быстрый заказ. В проекте собраны hero-секция, витрина букетов, преимущества, "
            "отзывы, FAQ, контактный блок и форма заявки. Для кейса использованы реальные "
            "фотографии букетов и мягкая фирменная палитра."
        ),
        "completion_date": date(2026, 3, 27),
        "stack_notes": "HTML, CSS, JavaScript, каталог букетов, форма заказа, насыщенный визуал.",
        "external_url": "/portfolio/site/bloom-atelier/",
        "color_palette": "#d77d96, #f7dfe5, #fffaf7, #352726",
        "cover": "assets/images/hero-bouquet.jpg",
        "gallery": [
            ("assets/images/storefront.jpg", "Витрина и интерьер магазина"),
            ("assets/images/process.jpg", "Процесс сборки букетов"),
            ("assets/images/bouquet-garden.jpg", "Одна из карточек каталога"),
        ],
    },
]


def import_projects() -> None:
    zip_path = find_archive()
    media_root = Path(settings.MEDIA_ROOT)
    site_root = media_root / "portfolio" / "sites"
    site_root.mkdir(parents=True, exist_ok=True)
    technologies = ensure_technologies()

    with zipfile.ZipFile(zip_path) as archive:
        name_map = {normalized_name(info.filename): info.filename for info in archive.infolist()}

        for item in PROJECTS:
            prefix = item["zip_prefix"]
            target_dir = site_root / item["slug"]
            if target_dir.exists():
                shutil.rmtree(target_dir)
            target_dir.mkdir(parents=True, exist_ok=True)

            for fixed_name, raw_name in name_map.items():
                if not fixed_name.startswith(prefix) or fixed_name.endswith("/"):
                    continue
                relative = PurePosixPath(fixed_name[len(prefix):])
                destination = target_dir.joinpath(*relative.parts)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(archive.read(raw_name))

            project, _ = Project.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "title": item["title"],
                    "short_description": item["short_description"],
                    "description": item["description"],
                    "completion_date": item["completion_date"],
                    "stack_notes": item["stack_notes"],
                    "external_url": item["external_url"],
                    "color_palette": item["color_palette"],
                    "is_featured": True,
                    "is_published": True,
                },
            )
            project.technologies.set(
                [
                    technologies["HTML"],
                    technologies["CSS"],
                    technologies["JavaScript"],
                ]
            )

            cover_fixed = f"{prefix}{item['cover']}"
            cover_bytes = archive.read(name_map[cover_fixed])
            cover_name = f"{item['slug']}-cover{Path(item['cover']).suffix}"
            project.cover_image.save(cover_name, ContentFile(cover_bytes), save=True)

            project.images.all().delete()
            for order, (relative_path, caption) in enumerate(item["gallery"], start=1):
                fixed_name = f"{prefix}{relative_path}"
                image_bytes = archive.read(name_map[fixed_name])
                image = ProjectImage(project=project, caption=caption, order=order)
                image_name = f"{item['slug']}-gallery-{order}{Path(relative_path).suffix}"
                image.image.save(image_name, ContentFile(image_bytes), save=True)

            print(f"Imported: {project.title}")


if __name__ == "__main__":
    import_projects()
