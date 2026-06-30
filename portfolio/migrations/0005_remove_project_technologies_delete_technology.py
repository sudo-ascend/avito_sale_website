from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("portfolio", "0004_seed_portfolio_from_backup"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="project",
            name="technologies",
        ),
        migrations.DeleteModel(
            name="Technology",
        ),
    ]
