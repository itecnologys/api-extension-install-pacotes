# Configuração de Whitelist Snort - Traefik e Carbonio

## ⚠️ CRÍTICO: Configuração Necessária

O Snort pode bloquear conexões do Traefik e Carbonio durante:
- Renovação de certificados Let's Encrypt (Traefik)
- Conexões persistentes do Traefik
- Tráfego de email do Carbonio

**É ESSENCIAL adicionar esses IPs à whitelist do Snort!**

---

## 📋 Passo 1: Adicionar IPs ao Alias

### IPs que devem estar na whitelist:
- **Traefik**: `10.10.10.105/32`
- **Carbonio**: `10.10.10.108/32`

### Instruções:

1. **Acesse a interface web do pfSense:**
   ```
   https://firewall.itecnologys.com
   ```

2. **Vá em: Firewall > Aliases**

3. **Encontre o alias: `SNORT_TRUSTED_IPS`**

4. **Clique em: Edit** (ícone de lápis)

5. **Adicione os seguintes IPs:**
   - `10.10.10.105/32` (Traefik)
   - `10.10.10.108/32` (Carbonio)
   
   **Nota:** Se já existir um range `10.10.10.0/24`, os IPs já estão incluídos, mas é melhor adicionar explicitamente para garantir.

6. **Clique em: Save**

---

## 📋 Passo 2: Verificar/Criar Pass List no Snort

### Opção A: Usar Pass List Existente

Se já existe a Pass List `SSH_Cloudflare_Hetzner_Whitelist`:

1. **Vá em: Services > Snort > Pass Lists**

2. **Encontre: `SSH_Cloudflare_Hetzner_Whitelist`**

3. **Clique em: Edit**

4. **Verifique se o alias `SNORT_TRUSTED_IPS` está selecionado em "Assigned Aliases"**

5. **Se não estiver, selecione e clique em: Save**

### Opção B: Criar Nova Pass List

1. **Vá em: Services > Snort > Pass Lists**

2. **Clique em: Add** (botão verde)

3. **Configure:**
   - **Name:** `Traefik_Carbonio_Whitelist`
   - **Assigned Aliases:** Selecione `SNORT_TRUSTED_IPS`
   - **Auto Generated IP Addresses:** Marque conforme necessário

4. **Clique em: Save**

---

## 📋 Passo 3: Associar Pass List às Interfaces do Snort

⚠️ **IMPORTANTE:** Este passo deve ser feito para **TODAS** as interfaces onde o Snort está ativo!

1. **Vá em: Services > Snort > Interfaces**

2. **Para cada interface listada (ex: `lan`, `wan`, etc.):**
   
   a. **Clique no ícone de Edit** (lápis) da interface
   
   b. **Role até a seção:** "Choose the Networks Snort Should Inspect and Whitelist"
   
   c. **No campo "Pass List", selecione:**
      - `SSH_Cloudflare_Hetzner_Whitelist` (se existir)
      - OU `Traefik_Carbonio_Whitelist` (se criou nova)
   
   d. **Clique em: Save**
   
   e. **Repita para TODAS as interfaces ativas**

---

## 📋 Passo 4: Reiniciar o Snort

Após configurar a Pass List em todas as interfaces, é **ESSENCIAL** reiniciar o Snort:

### Opção A: Reiniciar por Interface

1. **Em: Services > Snort > Interfaces**

2. **Para cada interface configurada:**
   - Clique no ícone de **Restart** (seta circular)
   - Aguarde a confirmação de reinício

### Opção B: Reiniciar Serviço Completo

1. **Vá em: Status > Services**

2. **Procure por: `snort`**

3. **Clique em: Restart**

---

## ✅ Verificação Final

Após completar todos os passos, verifique:

1. **Teste de conexão Traefik:**
   ```bash
   curl -k https://10.10.10.105:9055 -H "Host: mail.ligbox.com.br"
   ```
   - Deve funcionar sem bloqueios

2. **Teste de renovação de certificado:**
   - O Traefik deve conseguir renovar certificados Let's Encrypt
   - Verifique logs: `docker logs traefik | grep -i certificate`

3. **Teste de email:**
   - Envio e recebimento devem funcionar normalmente
   - Verifique logs do Carbonio se houver problemas

4. **Verificar logs do Snort:**
   - Vá em: Services > Snort > Alerts
   - Não deve haver bloqueios dos IPs configurados

---

## 🔧 Troubleshooting

### Problema: Snort ainda está bloqueando

**Soluções:**
1. Verifique se o alias `SNORT_TRUSTED_IPS` contém os IPs corretos
2. Verifique se a Pass List está associada a **TODAS** as interfaces ativas
3. Verifique se o Snort foi reiniciado após as mudanças
4. Verifique os logs do Snort em: Services > Snort > Alerts

### Problema: Traefik não consegue renovar certificados

**Soluções:**
1. Verifique se `10.10.10.105/32` está no alias
2. Verifique se a Pass List está configurada na interface WAN
3. Verifique logs do Traefik: `docker logs traefik | tail -100`

### Problema: Email não funciona

**Soluções:**
1. Verifique se `10.10.10.108/32` está no alias
2. Verifique se a Pass List está configurada na interface WAN
3. Verifique logs do Carbonio

---

## 📝 Resumo dos IPs na Whitelist

Após configurar, os seguintes IPs/ranges estarão na whitelist:

### IPs Específicos:
- `10.10.10.105/32` - Traefik (VM 105)
- `10.10.10.108/32` - Carbonio (VM 108)

### Ranges Existentes:
- `51.171.219.218/20` - IP local Cursor/IDE
- `95.216.14.0/24` - Range Hetzner
- `95.216.14.146/32` - IP específico Hetzner
- `95.216.14.146/32` - IP específico Hetzner
- 15 ranges da Cloudflare

---

## ⚠️ Notas Importantes

1. **SEMPRE reinicie o Snort** após modificar Pass Lists
2. **Configure em TODAS as interfaces** onde o Snort está ativo
3. **Use IPs específicos (/32)** para garantir que não há ambiguidade
4. **Monitore os logs** após configurar para garantir que está funcionando

---

**Data:** 2025-01-14  
**Autor:** Auto Assistant - itecnologys.com

