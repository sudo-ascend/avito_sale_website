from io import BytesIO

from django.http import HttpResponse
from openpyxl.styles import Font, PatternFill


def style_header(worksheet, row_index: int = 1):
    fill = PatternFill("solid", fgColor="14344C")
    font = Font(color="FFFFFF", bold=True)
    for cell in worksheet[row_index]:
        cell.fill = fill
        cell.font = font


def autosize_columns(worksheet):
    for column_cells in worksheet.columns:
        length = max(len(str(cell.value or "")) for cell in column_cells)
        worksheet.column_dimensions[column_cells[0].column_letter].width = min(length + 2, 45)


def workbook_response(workbook, filename: str) -> HttpResponse:
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
