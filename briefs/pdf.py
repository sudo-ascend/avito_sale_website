from __future__ import annotations

from functools import lru_cache
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from django.conf import settings
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, StyleSheet1, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

PRIMARY = colors.HexColor("#14344c")
PRIMARY_STRONG = colors.HexColor("#0f2638")
ACCENT = colors.HexColor("#c96f3b")
SURFACE = colors.HexColor("#ffffff")
SURFACE_ALT = colors.HexColor("#f4f1ea")
SURFACE_SOFT = colors.HexColor("#f8f9fb")
TEXT = colors.HexColor("#1f2933")
MUTED = colors.HexColor("#5f6c7b")
LINE = colors.HexColor("#d8e1e8")
SUCCESS = colors.HexColor("#2d6a4f")


def get_brief_pdf_filename(brief) -> str:
    return f"brief-{brief.pk}.pdf"


@lru_cache(maxsize=1)
def get_pdf_font_names() -> tuple[str, str]:
    candidates = [
        (
            Path("C:/Windows/Fonts/arial.ttf"),
            Path("C:/Windows/Fonts/arialbd.ttf"),
        ),
        (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ),
        (
            Path("/usr/share/fonts/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"),
        ),
        (
            Path(settings.BASE_DIR) / "static" / "fonts" / "DejaVuSans.ttf",
            Path(settings.BASE_DIR) / "static" / "fonts" / "DejaVuSans-Bold.ttf",
        ),
    ]

    for regular_path, bold_path in candidates:
        if regular_path.exists() and bold_path.exists():
            pdfmetrics.registerFont(TTFont("BriefSans", str(regular_path)))
            pdfmetrics.registerFont(TTFont("BriefSans-Bold", str(bold_path)))
            return "BriefSans", "BriefSans-Bold"

    return "Helvetica", "Helvetica-Bold"


def build_brief_pdf(brief) -> bytes:
    regular_font, bold_font = get_pdf_font_names()
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=32 * mm,
        bottomMargin=20 * mm,
        title=f"Техническое задание #{brief.pk}",
        author=settings.SITE_BRAND_NAME,
    )
    styles = build_pdf_styles(regular_font, bold_font)
    story = []

    created_label = timezone.localtime(brief.created_at).strftime("%d.%m.%Y %H:%M")
    story.append(build_hero_block(brief, styles, created_label))
    story.append(Spacer(1, 10 * mm))
    story.append(build_summary_grid(brief, styles))
    story.append(Spacer(1, 8 * mm))
    story.append(build_palette_block(brief, styles))
    story.append(Spacer(1, 7 * mm))
    story.extend(build_section("Контактные данные", build_contact_table(brief, styles), styles))
    story.extend(build_section("Контент и пожелания", build_content_table(brief, styles), styles))
    story.extend(build_section("Дополнительные услуги", build_extras_table(brief, styles), styles))
    story.extend(build_section("Вложения", build_attachments_table(brief, styles), styles))

    document.build(
        story,
        onFirstPage=lambda canvas, doc: draw_page_chrome(canvas, doc, regular_font, bold_font),
        onLaterPages=lambda canvas, doc: draw_page_chrome(canvas, doc, regular_font, bold_font),
    )
    return buffer.getvalue()


def build_pdf_styles(regular_font: str, bold_font: str) -> StyleSheet1:
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="BriefEyebrow",
            parent=styles["Normal"],
            fontName=bold_font,
            fontSize=8.4,
            leading=10,
            textColor=ACCENT,
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BriefHeroTitle",
            parent=styles["Title"],
            fontName=bold_font,
            fontSize=22,
            leading=26,
            textColor=SURFACE,
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BriefHeroMeta",
            parent=styles["Normal"],
            fontName=regular_font,
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#e5edf2"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="BriefSectionTitle",
            parent=styles["Heading2"],
            fontName=bold_font,
            fontSize=13,
            leading=16,
            textColor=PRIMARY_STRONG,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BriefCardTitle",
            parent=styles["Normal"],
            fontName=bold_font,
            fontSize=8.4,
            leading=10,
            textColor=MUTED,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BriefCardValue",
            parent=styles["Normal"],
            fontName=bold_font,
            fontSize=12,
            leading=15,
            textColor=TEXT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BriefBody",
            parent=styles["BodyText"],
            fontName=regular_font,
            fontSize=10.2,
            leading=14.2,
            textColor=TEXT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BriefBodyMuted",
            parent=styles["BodyText"],
            fontName=regular_font,
            fontSize=9.5,
            leading=13,
            textColor=MUTED,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BriefTableLabel",
            parent=styles["BodyText"],
            fontName=bold_font,
            fontSize=9.3,
            leading=12,
            textColor=PRIMARY_STRONG,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BriefTableValue",
            parent=styles["BodyText"],
            fontName=regular_font,
            fontSize=9.6,
            leading=13.2,
            textColor=TEXT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BriefSmall",
            parent=styles["BodyText"],
            fontName=regular_font,
            fontSize=8.4,
            leading=11,
            textColor=MUTED,
        )
    )
    return styles


def draw_page_chrome(canvas, document, regular_font: str, bold_font: str) -> None:
    page_width, page_height = A4
    canvas.saveState()
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, page_height - 17 * mm, page_width, 17 * mm, stroke=0, fill=1)
    canvas.setFillColor(ACCENT)
    canvas.rect(document.leftMargin, page_height - 17 * mm, 26 * mm, 2.2 * mm, stroke=0, fill=1)
    canvas.setFillColor(SURFACE)
    canvas.setFont(bold_font, 13)
    canvas.drawString(document.leftMargin, page_height - 10.7 * mm, settings.SITE_BRAND_NAME)
    canvas.setStrokeColor(LINE)
    canvas.line(document.leftMargin, 14 * mm, page_width - document.rightMargin, 14 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont(regular_font, 8.6)
    canvas.drawString(document.leftMargin, 9 * mm, "Техническое задание")
    canvas.drawRightString(page_width - document.rightMargin, 9 * mm, f"Стр. {document.page}")
    canvas.restoreState()


def build_hero_block(brief, styles: StyleSheet1, created_label: str) -> Table:
    left_block = [
        Paragraph("Бриф на разработку сайта", styles["BriefEyebrow"]),
        Paragraph("Техническое задание", styles["BriefHeroTitle"]),
        Paragraph(
            escape(brief.business_name or "Без названия"),
            ParagraphStyle(
                "BriefHeroName",
                parent=styles["BriefHeroMeta"],
                fontName=styles["BriefHeroTitle"].fontName,
                fontSize=14,
                leading=17,
                textColor=SURFACE,
            ),
        ),
        Spacer(1, 3 * mm),
        Paragraph(
            "Документ собран автоматически из формы сайта и оформлен в фирменной стилистике.",
            styles["BriefHeroMeta"],
        ),
    ]
    right_html = (
        f"<b>№ ТЗ</b><br/>{brief.pk}<br/><br/>"
        f"<b>Дата</b><br/>{escape(created_label)}<br/><br/>"
        f"<b>Тип сайта</b><br/>{escape(brief.get_site_type_display())}"
    )
    block = Table(
        [[left_block, Paragraph(right_html, styles["BriefHeroMeta"])]],
        colWidths=[112 * mm, 52 * mm],
    )
    block.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
                ("INNERGRID", (0, 0), (-1, -1), 0, PRIMARY),
                ("BOX", (0, 0), (-1, -1), 0, PRIMARY),
                ("TOPPADDING", (0, 0), (-1, -1), 13),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
                ("LEFTPADDING", (0, 0), (-1, -1), 16),
                ("RIGHTPADDING", (0, 0), (-1, -1), 16),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (1, 0), (1, 0), PRIMARY_STRONG),
            ]
        )
    )
    return block


def build_summary_grid(brief, styles: StyleSheet1) -> Table:
    contact_value = "<br/>".join(
        [
            escape(brief.contact_phone or "Не указан"),
            escape(brief.contact_email or "Email не указан"),
        ]
    )
    cards = [
        build_summary_card("Тип клиента", brief.get_client_type_display(), styles),
        build_summary_card("Ориентир по стоимости", format_currency(brief.estimated_price), styles),
        build_summary_card("Связь", contact_value, styles),
        build_summary_card("Предпочтительный канал", brief.get_preferred_contact_app_display(), styles),
    ]
    grid = Table(
        [
            [cards[0], cards[1]],
            [cards[2], cards[3]],
        ],
        colWidths=[79 * mm, 79 * mm],
        hAlign="LEFT",
    )
    grid.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return grid


def build_summary_card(title: str, value: str, styles: StyleSheet1) -> Table:
    card = Table(
        [
            [Paragraph(escape(title), styles["BriefCardTitle"])],
            [Paragraph(value, styles["BriefCardValue"])],
        ],
        colWidths=[79 * mm],
    )
    card.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE_SOFT),
                ("BOX", (0, 0), (-1, -1), 1, LINE),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    return card


def build_palette_block(brief, styles: StyleSheet1) -> Table:
    title = Table(
        [
            [Paragraph("Цветовая палитра", styles["BriefSectionTitle"])],
            [Paragraph(build_palette_caption(brief), styles["BriefBodyMuted"])],
        ],
        colWidths=[164 * mm],
    )
    title.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                ("BOX", (0, 0), (-1, -1), 0, SURFACE),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    color_row = ["" for _ in brief.palette_colors]
    labels_row = [escape(color.upper()) for color in brief.palette_colors]
    palette = Table(
        [color_row, labels_row],
        colWidths=[41 * mm, 41 * mm, 41 * mm, 41 * mm],
        rowHeights=[12 * mm, 7 * mm],
        hAlign="LEFT",
    )
    palette_style = [
        ("BOX", (0, 0), (-1, -1), 1, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 1, SURFACE),
        ("ALIGN", (0, 1), (-1, 1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 1), (-1, 1), styles["BriefSmall"].fontName),
        ("FONTSIZE", (0, 1), (-1, 1), 8.4),
        ("TEXTCOLOR", (0, 1), (-1, 1), MUTED),
        ("BACKGROUND", (0, 1), (-1, 1), SURFACE),
    ]
    for index, color in enumerate(brief.palette_colors):
        palette_style.append(("BACKGROUND", (index, 0), (index, 0), colors.HexColor(color)))
    palette.setStyle(TableStyle(palette_style))

    wrapper = Table([[title], [Spacer(1, 3 * mm)], [palette]], colWidths=[164 * mm])
    wrapper.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE_ALT),
                ("BOX", (0, 0), (-1, -1), 1, LINE),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    return wrapper


def build_palette_caption(brief) -> str:
    if brief.color_mode == brief.ColorMode.TEMPLATE and brief.color_template_name:
        return f"Выбран шаблон палитры: {brief.color_template_name}"
    return "Кастомная палитра, собранная по пожеланиям клиента."


def build_section(title: str, content: Table, styles: StyleSheet1) -> list:
    return [
        Paragraph(escape(title), styles["BriefSectionTitle"]),
        content,
        Spacer(1, 6 * mm),
    ]


def build_contact_table(brief, styles: StyleSheet1) -> Table:
    rows = [
        ("Компания / имя", brief.business_name or "Не указано"),
        ("Телефон", brief.contact_phone or "Не указан"),
        ("Email", brief.contact_email or "Не указан"),
        ("Предпочтительная связь", brief.get_preferred_contact_app_display()),
        ("Регион / адрес", brief.work_region or "Не указан"),
    ]
    return build_details_table(rows, styles)


def build_content_table(brief, styles: StyleSheet1) -> Table:
    rows = [
        ("Тип сайта", brief.get_site_type_display()),
        ("Доп. страницы", str(brief.extra_pages)),
        ("Референсы", brief.reference_sites or "Не указаны"),
        ("Желаемый домен", brief.desired_domain or "Не указан"),
        ("Комментарий клиента", brief.client_comment or "Не добавлен"),
    ]
    return build_details_table(rows, styles)


def build_extras_table(brief, styles: StyleSheet1) -> Table:
    extras = brief.selected_extra_services or ["Дополнительные услуги не выбраны."]
    rows = [
        (
            f"Позиция {index}",
            item,
        )
        for index, item in enumerate(extras, start=1)
    ]
    return build_details_table(rows, styles)


def build_attachments_table(brief, styles: StyleSheet1) -> Table:
    rows = [
        ("Логотип", file_name(brief.logo.name) if brief.logo else "Не прикреплён"),
        ("Фотки", join_names(brief.photo_attachments)),
        ("Тексты", join_names(brief.text_attachments)),
        ("Скрины отзывов", join_names(brief.review_attachments)),
    ]
    return build_details_table(rows, styles)


def build_details_table(rows: list[tuple[str, str]], styles: StyleSheet1) -> Table:
    table_rows = []
    for label, value in rows:
        table_rows.append(
            [
                Paragraph(escape(label), styles["BriefTableLabel"]),
                Paragraph(format_multiline(value), styles["BriefTableValue"]),
            ]
        )
    table = Table(table_rows, colWidths=[44 * mm, 120 * mm], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [SURFACE, SURFACE_SOFT]),
                ("BOX", (0, 0), (-1, -1), 1, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 1, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return table


def format_currency(value) -> str:
    amount = f"{value:,.2f}".replace(",", " ").replace(".", ",")
    if amount.endswith(",00"):
        amount = amount[:-3]
    return f"{amount} ₽"


def format_multiline(value: str) -> str:
    return escape(str(value)).replace("\n", "<br/>")


def join_names(attachments) -> str:
    names = [file_name(attachment.file.name) for attachment in attachments]
    return ", ".join(names) if names else "Не прикреплены"


def file_name(value: str) -> str:
    return Path(value).name
