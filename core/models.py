from django.conf import settings
from django.db import models
from django.utils import timezone

class PerfilUsuario(models.Model):
    PERFIS = [('ADMIN', 'Administrador'), ('SUPERVISOR', 'Supervisor'), ('OPERADOR', 'Operador')]
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil_whatsapp')
    perfil = models.CharField(max_length=20, choices=PERFIS, default='OPERADOR')
    ativo_sistema = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.usuario.get_full_name() or self.usuario.username} - {self.get_perfil_display()}'

class ListaEnvio(models.Model):
    nome = models.CharField(max_length=160)
    criada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

    @property
    def total_contatos(self):
        return self.contatos.count()

class ContatoLista(models.Model):
    lista = models.ForeignKey(ListaEnvio, on_delete=models.CASCADE, related_name='contatos')
    nome = models.CharField(max_length=160, blank=True)
    telefone = models.CharField(max_length=30)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('lista', 'telefone')

    def __str__(self):
        return f'{self.nome or "Contato"} - {self.telefone}'

class Disparo(models.Model):
    STATUS = [('SIMULADO', 'Simulado'), ('ENVIADO', 'Enviado'), ('ERRO', 'Erro')]
    lista = models.ForeignKey(ListaEnvio, on_delete=models.SET_NULL, null=True, blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    mensagem = models.TextField()
    quantidade = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS, default='SIMULADO')
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.lista} - {self.quantidade} contatos'

class Conversa(models.Model):
    STATUS = [('ABERTA', 'Nova mensagem'), ('EM_ATENDIMENTO', 'Em atendimento'), ('AGUARDANDO', 'Aguardando retorno'), ('TRANSFERENCIA_SOLICITADA', 'Transferência solicitada'), ('FINALIZADA', 'Finalizada')]
    nome = models.CharField(max_length=160, blank=True)
    telefone = models.CharField(max_length=30)
    status = models.CharField(max_length=40, choices=STATUS, default='ABERTA')
    responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='conversas_responsavel')
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)
    finalizada_em = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.nome or self.telefone} - {self.get_status_display()}'

    @property
    def nao_lidas(self):
        return self.mensagens.filter(direcao='RECEBIDA', lida=False).count()

class MensagemConversa(models.Model):
    DIRECOES = [('ENVIADA', 'Enviada'), ('RECEBIDA', 'Recebida')]
    TIPOS = [('TEXTO', 'Texto'), ('IMAGEM', 'Imagem'), ('DOCUMENTO', 'Documento'), ('AUDIO', 'Áudio')]
    STATUS_ENTREGA = [('SIMULADA', 'Simulada'), ('FILA', 'Na fila'), ('ENVIANDO', 'Enviando'), ('ENVIADA', 'Enviada'), ('ENTREGUE', 'Entregue'), ('LIDA', 'Lida'), ('FALHA', 'Falha no envio')]
    conversa = models.ForeignKey(Conversa, on_delete=models.CASCADE, related_name='mensagens')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    direcao = models.CharField(max_length=20, choices=DIRECOES)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='TEXTO')
    texto = models.TextField(blank=True)
    arquivo = models.FileField(upload_to='chat_uploads/%Y/%m/', blank=True, null=True)
    nome_arquivo = models.CharField(max_length=255, blank=True)
    lida = models.BooleanField(default=False)
    status_entrega = models.CharField(max_length=20, choices=STATUS_ENTREGA, default='SIMULADA')
    meta_message_id = models.CharField(max_length=120, blank=True)
    erro_integracao = models.TextField(blank=True)
    criada_em = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['criada_em']

    def __str__(self):
        return f'{self.get_direcao_display()} - {self.get_tipo_display()}'

    @property
    def filename(self):
        if self.nome_arquivo:
            return self.nome_arquivo
        if self.arquivo:
            return self.arquivo.name.split('/')[-1]
        return ''


class WhatsAppConfig(models.Model):
    STATUS = [
        ('AGUARDANDO_VERIFICACAO', 'Aguardando verificação'),
        ('CONECTADO', 'Conectado'),
        ('FALHA', 'Falha na conexão'),
        ('DESATIVADO', 'Desativado'),
    ]
    nome = models.CharField(max_length=120, default='LD Cargo')
    numero = models.CharField(max_length=30, default='+55 35 3606-5528')
    phone_number_id = models.CharField(max_length=80, default='11239284241451517')
    access_token = models.TextField(blank=True)
    webhook_url = models.URLField(blank=True)
    webhook_verify_token = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=40, choices=STATUS, default='AGUARDANDO_VERIFICACAO')
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuração WhatsApp API'
        verbose_name_plural = 'Configurações WhatsApp API'

    def __str__(self):
        return f'{self.nome} - {self.numero}'

    @property
    def token_mascarado(self):
        if not self.access_token:
            return 'Não informado'
        return '•' * 12 + self.access_token[-4:]


class WhatsAppIntegrationLog(models.Model):
    EVENTOS = [
        ('CONFIG', 'Configuração'),
        ('TESTE', 'Teste de conexão'),
        ('ENVIO', 'Envio'),
        ('RECEBIMENTO', 'Recebimento'),
        ('WEBHOOK', 'Webhook'),
        ('ERRO', 'Erro'),
    ]
    STATUS = [('SIMULADO', 'Simulado'), ('SUCESSO', 'Sucesso'), ('FALHA', 'Falha'), ('PENDENTE', 'Pendente')]
    config = models.ForeignKey(WhatsAppConfig, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    evento = models.CharField(max_length=30, choices=EVENTOS)
    status = models.CharField(max_length=20, choices=STATUS, default='SIMULADO')
    destino = models.CharField(max_length=30, blank=True)
    resumo = models.CharField(max_length=255, blank=True)
    payload = models.TextField(blank=True)
    resposta = models.TextField(blank=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Log de integração WhatsApp'
        verbose_name_plural = 'Logs de integração WhatsApp'

    def __str__(self):
        return f'{self.get_evento_display()} - {self.get_status_display()} - {self.criado_em:%d/%m/%Y %H:%M}'
