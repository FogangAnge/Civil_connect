import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mairies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hopital',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=32, unique=True)),
                ('nom', models.CharField(max_length=200)),
                ('adresse', models.CharField(blank=True, default='', max_length=255)),
                ('ville', models.CharField(blank=True, default='', max_length=120)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'user',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='hopital',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='DeclarationHopitaliere',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type_declaration', models.CharField(choices=[('NAISSANCE', 'Naissance'), ('DECES', 'Décès')], max_length=16)),
                ('nom', models.CharField(max_length=150)),
                ('prenom', models.CharField(max_length=150)),
                ('date_evenement', models.DateField()),
                ('lieu', models.CharField(blank=True, default='', max_length=200)),
                ('notes', models.TextField(blank=True, default='')),
                ('statut', models.CharField(choices=[('ENVOYEE', 'Envoyée'), ('VUE', 'Vue'), ('TRAITEE', 'Traitée'), ('REJETEE', 'Rejetée')], default='ENVOYEE', max_length=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'hopital',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='declarations',
                        to='hopitaux.hopital',
                    ),
                ),
                (
                    'mairie',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='declarations_hopital',
                        to='mairies.mairie',
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name='declarationhopitaliere',
            index=models.Index(fields=['mairie', 'created_at'], name='hopitaux_de_mairie__7dc1e9_idx'),
        ),
        migrations.AddIndex(
            model_name='declarationhopitaliere',
            index=models.Index(fields=['hopital', 'created_at'], name='hopitaux_de_hopital_2f3fdd_idx'),
        ),
        migrations.AddIndex(
            model_name='declarationhopitaliere',
            index=models.Index(fields=['statut'], name='hopitaux_de_statut_0cba53_idx'),
        ),
    ]

