from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0002_criar_grupos_perfil'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telefone', models.CharField(max_length=20)),
                ('nome', models.CharField(blank=True, max_length=120)),
                ('status', models.CharField(choices=[('ABERTA', 'Aberta'), ('EM_ATENDIMENTO', 'Em atendimento'), ('FINALIZADA', 'Finalizada')], default='ABERTA', max_length=20)),
                ('criada_em', models.DateTimeField(default=django.utils.timezone.now)),
                ('atualizada_em', models.DateTimeField(default=django.utils.timezone.now)),
                ('responsavel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='conversas_responsaveis', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Conversa',
                'verbose_name_plural': 'Conversas',
                'ordering': ['-atualizada_em'],
            },
        ),
        migrations.CreateModel(
            name='MensagemConversa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direcao', models.CharField(choices=[('ENTRADA', 'Recebida'), ('SAIDA', 'Enviada')], max_length=10)),
                ('texto', models.TextField()),
                ('criada_em', models.DateTimeField(default=django.utils.timezone.now)),
                ('retorno_api', models.TextField(blank=True)),
                ('conversa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensagens', to='core.conversa')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mensagens_conversa', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Mensagem da conversa',
                'verbose_name_plural': 'Mensagens da conversa',
                'ordering': ['criada_em'],
            },
        ),
    ]
