from __future__ import annotations

import os
import shutil
import sqlite3
import tempfile
import zipfile
from pathlib import Path

from django.conf import settings
from django.db import migrations


BACKUP_DB_ARCHIVE = Path(settings.BASE_DIR) / "backups" / "prod" / "db.sqlite3.2026-04-20.zip"
BACKUP_MEDIA_ARCHIVE = Path(settings.BASE_DIR) / "backups" / "prod" / "media.2026-04-20.zip"
MEDIA_PREFIX = "media/"
PROJECT_ORDER = [
    "expert-landing",
    "math-tutor-landing",
    "bloom-atelier",
    "aesthetics-house",
    "system-style",
    "triumf-billiards",
    "gracheva-daria",
    "eco-spil",
    "al-lex",
]


def _extract_zip_db_to_temp(db_archive_path: Path) -> Path | None:
    if not db_archive_path.exists():
        return None

    with zipfile.ZipFile(db_archive_path) as archive:
        members = [name for name in archive.namelist() if name.endswith(".sqlite3")]
        if not members:
            return None
        db_bytes = archive.read(members[0])

    fd, temp_path = tempfile.mkstemp(suffix=".sqlite3")
    os.close(fd)
    temp_db_path = Path(temp_path)
    temp_db_path.write_bytes(db_bytes)
    return temp_db_path


def _load_backup_payload() -> tuple[list[dict], list[dict], dict[str, list[str]], dict[str, list[dict]]]:
    temp_db_path = _extract_zip_db_to_temp(BACKUP_DB_ARCHIVE)
    if temp_db_path is None:
        return [], [], {}, {}

    connection = None
    try:
        connection = sqlite3.connect(temp_db_path)
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, title, slug, short_description, description, completion_date,
                   stack_notes, external_url, cover_image, is_featured, is_published, color_palette
            FROM portfolio_project
            ORDER BY id
            """
        )
        projects = [
            {
                "legacy_id": row[0],
                "title": row[1],
                "slug": row[2],
                "short_description": row[3],
                "description": row[4],
                "completion_date": row[5],
                "stack_notes": row[6],
                "external_url": row[7],
                "cover_image": row[8],
                "is_featured": bool(row[9]),
                "is_published": bool(row[10]),
                "color_palette": row[11] or "",
            }
            for row in cursor.fetchall()
        ]

        cursor.execute("SELECT id, name, slug, color FROM portfolio_technology ORDER BY id")
        technologies = [
            {"legacy_id": row[0], "name": row[1], "slug": row[2], "color": row[3]}
            for row in cursor.fetchall()
        ]

        cursor.execute(
            """
            SELECT p.slug, t.name
            FROM portfolio_project_technologies pt
            JOIN portfolio_project p ON p.id = pt.project_id
            JOIN portfolio_technology t ON t.id = pt.technology_id
            ORDER BY pt.project_id, pt.technology_id
            """
        )
        project_technology_map: dict[str, list[str]] = {}
        for slug, technology_name in cursor.fetchall():
            project_technology_map.setdefault(slug, []).append(technology_name)

        cursor.execute(
            """
            SELECT p.slug, i.image, i.caption, i."order"
            FROM portfolio_projectimage i
            JOIN portfolio_project p ON p.id = i.project_id
            ORDER BY p.id, i."order", i.id
            """
        )
        image_map: dict[str, list[dict]] = {}
        for slug, image, caption, order in cursor.fetchall():
            image_map.setdefault(slug, []).append(
                {
                    "image": image,
                    "caption": caption or "",
                    "order": order or 0,
                }
            )

        return projects, technologies, project_technology_map, image_map
    finally:
        if connection is not None:
            connection.close()
        temp_db_path.unlink(missing_ok=True)


def _copy_media_file_if_needed(media_archive: zipfile.ZipFile, relative_path: str) -> None:
    if not relative_path:
        return

    archive_member = f"{MEDIA_PREFIX}{relative_path}"
    target_path = Path(settings.MEDIA_ROOT) / relative_path
    if target_path.exists():
        return
    if archive_member not in media_archive.namelist():
        return

    target_path.parent.mkdir(parents=True, exist_ok=True)
    with media_archive.open(archive_member) as source, target_path.open("wb") as destination:
        shutil.copyfileobj(source, destination)


def seed_portfolio_from_backup(apps, schema_editor):
    Project = apps.get_model("portfolio", "Project")
    ProjectImage = apps.get_model("portfolio", "ProjectImage")
    Technology = apps.get_model("portfolio", "Technology")

    projects, technologies, project_technology_map, image_map = _load_backup_payload()
    if not projects:
        return

    technology_by_name = {}
    for position, payload in enumerate(technologies, start=1):
        technology, _ = Technology.objects.update_or_create(
            slug=payload["slug"],
            defaults={
                "name": payload["name"],
                "color": payload["color"],
                "order": position,
            },
        )
        technology_by_name[technology.name] = technology

    slug_order = {slug: index for index, slug in enumerate(PROJECT_ORDER, start=1)}
    media_archive = zipfile.ZipFile(BACKUP_MEDIA_ARCHIVE) if BACKUP_MEDIA_ARCHIVE.exists() else None

    try:
        for fallback_index, payload in enumerate(projects, start=1):
            catalog_order = slug_order.get(payload["slug"], len(PROJECT_ORDER) + fallback_index)

            if media_archive is not None:
                _copy_media_file_if_needed(media_archive, payload["cover_image"])
                for image_payload in image_map.get(payload["slug"], []):
                    _copy_media_file_if_needed(media_archive, image_payload["image"])

            project, _ = Project.objects.update_or_create(
                slug=payload["slug"],
                defaults={
                    "title": payload["title"],
                    "short_description": payload["short_description"],
                    "description": payload["description"],
                    "completion_date": payload["completion_date"],
                    "stack_notes": payload["stack_notes"],
                    "external_url": payload["external_url"],
                    "cover_image": payload["cover_image"],
                    "cover_image_alt": payload["title"],
                    "color_palette": payload["color_palette"],
                    "catalog_order": catalog_order,
                    "is_featured": payload["is_featured"],
                    "is_published": payload["is_published"],
                },
            )

            project.technologies.set(
                [
                    technology_by_name[name]
                    for name in project_technology_map.get(payload["slug"], [])
                    if name in technology_by_name
                ]
            )

            project.images.all().delete()
            for image_payload in image_map.get(payload["slug"], []):
                ProjectImage.objects.create(
                    project=project,
                    image=image_payload["image"],
                    caption=image_payload["caption"],
                    alt_text=image_payload["caption"] or payload["title"],
                    order=image_payload["order"],
                )
    finally:
        if media_archive is not None:
            media_archive.close()


class Migration(migrations.Migration):
    dependencies = [
        ("portfolio", "0003_alter_project_options_alter_technology_options_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_portfolio_from_backup, migrations.RunPython.noop),
    ]
