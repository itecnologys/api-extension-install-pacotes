#!/bin/bash
# Script para analisar configuração do Traefik e verificar se está escutando

echo "═══════════════════════════════════════════════════════════════════════════"
echo "ANÁLISE: TRAEFIK E CONFIGURAÇÃO PARA mail.ligbox.com.br"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

TRAEFIK_IP="10.10.10.105"
TRAEFIK_HTTPS_PORT="9055"
TRAEFIK_HTTP_PORT="8055"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "1. Testando se Traefik está escutando na porta 9055..."
if timeout 3 bash -c "echo > /dev/tcp/$TRAEFIK_IP/$TRAEFIK_HTTPS_PORT" 2>/dev/null; then
    echo -e "${GREEN}✅ Traefik está escutando na porta 9055${NC}"
else
    echo -e "${RED}❌ Traefik NÃO está escutando na porta 9055${NC}"
fi

echo ""
echo "2. Testando acesso direto ao Traefik (sem Host header)..."
HTTP_CODE=$(timeout 5 curl -k -s -o /dev/null -w "%{http_code}" https://$TRAEFIK_IP:$TRAEFIK_HTTPS_PORT 2>/dev/null)
if [ ! -z "$HTTP_CODE" ] && [ "$HTTP_CODE" != "000" ]; then
    echo -e "${GREEN}✅ Traefik responde (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ Traefik não responde${NC}"
fi

echo ""
echo "3. Testando acesso com Host header mail.ligbox.com.br..."
HTTP_CODE=$(timeout 5 curl -k -s -o /dev/null -w "%{http_code}" -H "Host: mail.ligbox.com.br" https://$TRAEFIK_IP:$TRAEFIK_HTTPS_PORT 2>/dev/null)
if [ ! -z "$HTTP_CODE" ] && [ "$HTTP_CODE" != "000" ]; then
    echo -e "${GREEN}✅ Traefik roteia para mail.ligbox.com.br (HTTP $HTTP_CODE)${NC}"
    
    # Mostrar resposta completa
    echo ""
    echo "   Resposta completa:"
    timeout 5 curl -k -s -I -H "Host: mail.ligbox.com.br" https://$TRAEFIK_IP:$TRAEFIK_HTTPS_PORT 2>/dev/null | head -10
else
    echo -e "${RED}❌ Traefik NÃO roteia para mail.ligbox.com.br${NC}"
    echo ""
    echo "   Possíveis causas:"
    echo "   - Traefik não tem configuração para mail.ligbox.com.br"
    echo "   - Backend (Carbonio) não está acessível"
    echo "   - Certificado SSL não configurado para este domínio"
fi

echo ""
echo "4. Testando acesso HTTP (porta 8055)..."
HTTP_CODE=$(timeout 5 curl -s -o /dev/null -w "%{http_code}" -H "Host: mail.ligbox.com.br" http://$TRAEFIK_IP:$TRAEFIK_HTTP_PORT 2>/dev/null)
if [ ! -z "$HTTP_CODE" ] && [ "$HTTP_CODE" != "000" ]; then
    echo -e "${GREEN}✅ Traefik HTTP responde (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ Traefik HTTP não responde${NC}"
fi

echo ""
echo "5. Testando acesso direto ao Carbonio..."
HTTP_CODE=$(timeout 5 curl -k -s -o /dev/null -w "%{http_code}" https://10.10.10.108:443 2>/dev/null)
if [ ! -z "$HTTP_CODE" ] && [ "$HTTP_CODE" != "000" ]; then
    echo -e "${GREEN}✅ Carbonio responde diretamente (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ Carbonio não responde diretamente${NC}"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "CONCLUSÃO"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "Se outros apps funcionam na porta 443, significa que:"
echo "1. ✅ O port forward ID 20 está funcionando"
echo "2. ✅ O Traefik está recebendo tráfego"
echo "3. ⚠️  O problema é específico para mail.ligbox.com.br"
echo ""
echo "Possíveis causas:"
echo "- Traefik não tem rota configurada para mail.ligbox.com.br"
echo "- Backend do Carbonio não está configurado corretamente no Traefik"
echo "- Certificado SSL não está configurado para mail.ligbox.com.br"
echo "- Problema de DNS interno"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"

