from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_mfa_enabled_user_mfa_secret_user_telephone'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='nin',
            field=models.CharField(max_length=24, blank=True, default='', db_index=True),
        ),
    ]
