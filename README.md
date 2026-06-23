# Tower WhatsApp Center - Etapa 18.1

Preparação da integração oficial Meta WhatsApp API.

## Dados pré-configurados
- Conexão: LD Cargo
- Número: +55 35 3606-5528
- Phone Number ID: 11239284241451517
- Status inicial: Aguardando verificação

## Incluído
- Menu administrativo WhatsApp API.
- Tela de configuração da conexão.
- Campos para Access Token, Webhook e token de validação.
- Logs técnicos de integração.
- Status de entrega nas mensagens: simulada, fila, enviando, enviada, entregue, lida e falha.
- Endpoint reservado: /api/whatsapp/webhook/
- Estrutura de serviços: whatsapp_api.py, webhook.py, services.py e logs.py.

## Rodar após substituir
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

## Observação
Esta etapa ainda não envia mensagens reais. Ela prepara o sistema para receber o token permanente e o webhook público com HTTPS na próxima fase.
