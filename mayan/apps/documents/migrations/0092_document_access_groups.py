from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('igar_core', '0002_rbac_document_access_groups'),
        ('documents', '0091_fix_documenttype_verbose_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='access_groups',
            field=models.ManyToManyField(
                blank=True,
                help_text='Document access groups used for cloisonnement.',
                related_name='documents',
                to='igar_core.documentaccessgroup',
                verbose_name='Access groups'
            ),
        ),
    ]
