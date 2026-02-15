# Generated migration to remove duplicate models

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserProfile',
        ),
        migrations.DeleteModel(
            name='SchoolProfile',
        ),
    ]
