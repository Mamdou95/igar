# Generated migration for document access groups and audit logging

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("igar_core", "0001_two_factor_reset_event"),
    ]

    operations = [
        migrations.CreateModel(
            name="DocumentAccessGroup",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("uuid", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(db_index=True, max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="children",
                        to="igar_core.documentaccessgroup",
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="GroupDocumentAccessGroup",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("uuid", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "access_group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="groups",
                        to="igar_core.documentaccessgroup",
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="allowed_document_groups",
                        to="auth.group",
                    ),
                ),
            ],
            options={
                "ordering": ("group", "access_group"),
                "unique_together": {("group", "access_group")},
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="UserDocumentAccessGroup",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("uuid", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "access_group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="users",
                        to="igar_core.documentaccessgroup",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="allowed_document_groups",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("user", "access_group"),
                "unique_together": {("user", "access_group")},
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="AuditLogEntry",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("uuid", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("user.created", "User créé"),
                            ("user.modified", "User modifié"),
                            ("user.deactivated", "User désactivé"),
                            ("user.2fa_reset", "2FA réinitialisé"),
                            ("role.created", "Rôle créé"),
                            ("role.modified", "Rôle modifié"),
                            ("role.deleted", "Rôle supprimé"),
                            ("permission.assigned", "Permission assignée"),
                            ("permission.revoked", "Permission révoquée"),
                            ("document.access_denied", "Accès document refusé"),
                            ("group.user_added", "Utilisateur ajouté au groupe"),
                            ("group.user_removed", "Utilisateur retiré du groupe"),
                        ],
                        db_index=True,
                        max_length=32,
                    ),
                ),
                (
                    "resource_type",
                    models.CharField(
                        choices=[
                            ("user", "Utilisateur"),
                            ("role", "Rôle"),
                            ("group", "Groupe"),
                            ("document", "Document"),
                            ("permission", "Permission"),
                        ],
                        db_index=True,
                        max_length=32,
                    ),
                ),
                ("resource_id", models.IntegerField(db_index=True)),
                ("old_values", models.JSONField(blank=True, null=True)),
                ("new_values", models.JSONField(blank=True, null=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("reason", models.TextField(blank=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="audit_log_entries",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
                "abstract": False,
            },
        ),
        migrations.AddIndex(
            model_name="groupdocumentaccessgroup",
            index=models.Index(fields=("group", "access_group"), name="igar_core_g_groupid_a5d8c2_idx"),
        ),
        migrations.AddIndex(
            model_name="groupdocumentaccessgroup",
            index=models.Index(fields=("access_group",), name="igar_core_g_access__f4a1b3_idx"),
        ),
        migrations.AddIndex(
            model_name="userdocumentaccessgroup",
            index=models.Index(fields=("user", "access_group"), name="igar_core_u_userid_c2d9e1_idx"),
        ),
        migrations.AddIndex(
            model_name="userdocumentaccessgroup",
            index=models.Index(fields=("access_group",), name="igar_core_u_access__a7b2f8_idx"),
        ),
        migrations.AddIndex(
            model_name="auditlogentry",
            index=models.Index(fields=("-created_at",), name="igar_core_a_created_3c1a9d_idx"),
        ),
        migrations.AddIndex(
            model_name="auditlogentry",
            index=models.Index(fields=("user", "-created_at"), name="igar_core_a_userid_d5e8c2_idx"),
        ),
        migrations.AddIndex(
            model_name="auditlogentry",
            index=models.Index(fields=("action", "-created_at"), name="igar_core_a_action_b3f1a7_idx"),
        ),
        migrations.AddIndex(
            model_name="auditlogentry",
            index=models.Index(fields=("resource_type", "resource_id"), name="igar_core_a_resourc_e9c7b2_idx"),
        ),
        migrations.AddIndex(
            model_name="documentaccessgroup",
            index=models.Index(fields=("name",), name="igar_core_d_name_a5c3d1_idx"),
        ),
        migrations.AddIndex(
            model_name="documentaccessgroup",
            index=models.Index(fields=("parent",), name="igar_core_d_parent_f2b8e9_idx"),
        ),
    ]
