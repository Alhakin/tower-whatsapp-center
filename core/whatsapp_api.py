"""Camada reservada para a comunicação com a API oficial da Meta WhatsApp.

Etapa 18.1: estrutura preparada, ainda em modo local/teste.
Na Etapa 18.3, esta camada receberá chamadas reais usando o token permanente.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class WhatsAppSendResult:
    success: bool
    status: str
    message_id: str = ''
    error: str = ''


def enviar_texto(config, destino: str, texto: str) -> WhatsAppSendResult:
    if not config or config.status != 'CONECTADO' or not config.access_token:
        return WhatsAppSendResult(
            success=False,
            status='SIMULADA',
            error='Ambiente local/teste ou configuração incompleta. Nenhuma chamada foi feita à Meta.'
        )
    return WhatsAppSendResult(success=False, status='FILA', error='Envio real será habilitado na Etapa 18.3.')
