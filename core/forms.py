from django import forms
from django.contrib.auth.models import User
from .models import ListaEnvio, ContatoLista, Disparo, MensagemConversa, Conversa, PerfilUsuario, WhatsAppConfig

class UsuarioForm(forms.ModelForm):
    senha = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite uma nova senha'}),
        required=False,
        help_text='Informe somente para criar/alterar a senha.'
    )
    perfil = forms.ChoiceField(choices=PerfilUsuario.PERFIS, widget=forms.Select(attrs={'class': 'form-select'}))
    ativo_sistema = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Paulo'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Roberto'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: paulo.roberto'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'nome@empresa.com.br'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ListaEnvioForm(forms.ModelForm):
    class Meta:
        model = ListaEnvio
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Motoristas Sul de Minas'}),
        }

class ContatoListaForm(forms.ModelForm):
    class Meta:
        model = ContatoLista
        fields = ['nome', 'telefone']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do contato'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '35999999999'}),
        }

class DisparoForm(forms.ModelForm):
    class Meta:
        model = Disparo
        fields = ['lista', 'mensagem']
        widgets = {
            'lista': forms.Select(attrs={'class': 'form-select'}),
            'mensagem': forms.Textarea(attrs={'class': 'form-control', 'rows': 7, 'placeholder': 'Digite a mensagem que será enviada para a lista selecionada.'}),
        }

class ConversaForm(forms.ModelForm):
    class Meta:
        model = Conversa
        fields = ['nome', 'telefone']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do contato'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone com DDD'}),
        }

class MensagemTextoForm(forms.ModelForm):
    class Meta:
        model = MensagemConversa
        fields = ['texto']
        widgets = {'texto': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Digite a resposta para este contato.'})}

class MensagemAnexoForm(forms.ModelForm):
    class Meta:
        model = MensagemConversa
        fields = ['tipo', 'texto', 'arquivo']
        widgets = {'texto': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Legenda ou observação opcional.'})}


class WhatsAppConfigForm(forms.ModelForm):
    class Meta:
        model = WhatsAppConfig
        fields = ['nome', 'numero', 'phone_number_id', 'access_token', 'webhook_url', 'webhook_verify_token', 'status', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'LD Cargo'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+55 35 3606-5528'}),
            'phone_number_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '11239284241451517'}),
            'access_token': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Cole o token da Meta quando disponível'}, render_value=True),
            'webhook_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://seu-dominio.com.br/api/whatsapp/webhook/'}),
            'webhook_verify_token': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Token interno para validação do webhook'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
