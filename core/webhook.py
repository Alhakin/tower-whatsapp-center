from django.utils import timezone
from .models import Conversa, MensagemConversa, WhatsAppIntegrationLog, WhatsAppConfig


def _get_texto_mensagem(message):
    tipo = message.get("type", "")

    if tipo == "text":
        return message.get("text", {}).get("body", ""), "TEXTO"

    if tipo == "image":
        return message.get("image", {}).get("caption", ""), "IMAGEM"

    if tipo == "document":
        return message.get("document", {}).get("caption", ""), "DOCUMENTO"

    if tipo == "audio":
        return "", "AUDIO"

    return f"Mensagem recebida do tipo: {tipo}", "TEXTO"


def processar_evento(payload):
    config = WhatsAppConfig.objects.filter(ativo=True).first()

    try:
        entries = payload.get("entry", [])

        for entry in entries:
            changes = entry.get("changes", [])

            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                contacts = value.get("contacts", [])

                contato_nome = ""
                if contacts:
                    contato_nome = contacts[0].get("profile", {}).get("name", "")

                for msg in messages:
                    telefone = msg.get("from", "")
                    meta_message_id = msg.get("id", "")
                    texto, tipo = _get_texto_mensagem(msg)

                    conversa, criada = Conversa.objects.get_or_create(
                        telefone=telefone,
                        defaults={
                            "nome": contato_nome or telefone,
                            "status": "ABERTA",
                        }
                    )

                    if contato_nome and not conversa.nome:
                        conversa.nome = contato_nome

                    conversa.status = "ABERTA"
                    conversa.atualizada_em = timezone.now()
                    conversa.save()

                    MensagemConversa.objects.create(
                        conversa=conversa,
                        usuario=None,
                        direcao="RECEBIDA",
                        tipo=tipo,
                        texto=texto,
                        lida=False,
                        status_entrega="ENTREGUE",
                        meta_message_id=meta_message_id,
                    )

        WhatsAppIntegrationLog.objects.create(
            config=config,
            evento="WEBHOOK",
            status="SUCESSO",
            resumo="Webhook processado com sucesso.",
            payload=str(payload)[:5000],
            resposta="Mensagens recebidas registradas no sistema.",
        )

        return {"processed": True, "reason": "Webhook processado com sucesso."}

    except Exception as e:
        WhatsAppIntegrationLog.objects.create(
            config=config,
            evento="ERRO",
            status="FALHA",
            resumo="Erro ao processar webhook.",
            payload=str(payload)[:5000],
            resposta=str(e),
        )

        return {"processed": False, "reason": str(e)}
