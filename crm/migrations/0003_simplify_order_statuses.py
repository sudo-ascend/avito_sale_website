from django.db import migrations, models


def migrate_order_statuses(apps, schema_editor):
    Order = apps.get_model("crm", "Order")
    status_mapping = {
        "lead": "new",
        "support": "in_progress",
        "on_hold": "in_progress",
        "cancelled": "completed",
    }
    for old_status, new_status in status_mapping.items():
        Order.objects.filter(status=old_status).update(status=new_status)


class Migration(migrations.Migration):
    dependencies = [
        ("crm", "0002_client_preferred_contact_app_alter_order_status"),
    ]

    operations = [
        migrations.RunPython(migrate_order_statuses, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("new", "Новый"),
                    ("in_progress", "В работе"),
                    ("dns_pending", "Ожидание обновления DNS"),
                    ("completed", "Выполнено"),
                ],
                default="new",
                max_length=20,
                verbose_name="Статус",
            ),
        ),
    ]
