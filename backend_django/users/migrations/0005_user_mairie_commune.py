from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_user_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='commune',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='user',
            name='mairie',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='users', to='mairies.mairie'),
        ),
    ]
