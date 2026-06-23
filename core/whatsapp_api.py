from dataclasses import dataclass
import requests


@dataclass
class WhatsAppSendResult:
    success: bool
    status: str
    message_id: str = ''
    error: str = ''
    response_text: str = ''


def enviar_texto(config, destino: str, texto: str) -> WhatsAppSendResult:
    if not config or config.status != 'CONECTADO' or not config.access_token or not config.phone_number_id:
        return WhatsAppSendResult(
            success=False,
            status='SIMULADA',
            error='Configuração incompleta ou API ainda não conectada. Nenhuma chamada real foi feita à Meta.'
        )

    url = f"https://graph.facebook.com/v20.0/{config.phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {config.access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": destino,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": texto,
        },
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json() if response.content else {}

        if response.status_code in [200, 201]:
            message_id = ''
            try:
                message_id = data.get("messages", [{}])[0].get("id", "")
            except Exception:
                message_id = ''

            return WhatsAppSendResult(
                success=True,
                status='ENVIADA',
                message_id=message_id,
                response_text=str(data),
            )

        return WhatsAppSendResult(
            success=False,
            status='FALHA',
            error=str(data),
            response_text=str(data),
        )

    except Exception as e:
        return WhatsAppSendResult(
            success=False,
            status='FALHA',
            error=str(e),
            response_text=str(e),
        )
