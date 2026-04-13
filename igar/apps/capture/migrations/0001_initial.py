from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CaptureUploadRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("upload_id", models.CharField(max_length=128, unique=True)),
                ("filename", models.CharField(max_length=255)),
                ("mime_type", models.CharField(max_length=150)),
                ("size_bytes", models.BigIntegerField()),
                ("bucket", models.CharField(default="igar-temp", max_length=63)),
                ("storage_key", models.CharField(max_length=512)),
                ("raw_metadata", models.JSONField(blank=True, default=dict)),
                (
                    "status",
                    models.CharField(
                        choices=[("received", "Received"), ("error", "Error")],
                        default="received",
                        max_length=16,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("-created_at",)},
        ),
    ]
