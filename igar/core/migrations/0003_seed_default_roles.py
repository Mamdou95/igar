from django.db import migrations


def seed_default_roles(apps, schema_editor):
    group_model = apps.get_model('auth', 'Group')
    default_roles = [
        'Direction',
        'Comptabilite',
        'RH',
        'Production',
        'Archives',
        'Admin',
    ]
    for role_name in default_roles:
        group_model.objects.get_or_create(name=role_name)


def unseed_default_roles(apps, schema_editor):
    group_model = apps.get_model('auth', 'Group')
    default_roles = [
        'Direction',
        'Comptabilite',
        'RH',
        'Production',
        'Archives',
        'Admin',
    ]
    group_model.objects.filter(name__in=default_roles).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('igar_core', '0002_rbac_document_access_groups'),
    ]

    operations = [
        migrations.RunPython(seed_default_roles, reverse_code=unseed_default_roles),
    ]
