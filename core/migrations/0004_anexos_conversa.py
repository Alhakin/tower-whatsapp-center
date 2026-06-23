from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_conversas'),
    ]

    operations = [
        migrations.AddField(
            model_name='mensagemconversa',
            name='tipo',
            field=models.CharField(choices=[('TEXTO', 'Texto'), ('IMAGEM', 'Imagem'), ('DOCUMENTO', 'Documento'), ('AUDIO', 'Áudio')], default='TEXTO', max_length=20),
        ),
        migrations.AlterField(
            model_name='mensagemconversa',
            name='texto',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='mensagemconversa',
            name='arquivo',
            field=models.FileField(blank=True, null=True, upload_to='conversas/anexos/%Y/%m/'),
        ),
        migrations.AddField(
            model_name='mensagemconversa',
            name='nome_arquivo',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
