from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .forms import UsuarioForm, ListaEnvioForm, ContatoListaForm, DisparoForm, ConversaForm, MensagemAnexoForm, WhatsAppConfigForm
from .models import PerfilUsuario, ListaEnvio, ContatoLista, Disparo, Conversa, MensagemConversa, WhatsAppConfig, WhatsAppIntegrationLog


def perfil_do_usuario(user):
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=user)
    return perfil


def is_admin(user):
    return user.is_superuser or user.is_staff or perfil_do_usuario(user).perfil == 'ADMIN'




def get_whatsapp_config():
    config = WhatsAppConfig.objects.filter(ativo=True).first()
    if not config:
        config = WhatsAppConfig.objects.create(
            nome='LD Cargo',
            numero='+55 35 3606-5528',
            phone_number_id='11239284241451517',
            status='AGUARDANDO_VERIFICACAO',
            ativo=True,
        )
    return config


def registrar_log_whatsapp(evento, status='SIMULADO', destino='', resumo='', payload='', resposta='', usuario=None, config=None):
    try:
        WhatsAppIntegrationLog.objects.create(
            config=config or get_whatsapp_config(),
            evento=evento,
            status=status,
            destino=destino,
            resumo=resumo[:255] if resumo else '',
            payload=payload or '',
            resposta=resposta or '',
            criado_por=usuario,
        )
    except Exception:
        pass

def is_supervisor(user):
    return perfil_do_usuario(user).perfil == 'SUPERVISOR'


def is_gestor(user):
    return is_admin(user) or is_supervisor(user)


def usuario_responsavel(conversa, user):
    return conversa.responsavel_id == user.id


def pode_interagir_conversa(conversa, user):
    if conversa.status == 'FINALIZADA':
        return False
    return is_gestor(user) or usuario_responsavel(conversa, user)


def pode_assumir_conversa(conversa, user):
    if conversa.status == 'FINALIZADA':
        return False
    if not is_gestor(user):
        return False
    return conversa.responsavel_id is None or conversa.status in ['ABERTA', 'TRANSFERENCIA_SOLICITADA']


def conversa_status_badge(status):
    return {
        'ABERTA': 'Nova mensagem',
        'EM_ATENDIMENTO': 'Em atendimento',
        'AGUARDANDO': 'Aguardando retorno',
        'TRANSFERENCIA_SOLICITADA': 'Transferência solicitada',
        'FINALIZADA': 'Finalizada',
    }.get(status, status)


def filtrar_conversas(request, qs):
    filtro = request.GET.get('filtro', '').strip()
    busca = request.GET.get('q', '').strip()
    if filtro == 'minhas':
        qs = qs.filter(responsavel=request.user)
    elif filtro == 'novas':
        qs = qs.filter(status='ABERTA')
    elif filtro == 'aguardando':
        qs = qs.filter(status='AGUARDANDO')
    elif filtro == 'transferencia':
        qs = qs.filter(status='TRANSFERENCIA_SOLICITADA')
    elif filtro == 'atendimento':
        qs = qs.filter(status='EM_ATENDIMENTO')
    if busca:
        qs = qs.filter(Q(nome__icontains=busca) | Q(telefone__icontains=busca) | Q(mensagens__texto__icontains=busca)).distinct()
    return qs, filtro, busca


@login_required
def dashboard(request):
    admin = is_admin(request.user)
    gestor = is_gestor(request.user)
    conversas_abertas_qs = Conversa.objects.exclude(status='FINALIZADA').order_by('-atualizada_em')

    if gestor:
        contexto = {
            'admin_view': True,
            'supervisor_view': is_supervisor(request.user) and not admin,
            'usuarios_ativos': User.objects.filter(is_active=True).count(),
            'listas_total': ListaEnvio.objects.count(),
            'contatos_total': ContatoLista.objects.count(),
            'mensagens_mes': MensagemConversa.objects.filter(criada_em__month=timezone.now().month, direcao='ENVIADA').count(),
            'conversas_abertas_total': conversas_abertas_qs.count(),
            'nao_lidas_total': MensagemConversa.objects.filter(direcao='RECEBIDA', lida=False).exclude(conversa__status='FINALIZADA').count(),
            'transferencias_pendentes': Conversa.objects.filter(status='TRANSFERENCIA_SOLICITADA').count(),
            'ultimos_disparos': Disparo.objects.select_related('usuario', 'lista').order_by('-criado_em')[:8],
            'conversas_abertas': conversas_abertas_qs.select_related('responsavel')[:8],
            'ranking_usuarios': (
                MensagemConversa.objects
                .filter(criada_em__month=timezone.now().month, direcao='ENVIADA', usuario__isnull=False)
                .values('usuario__username', 'usuario__first_name', 'usuario__last_name')
                .annotate(total=Count('id'))
                .order_by('-total')[:8]
            ),
        }
    else:
        contexto = {
            'admin_view': False,
            'listas_total': ListaEnvio.objects.count(),
            'contatos_total': ContatoLista.objects.count(),
            'meus_disparos': MensagemConversa.objects.filter(usuario=request.user, direcao='ENVIADA').count(),
            'minhas_conversas': Conversa.objects.filter(responsavel=request.user).exclude(status='FINALIZADA').count(),
            'conversas_abertas_total': conversas_abertas_qs.count(),
            'nao_lidas_total': MensagemConversa.objects.filter(direcao='RECEBIDA', lida=False).exclude(conversa__status='FINALIZADA').count(),
            'transferencias_pendentes': Conversa.objects.filter(status='TRANSFERENCIA_SOLICITADA').count(),
            'ultimos_disparos': Disparo.objects.filter(usuario=request.user).select_related('lista').order_by('-criado_em')[:8],
            'conversas_abertas': conversas_abertas_qs.select_related('responsavel')[:8],
        }
    return render(request, 'core/dashboard.html', contexto)


@login_required
def usuarios(request):
    if not is_admin(request.user):
        messages.error(request, 'Acesso restrito ao administrador.')
        return redirect('dashboard')
    return render(request, 'core/usuarios.html', {'usuarios': User.objects.all().order_by('first_name','username')})


@login_required
def usuario_form(request, pk=None):
    if not is_admin(request.user):
        messages.error(request, 'Acesso restrito ao administrador.')
        return redirect('dashboard')
    usuario = get_object_or_404(User, pk=pk) if pk else None
    perfil_obj = perfil_do_usuario(usuario) if usuario else None
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            novo_usuario = form.save(commit=False)
            senha = form.cleaned_data.get('senha')
            if senha:
                novo_usuario.set_password(senha)
            novo_usuario.save()
            perfil, _ = PerfilUsuario.objects.get_or_create(usuario=novo_usuario)
            perfil.perfil = form.cleaned_data['perfil']
            perfil.ativo_sistema = form.cleaned_data['ativo_sistema']
            perfil.save()
            messages.success(request, 'Usuário salvo com sucesso.')
            return redirect('usuarios')
    else:
        initial = {}
        if perfil_obj:
            initial = {'perfil': perfil_obj.perfil, 'ativo_sistema': perfil_obj.ativo_sistema}
        form = UsuarioForm(instance=usuario, initial=initial)
    return render(request, 'core/usuario_form.html', {'form': form, 'usuario_editado': usuario})


@login_required
def listas(request):
    listas_qs = ListaEnvio.objects.select_related('criada_por').annotate(total=Count('contatos')).order_by('-criada_em')
    return render(request, 'core/listas.html', {'listas': listas_qs})


@login_required
def lista_form(request, pk=None):
    lista = get_object_or_404(ListaEnvio, pk=pk) if pk else None
    if request.method == 'POST':
        form = ListaEnvioForm(request.POST, instance=lista)
        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.pk:
                obj.criada_por = request.user
            obj.save()
            messages.success(request, 'Lista salva com sucesso.')
            return redirect('lista_detalhe', pk=obj.pk)
    else:
        form = ListaEnvioForm(instance=lista)
    return render(request, 'core/lista_form.html', {'form': form})


@login_required
def lista_detalhe(request, pk):
    lista = get_object_or_404(ListaEnvio, pk=pk)
    return render(request, 'core/lista_detalhe.html', {'lista': lista, 'contatos': lista.contatos.order_by('nome','telefone')})


@login_required
def contato_form(request, pk):
    lista = get_object_or_404(ListaEnvio, pk=pk)
    if request.method == 'POST':
        form = ContatoListaForm(request.POST)
        if form.is_valid():
            contato = form.save(commit=False)
            contato.lista = lista
            contato.save()
            messages.success(request, 'Contato adicionado.')
            return redirect('lista_detalhe', pk=lista.pk)
    else:
        form = ContatoListaForm()
    return render(request, 'core/contato_form.html', {'form': form, 'lista': lista})


@login_required
def disparos(request):
    qs = Disparo.objects.select_related('lista','usuario').order_by('-criado_em')
    if not is_gestor(request.user):
        qs = qs.filter(usuario=request.user)
    return render(request, 'core/disparos.html', {'disparos': qs})


@login_required
def disparo_novo(request):
    if request.method == 'POST':
        form = DisparoForm(request.POST)
        if form.is_valid():
            disparo = form.save(commit=False)
            disparo.usuario = request.user
            disparo.quantidade = disparo.lista.contatos.count() if disparo.lista else 0
            disparo.status = 'SIMULADO'
            disparo.save()
            # cria conversas e registra mensagem simulada para cada contato
            for contato in disparo.lista.contatos.all():
                conversa, _ = Conversa.objects.get_or_create(telefone=contato.telefone, defaults={'nome': contato.nome or contato.telefone})
                MensagemConversa.objects.create(conversa=conversa, usuario=request.user, direcao='ENVIADA', tipo='TEXTO', texto=disparo.mensagem, lida=True, status_entrega='SIMULADA')
            registrar_log_whatsapp(evento='ENVIO', status='SIMULADO', destino='lista', resumo=f'Disparo simulado para {disparo.quantidade} contatos.', payload=disparo.mensagem, resposta='Modo local/teste. Nenhuma mensagem foi enviada para a Meta.', usuario=request.user)
            messages.success(request, 'Disparo simulado registrado.')
            return redirect('disparos')
    else:
        form = DisparoForm()
    return render(request, 'core/disparo_form.html', {'form': form})


@login_required
def conversas(request):
    qs = Conversa.objects.exclude(status='FINALIZADA').select_related('responsavel').order_by('-atualizada_em')
    qs, filtro, busca = filtrar_conversas(request, qs)
    return render(request, 'core/conversas.html', {
        'conversas': qs, 'titulo': 'Conversas', 'filtro': filtro, 'busca': busca,
        'total_nao_lidas': MensagemConversa.objects.filter(direcao='RECEBIDA', lida=False).exclude(conversa__status='FINALIZADA').count(),
        'total_transferencias': Conversa.objects.filter(status='TRANSFERENCIA_SOLICITADA').count(),
    })


@login_required
def conversas_finalizadas(request):
    qs = Conversa.objects.filter(status='FINALIZADA').select_related('responsavel').order_by('-finalizada_em','-atualizada_em')
    qs, filtro, busca = filtrar_conversas(request, qs)
    return render(request, 'core/conversas.html', {'conversas': qs, 'titulo': 'Atendimentos finalizados', 'finalizadas': True, 'filtro': filtro, 'busca': busca})


@login_required
def conversa_nova(request):
    if request.method == 'POST':
        form = ConversaForm(request.POST)
        if form.is_valid():
            conversa = form.save(commit=False)
            conversa.status = 'EM_ATENDIMENTO'
            conversa.responsavel = request.user
            conversa.save()
            messages.success(request, 'Conversa criada.')
            return redirect('conversa_detalhe', pk=conversa.pk)
    else:
        form = ConversaForm()
    return render(request, 'core/conversa_form.html', {'form': form})


def _salvar_mensagem_anexo(request, conversa, direcao):
    texto = request.POST.get('texto', '').strip()
    tipo = request.POST.get('tipo', 'TEXTO')
    arquivo = request.FILES.get('arquivo') or request.FILES.get('audio_blob')
    if arquivo and tipo == 'TEXTO':
        content_type = getattr(arquivo, 'content_type', '') or ''
        if content_type.startswith('image/'):
            tipo = 'IMAGEM'
        elif content_type.startswith('audio/'):
            tipo = 'AUDIO'
        else:
            tipo = 'DOCUMENTO'
    if not texto and not arquivo:
        return False
    mensagem = MensagemConversa.objects.create(
        conversa=conversa,
        usuario=request.user if direcao == 'ENVIADA' else None,
        direcao=direcao,
        tipo=tipo,
        texto=texto,
        arquivo=arquivo,
        nome_arquivo=getattr(arquivo, 'name', '') if arquivo else '',
        lida=(direcao == 'ENVIADA'),
        status_entrega='SIMULADA'
    )
    if direcao == 'ENVIADA':
        registrar_log_whatsapp(
            evento='ENVIO',
            status='SIMULADO',
            destino=conversa.telefone,
            resumo=f'Mensagem {tipo.lower()} registrada em modo simulado.',
            payload=texto,
            resposta='Modo local/teste. A mensagem não foi enviada para a API da Meta.',
            usuario=request.user,
        )
    elif direcao == 'RECEBIDA':
        registrar_log_whatsapp(
            evento='RECEBIMENTO',
            status='SIMULADO',
            destino=conversa.telefone,
            resumo=f'Recebimento {tipo.lower()} simulado.',
            payload=texto,
            resposta='Recebimento registrado manualmente para simulação do webhook.',
            usuario=request.user,
        )
    conversa.atualizada_em = timezone.now()
    if conversa.status == 'FINALIZADA':
        conversa.status = 'EM_ATENDIMENTO'
        conversa.finalizada_em = None
    elif direcao == 'RECEBIDA' and conversa.status != 'TRANSFERENCIA_SOLICITADA':
        conversa.status = 'ABERTA'
    elif direcao == 'ENVIADA' and conversa.status == 'ABERTA':
        conversa.status = 'EM_ATENDIMENTO'
    conversa.save()
    return True


@login_required
def conversa_detalhe(request, pk):
    conversa = get_object_or_404(Conversa, pk=pk)
    admin = is_admin(request.user)
    can_interact = pode_interagir_conversa(conversa, request.user)

    if request.method == 'POST':
        if not can_interact:
            messages.error(request, 'Este atendimento está com outro responsável. Você pode visualizar e solicitar a transferência, mas não pode interagir.')
            return redirect('conversa_detalhe', pk=conversa.pk)
        if _salvar_mensagem_anexo(request, conversa, 'ENVIADA'):
            messages.success(request, 'Mensagem simulada enviada.')
        else:
            messages.warning(request, 'Digite uma mensagem ou anexe um arquivo.')
        return redirect('conversa_detalhe', pk=conversa.pk)

    if can_interact:
        conversa.mensagens.filter(direcao='RECEBIDA', lida=False).update(lida=True)

    usuarios = User.objects.filter(is_active=True).order_by('first_name','username')
    conversas_menu = Conversa.objects.select_related('responsavel').order_by('-atualizada_em')[:80]
    return render(request, 'core/conversa_detalhe.html', {
        'conversa': conversa,
        'usuarios': usuarios,
        'conversas_menu': conversas_menu,
        'can_interact': can_interact,
        'can_transfer': is_gestor(request.user) or usuario_responsavel(conversa, request.user),
        'can_assume': pode_assumir_conversa(conversa, request.user),
        'can_request_transfer': (not can_interact and conversa.status != 'FINALIZADA'),
    })


@login_required
def conversa_editar_contato(request, pk):
    conversa = get_object_or_404(Conversa, pk=pk)
    if not is_gestor(request.user) and not usuario_responsavel(conversa, request.user):
        messages.error(request, 'Somente o responsável, supervisor ou administrador pode editar o contato desta conversa.')
        return redirect('conversa_detalhe', pk=pk)

    telefone_antigo = conversa.telefone
    if request.method == 'POST':
        form = ConversaForm(request.POST, instance=conversa)
        if form.is_valid():
            conversa_editada = form.save(commit=False)
            nome_novo = (conversa_editada.nome or '').strip()
            telefone_novo = (conversa_editada.telefone or '').strip()
            conversa_editada.nome = nome_novo
            conversa_editada.telefone = telefone_novo
            conversa_editada.save()

            # Atualiza o nome/telefone do mesmo contato em todas as listas onde ele já estiver incluído.
            contatos_vinculados = ContatoLista.objects.filter(telefone=telefone_antigo)
            atualizados = 0
            for contato in contatos_vinculados:
                conflito = ContatoLista.objects.filter(lista=contato.lista, telefone=telefone_novo).exclude(pk=contato.pk).first()
                if conflito:
                    if nome_novo:
                        conflito.nome = nome_novo
                        conflito.save(update_fields=['nome'])
                    contato.delete()
                    atualizados += 1
                else:
                    contato.telefone = telefone_novo
                    if nome_novo:
                        contato.nome = nome_novo
                    contato.save()
                    atualizados += 1

            # Se houver registros já com o telefone novo em outras listas, atualiza o nome também.
            if nome_novo:
                atualizados += ContatoLista.objects.filter(telefone=telefone_novo).exclude(nome=nome_novo).update(nome=nome_novo)

            messages.success(request, f'Contato atualizado. Listas vinculadas atualizadas: {atualizados}.')
            return redirect('conversa_detalhe', pk=conversa.pk)
    else:
        form = ConversaForm(instance=conversa)

    return render(request, 'core/conversa_contato_form.html', {'form': form, 'conversa': conversa})


@login_required
def simular_recebida(request, pk):
    conversa = get_object_or_404(Conversa, pk=pk)
    if not pode_interagir_conversa(conversa, request.user):
        messages.error(request, 'Apenas o responsável pelo atendimento pode registrar mensagens nesta conversa.')
        return redirect('conversa_detalhe', pk=conversa.pk)
    if request.method == 'POST':
        if _salvar_mensagem_anexo(request, conversa, 'RECEBIDA'):
            messages.success(request, 'Recebimento simulado registrado.')
        else:
            messages.warning(request, 'Digite uma mensagem ou anexe um arquivo.')
    return redirect('conversa_detalhe', pk=conversa.pk)


@login_required
def conversa_assumir(request, pk):
    conversa = get_object_or_404(Conversa, pk=pk)
    if not pode_assumir_conversa(conversa, request.user):
        messages.error(request, 'Este atendimento já possui responsável. Solicite a transferência do atendimento.')
        return redirect('conversa_detalhe', pk=pk)
    conversa.responsavel = request.user
    conversa.status = 'EM_ATENDIMENTO'
    conversa.finalizada_em = None
    conversa.save()
    messages.success(request, 'Atendimento assumido.')
    return redirect('conversa_detalhe', pk=pk)


@login_required
def conversa_transferir(request, pk):
    conversa = get_object_or_404(Conversa, pk=pk)
    if not (is_gestor(request.user) or usuario_responsavel(conversa, request.user)):
        messages.error(request, 'A transferência direta só pode ser feita pelo responsável atual, supervisor ou administrador.')
        return redirect('conversa_detalhe', pk=pk)
    if request.method == 'POST':
        usuario_id = request.POST.get('responsavel')
        novo = get_object_or_404(User, pk=usuario_id, is_active=True)
        conversa.responsavel = novo
        conversa.status = 'EM_ATENDIMENTO'
        conversa.save()
        messages.success(request, f'Atendimento transferido para {novo.get_full_name() or novo.username}.')
    return redirect('conversa_detalhe', pk=pk)


@login_required
def conversa_aguardar(request, pk):
    conversa = get_object_or_404(Conversa, pk=pk)
    if not pode_interagir_conversa(conversa, request.user):
        messages.error(request, 'Apenas o responsável pode alterar o status deste atendimento.')
        return redirect('conversa_detalhe', pk=pk)
    conversa.status = 'AGUARDANDO'
    conversa.atualizada_em = timezone.now()
    conversa.save()
    messages.success(request, 'Atendimento marcado como aguardando retorno do contato.')
    return redirect('conversa_detalhe', pk=pk)


@login_required
def conversa_finalizar(request, pk):
    conversa = get_object_or_404(Conversa, pk=pk)
    if not pode_interagir_conversa(conversa, request.user):
        messages.error(request, 'Apenas o responsável pelo atendimento pode finalizar esta conversa.')
        return redirect('conversa_detalhe', pk=pk)
    conversa.status = 'FINALIZADA'
    conversa.finalizada_em = timezone.now()
    conversa.save()
    messages.success(request, 'Atendimento finalizado.')
    return redirect('conversas')


@login_required
def conversa_solicitar_transferencia(request, pk):
    conversa = get_object_or_404(Conversa, pk=pk)
    if pode_interagir_conversa(conversa, request.user):
        messages.info(request, 'Você já pode interagir com este atendimento.')
        return redirect('conversa_detalhe', pk=pk)
    if conversa.status == 'FINALIZADA':
        messages.error(request, 'Atendimento finalizado. Reabra o atendimento antes de solicitar transferência.')
        return redirect('conversa_detalhe', pk=pk)
    solicitante = request.user.get_full_name() or request.user.username
    responsavel = conversa.responsavel.get_full_name() if conversa.responsavel else ''
    if conversa.responsavel and not responsavel:
        responsavel = conversa.responsavel.username
    texto = f'[SOLICITAÇÃO INTERNA] {solicitante} solicitou a transferência deste atendimento.'
    if responsavel:
        texto += f' Responsável atual: {responsavel}.'
    # Registra como mensagem recebida/interna para que o responsável atual veja a solicitação
    # no histórico e também receba indicador de mensagem nova na lista de conversas.
    MensagemConversa.objects.create(
        conversa=conversa,
        usuario=request.user,
        direcao='RECEBIDA',
        tipo='TEXTO',
        texto=texto,
        lida=False
    )
    conversa.status = 'TRANSFERENCIA_SOLICITADA'
    conversa.atualizada_em = timezone.now()
    conversa.save()
    messages.success(request, 'Solicitação de transferência enviada ao responsável e registrada no histórico.')
    return redirect('conversa_detalhe', pk=pk)


@login_required
def conversa_reabrir(request, pk):
    conversa = get_object_or_404(Conversa, pk=pk)
    conversa.status = 'EM_ATENDIMENTO'
    conversa.finalizada_em = None
    if not conversa.responsavel:
        conversa.responsavel = request.user
    conversa.save()
    messages.success(request, 'Atendimento reaberto.')
    return redirect('conversa_detalhe', pk=pk)


@login_required
def whatsapp_api_config(request):
    if not is_admin(request.user):
        messages.error(request, 'Acesso restrito ao administrador.')
        return redirect('dashboard')
    config = get_whatsapp_config()
    if request.method == 'POST':
        form = WhatsAppConfigForm(request.POST, instance=config)
        if form.is_valid():
            config = form.save()
            registrar_log_whatsapp(
                evento='CONFIG',
                status='SUCESSO',
                resumo='Configuração da WhatsApp API atualizada.',
                payload=f'Número: {config.numero} | Phone Number ID: {config.phone_number_id} | Status: {config.get_status_display()}',
                resposta='Configuração salva no Tower WhatsApp Center.',
                usuario=request.user,
                config=config,
            )
            messages.success(request, 'Configuração da WhatsApp API salva com sucesso.')
            return redirect('whatsapp_api_config')
    else:
        form = WhatsAppConfigForm(instance=config)
    logs = WhatsAppIntegrationLog.objects.select_related('criado_por', 'config').order_by('-criado_em')[:12]
    return render(request, 'core/whatsapp_api_config.html', {'form': form, 'config': config, 'logs': logs})


@login_required
def whatsapp_api_logs(request):
    if not is_admin(request.user):
        messages.error(request, 'Acesso restrito ao administrador.')
        return redirect('dashboard')
    logs = WhatsAppIntegrationLog.objects.select_related('criado_por', 'config').order_by('-criado_em')[:200]
    return render(request, 'core/whatsapp_api_logs.html', {'logs': logs})


@login_required
def whatsapp_api_testar(request):
    if not is_admin(request.user):
        messages.error(request, 'Acesso restrito ao administrador.')
        return redirect('dashboard')
    config = get_whatsapp_config()
    if config.status == 'AGUARDANDO_VERIFICACAO':
        status = 'PENDENTE'
        resumo = 'Número cadastrado, aguardando verificação na Meta.'
        resposta = 'O número +55 35 3606-5528 ainda precisa concluir a validação por ligação.'
        messages.warning(request, 'A configuração está preparada, mas o número ainda aguarda verificação na Meta.')
    elif not config.access_token:
        status = 'PENDENTE'
        resumo = 'Token da API ainda não informado.'
        resposta = 'Após gerar o token permanente na Meta, cole-o na tela de configuração.'
        messages.warning(request, 'Token da API ainda não informado.')
    else:
        status = 'SIMULADO'
        resumo = 'Teste local realizado sem chamada real à Meta.'
        resposta = 'Ambiente local/teste. A chamada real será habilitada quando o webhook HTTPS e o token estiverem prontos.'
        messages.success(request, 'Teste local registrado. A chamada real será feita na etapa de produção com HTTPS.')
    registrar_log_whatsapp(evento='TESTE', status=status, resumo=resumo, payload=f'Phone Number ID: {config.phone_number_id}', resposta=resposta, usuario=request.user, config=config)
    return redirect('whatsapp_api_config')


@csrf_exempt
def whatsapp_webhook(request):
    # Endpoint reservado para a Etapa 18.2.
    # A Meta validará este endereço quando o sistema estiver publicado com HTTPS.
    from django.http import JsonResponse, HttpResponse
    if request.method == 'GET':
        verify_token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        config = WhatsAppConfig.objects.filter(ativo=True).first()
        if config and verify_token and verify_token == config.webhook_verify_token:
            return HttpResponse(challenge or '')
        return HttpResponse('Token de verificação inválido', status=403)
    registrar_log_whatsapp(evento='WEBHOOK', status='SIMULADO', resumo='Webhook recebido em ambiente local/teste.', payload=str(request.body[:2000]), resposta='Recebido sem processamento real nesta etapa.')
    return JsonResponse({'status': 'received', 'mode': 'local_test'})
