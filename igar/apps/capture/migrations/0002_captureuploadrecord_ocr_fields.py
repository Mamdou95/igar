from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("capture", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="captureuploadrecord",
            name="ocr_duration_ms",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="captureuploadrecord",
            name="ocr_error",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="captureuploadrecord",
            name="ocr_status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("queued", "Queued"),
                    ("processing", "Processing"),
                    ("done", "Done"),
                    ("failed", "Failed"),
                ],
                default="pending",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="captureuploadrecord",
            name="ocr_text",
            field=models.TextField(blank=True, default=""),
        ),
    ]
