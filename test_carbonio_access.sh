#!/bin/bash
# Script de teste para verificar acesso ao Carbonio via Traefik

echo "═══════════════════════════════════════════════════════════════════════════"
echo "TESTE DE ACESSO AO CARBONIO VIA TRAEFIK"
echo "═══════════════════════════════════════════════════════════════════════════"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "1. Testando acesso direto ao Carbonio (10.10.10.108:443)..."
if curl -k -s -o /dev/null -w "%{http_code}" https://10.10.10.108:443 | grep -q "200\|301\|302"; then
    echo -e "${GREEN}✅ Carbonio responde diretamente${NC}"
else
    echo -e "${RED}❌ Carbonio não responde diretamente${NC}"
fi

echo ""
echo "2. Testando acesso via Traefik (10.10.10.105:9055)..."
if curl -k -s -o /dev/null -w "%{http_code}" -H "Host: mail.ligbox.com.br" https://10.10.10.105:9055 | grep -q "200\|301\|302"; then
    echo -e "${GREEN}✅ Traefik responde na porta custom${NC}"
else
    echo -e "${RED}❌ Traefik não responde na porta custom${NC}"
fi

echo ""
echo "3. Testando acesso via Traefik HTTP (10.10.10.105:8055)..."
if curl -s -o /dev/null -w "%{http_code}" -H "Host: mail.ligbox.com.br" http://10.10.10.105:8055 | grep -q "200\|301\|302"; then
    echo -e "${GREEN}✅ Traefik HTTP responde${NC}"
else
    echo -e "${RED}❌ Traefik HTTP não responde${NC}"
fi

echo ""
echo "4. Testando acesso via domínio (mail.ligbox.com.br)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://mail.ligbox.com.br)
if echo "$HTTP_CODE" | grep -q "200\|301\|302"; then
    echo -e "${GREEN}✅ Domínio responde (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${YELLOW}⚠️  Domínio retornou HTTP $HTTP_CODE${NC}"
    echo "   (Pode estar funcionando mas com redirecionamento)"
fi

echo ""
echo "5. Verificando certificado SSL..."
if echo | openssl s_client -connect mail.ligbox.com.br:443 -servername mail.ligbox.com.br 2>/dev/null | grep -q "Verify return code: 0"; then
    echo -e "${GREEN}✅ Certificado SSL válido${NC}"
else
    echo -e "${YELLOW}⚠️  Certificado SSL pode ter problemas${NC}"
fi

echo ""
echo "6. Testando redirecionamento HTTP → HTTPS..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -L http://mail.ligbox.com.br)
if echo "$HTTP_CODE" | grep -q "200\|301\|302"; then
    echo -e "${GREEN}✅ Redirecionamento HTTP funciona${NC}"
else
    echo -e "${YELLOW}⚠️  Redirecionamento HTTP retornou $HTTP_CODE${NC}"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "TESTES CONCLUÍDOS"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "📋 Para testar portas externas, use:"
echo "   https://canyouseeme.org"
echo "   IP: 95.216.14.162"
echo "   Portas: 80 e 443"
echo ""

