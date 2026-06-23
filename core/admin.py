from django.contrib import admin
from .models import PerfilUsuario, ListaEnvio, ContatoLista, Disparo, Conversa, MensagemConversa, WhatsAppConfig, WhatsAppIntegrationLog

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'perfil', 'ativo_sistema')
    list_filter = ('perfil', 'ativo_sistema')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'usuario__email')

class ContatoInline(admin.TabularInline):
    model = ContatoLista
    extra = 0

@admin.register(ListaEnvio)
class ListaEnvioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'criada_por', 'criada_em', 'total_contatos')
    search_fields = ('nome',)
    inlines = [ContatoInline]

@admin.register(ContatoLista)
class ContatoListaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'lista')
    search_fields = ('nome', 'telefone', 'lista__nome')

@admin.register(Disparo)
class DisparoAdmin(admin.ModelAdmin):
    list_display = ('lista', 'usuario', 'quantidade', 'status', 'criado_em')
    list_filter = ('status', 'criado_em')

class MensagemInline(admin.TabularInline):
    model = MensagemConversa
    extra = 0

@admin.register(Conversa)
class ConversaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'status', 'responsavel', 'atualizada_em')
    list_filter = ('status', 'responsavel')
    search_fields = ('nome', 'telefone')
    inlines = [MensagemInline]

@admin.register(MensagemConversa)
class MensagemConversaAdmin(admin.ModelAdmin):
    list_display = ('conversa', 'direcao', 'tipo', 'usuario', 'criada_em', 'lida')
    list_filter = ('direcao', 'tipo', 'lida')


@admin.register(WhatsAppConfig)
class WhatsAppConfigAdmin(admin.ModelAdmin):
    list_display = ('nome', 'numero', 'phone_number_id', 'status', 'ativo', 'atualizado_em')
    list_filter = ('status', 'ativo')
    search_fields = ('nome', 'numero', 'phone_number_id')

@admin.register(WhatsAppIntegrationLog)
class WhatsAppIntegrationLogAdmin(admin.ModelAdmin):
    list_display = ('criado_em', 'evento', 'status', 'destino', 'resumo', 'criado_por')
    list_filter = ('evento', 'status', 'criado_em')
    search_fields = ('destino', 'resumo', 'payload', 'resposta')
    readonly_fields = ('criado_em',)
