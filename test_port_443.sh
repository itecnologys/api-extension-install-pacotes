#!/bin/bash
# Script para testar se a porta 443 está aberta para o IP 95.216.14.162

IP="95.216.14.162"
PORT="443"
TIMEOUT=5

echo "═══════════════════════════════════════════════════════════════════════════"
echo "TESTE DE CONECTIVIDADE - PORTA 443"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "IP: $IP"
echo "Porta: $PORT"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Teste 1: Teste básico de conectividade TCP
echo "1. Teste de conectividade TCP..."
if timeout $TIMEOUT bash -c "echo > /dev/tcp/$IP/$PORT" 2>/dev/null; then
    echo -e "${GREEN}✅ Porta 443 está ABERTA (conectividade TCP OK)${NC}"
    TCP_OK=true
else
    echo -e "${RED}❌ Porta 443 está FECHADA ou inacessível (timeout TCP)${NC}"
    TCP_OK=false
fi

# Teste 2: Teste com nc (netcat) se disponível
echo ""
echo "2. Teste com netcat (nc)..."
if command -v nc &> /dev/null; then
    if timeout $TIMEOUT nc -zv $IP $PORT 2>&1 | grep -q "succeeded\|open"; then
        echo -e "${GREEN}✅ Porta 443 está ABERTA (nc confirma)${NC}"
    else
        echo -e "${RED}❌ Porta 443 está FECHADA (nc confirma)${NC}"
        nc -zv $IP $PORT 2>&1 | head -1
    fi
else
    echo -e "${YELLOW}⚠️  netcat (nc) não está disponível${NC}"
fi

# Teste 3: Teste com curl HTTPS
echo ""
echo "3. Teste com curl HTTPS..."
HTTP_CODE=$(timeout $TIMEOUT curl -k -s -o /dev/null -w "%{http_code}" --connect-timeout $TIMEOUT https://$IP:$PORT 2>/dev/null)
if [ ! -z "$HTTP_CODE" ] && [ "$HTTP_CODE" != "000" ]; then
    echo -e "${GREEN}✅ Porta 443 está ABERTA (curl retornou HTTP $HTTP_CODE)${NC}"
    CURL_OK=true
else
    echo -e "${RED}❌ Porta 443 está FECHADA ou não responde HTTPS (curl falhou)${NC}"
    CURL_OK=false
    # Mostrar erro detalhado
    timeout $TIMEOUT curl -k -v https://$IP:$PORT 2>&1 | grep -i "failed\|timeout\|refused" | head -3
fi

# Teste 4: Teste com openssl
echo ""
echo "4. Teste com openssl (handshake SSL)..."
if timeout $TIMEOUT openssl s_client -connect $IP:$PORT -servername $IP < /dev/null 2>&1 | grep -q "Verify return code"; then
    echo -e "${GREEN}✅ Porta 443 está ABERTA (openssl handshake OK)${NC}"
    SSL_OK=true
else
    echo -e "${RED}❌ Porta 443 está FECHADA ou não aceita SSL (openssl falhou)${NC}"
    SSL_OK=false
    timeout $TIMEOUT openssl s_client -connect $IP:$PORT -servername $IP < /dev/null 2>&1 | grep -i "error\|timeout\|refused" | head -3
fi

# Teste 5: Teste via telnet (se disponível)
echo ""
echo "5. Teste com telnet..."
if command -v telnet &> /dev/null; then
    if timeout $TIMEOUT telnet $IP $PORT 2>&1 | grep -q "Connected\|Escape"; then
        echo -e "${GREEN}✅ Porta 443 está ABERTA (telnet conectou)${NC}"
    else
        echo -e "${RED}❌ Porta 443 está FECHADA (telnet não conectou)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  telnet não está disponível${NC}"
fi

# Resumo
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "RESUMO"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

if [ "$TCP_OK" = true ] || [ "$CURL_OK" = true ] || [ "$SSL_OK" = true ]; then
    echo -e "${GREEN}✅ CONCLUSÃO: Porta 443 está ABERTA para $IP${NC}"
    echo ""
    echo "📋 Próximos passos:"
    echo "   1. Teste acesso via domínio: https://mail.ligbox.com.br"
    echo "   2. Verifique se o Traefik está roteando corretamente"
    echo "   3. Verifique logs do Traefik se houver problemas"
else
    echo -e "${RED}❌ CONCLUSÃO: Porta 443 está FECHADA ou inacessível para $IP${NC}"
    echo ""
    echo "📋 Possíveis causas:"
    echo "   1. Port forward não está funcionando no pfSense"
    echo "   2. Regra de firewall bloqueando"
    echo "   3. Traefik não está escutando na porta 9055"
    echo "   4. Problema de rede/firewall externo"
    echo ""
    echo "🔧 Verificações recomendadas:"
    echo "   1. Verifique port forwards no pfSense: Firewall > NAT > Port Forward"
    echo "   2. Verifique regras WAN: Firewall > Rules > WAN"
    echo "   3. Verifique se Traefik está rodando: docker ps | grep traefik"
    echo "   4. Teste acesso interno: curl -k https://10.10.10.105:9055"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"

