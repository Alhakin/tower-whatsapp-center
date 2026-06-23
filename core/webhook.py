"""Processadores reservados para eventos recebidos pelo Webhook da Meta.
Etapa 18.1 mantém apenas a estrutura para futura ativação com HTTPS.
"""

def processar_evento(payload):
    return {'processed': False, 'reason': 'Webhook ainda em preparação local/teste'}
