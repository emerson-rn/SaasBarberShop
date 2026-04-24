# Generated manually for adding avaliações

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('agendamentos', '0002_agendamento_observacoes_agendamento_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Avaliacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nota', models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('comentario', models.TextField(blank=True, null=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('agendamento', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='avaliacao', to='agendamentos.agendamento')),
                ('barbeiro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='avaliacoes_recebidas', to=settings.AUTH_USER_MODEL)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='avaliacoes_feitas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Avaliação',
                'verbose_name_plural': 'Avaliações',
                'ordering': ['-criado_em'],
            },
        ),
    ]
