# Configuração de Whitelist no Snort - Guia Completo

## ✅ Status Atual

- **Alias criado via API**: `SNORT_TRUSTED_IPS` ✅
- **IPs configurados**: 19 ranges/IPs incluindo:
  - IP local Cursor/IDE: `51.171.219.218/20`
  - IPs Hetzner: `95.216.14.0/24`, `95.216.14.146`, `95.216.14.146`
  - Ranges Cloudflare: 15 ranges principais

## 📋 Passo a Passo - Configuração Manual

### PASSO 1: Verificar Alias Criado

1. Acesse: **https://firewall.itecnologys.com**
2. Faça login com suas credenciais
3. Vá em: **Firewall** > **Aliases**
4. Procure pelo alias: **`SNORT_TRUSTED_IPS`**
5. Verifique se contém todos os IPs listados abaixo

**IPs que devem estar no alias:**
```
51.171.219.218/20          # IP local Cursor/IDE
95.216.14.0/24             # Range Hetzner
95.216.14.146/32           # IP específico Hetzner
95.216.14.146/32           # IP específico Hetzner
173.245.48.0/20            # Cloudflare
103.21.244.0/22            # Cloudflare
103.22.200.0/22            # Cloudflare
103.31.4.0/22              # Cloudflare
141.101.64.0/18            # Cloudflare
108.162.192.0/18           # Cloudflare
190.93.240.0/20            # Cloudflare
188.114.96.0/20            # Cloudflare
197.234.240.0/22           # Cloudflare
198.41.128.0/17            # Cloudflare
162.158.0.0/15             # Cloudflare
104.16.0.0/13              # Cloudflare
104.24.0.0/14              # Cloudflare
172.64.0.0/13              # Cloudflare
131.0.72.0/22              # Cloudflare
```

---

### PASSO 2: Criar Pass List no Snort

1. Acesse: **Services** > **Snort**
2. Vá na aba: **Pass Lists**
3. Clique em: **Add** (botão verde no canto superior direito)
4. Configure os seguintes campos:

   **Name:**
   ```
   SSH_Cloudflare_Hetzner_Whitelist
   ```

   **Assigned Aliases:**
   - Selecione: **`SNORT_TRUSTED_IPS`**
   - (Este é o alias que criamos anteriormente)

   **Auto Generated IP Addresses:**
   - Marque as opções conforme necessário
   - Geralmente: marque "Auto Generated IP Addresses" se quiser incluir IPs gerados automaticamente

5. Clique em: **Save** (botão no final da página)

---

### PASSO 3: Associar Pass List às Interfaces do Snort

⚠️ **IMPORTANTE**: Este passo deve ser feito para **TODAS** as interfaces onde o Snort está ativo (LAN, WAN, etc.)

1. Ainda em: **Services** > **Snort**
2. Vá na aba: **Interfaces**
3. Para cada interface listada (ex: `lan`, `wan`, etc.):
   
   a. Clique no ícone de **Edit** (lápis) da interface
   
   b. Role até a seção: **"Choose the Networks Snort Should Inspect and Whitelist"**
   
   c. No campo **Pass List**, selecione:
      ```
      SSH_Cloudflare_Hetzner_Whitelist
      ```
   
   d. **IMPORTANTE**: Verifique também outras configurações:
      - Certifique-se de que a interface está **Enabled**
      - Verifique as regras de detecção se necessário
   
   e. Clique em: **Save** (no final da página)

4. Repita o processo para **todas as interfaces** onde o Snort está ativo

---

### PASSO 4: Reiniciar o Snort

Após configurar a Pass List em todas as interfaces, é **ESSENCIAL** reiniciar o Snort para aplicar as mudanças.

#### Opção A: Reiniciar por Interface

1. Em: **Services** > **Snort** > **Interfaces**
2. Para cada interface configurada:
   - Clique no ícone de **Restart** (seta circular)
   - Aguarde a confirmação de reinício

#### Opção B: Reiniciar Serviço Completo

1. Vá em: **Status** > **Services**
2. Procure por: **snort**
3. Clique em: **Restart**

---

## ✅ Verificação Final

Após completar todos os passos, verifique:

1. **Teste de Conexão SSH:**
   ```bash
   # Tente conectar via SSH do seu IP local
   ssh usuario@firewall.itecnologys.com
   ```

2. **Verificar Logs do Snort:**
   - Vá em: **Services** > **Snort** > **Alerts**
   - Verifique se não há bloqueios dos IPs configurados

3. **Monitorar por alguns minutos:**
   - Faça algumas conexões SSH
   - Acesse serviços web
   - Verifique se não há bloqueios

---

## 🔧 Troubleshooting

### Problema: Ainda está bloqueando

**Soluções:**
1. Verifique se o alias `SNORT_TRUSTED_IPS` contém todos os IPs corretos
2. Verifique se a Pass List está associada a **TODAS** as interfaces ativas
3. Verifique se o Snort foi reiniciado após as mudanças
4. Verifique os logs do Snort em: **Services** > **Snort** > **Alerts**

### Problema: Não consigo acessar a interface web

**Soluções:**
1. Verifique se seu IP está no alias `IPs_Acesso_Web_Permitidos`
2. Tente acessar de outro IP que esteja na whitelist
3. Verifique regras de firewall do pfSense

### Problema: Pass List não aparece nas interfaces

**Soluções:**
1. Verifique se a Pass List foi salva corretamente
2. Tente criar novamente a Pass List
3. Verifique se o alias está correto

---

## 📝 Notas Importantes

1. **Ranges vs IPs Específicos:**
   - Use ranges (ex: `/20`, `/24`) quando possível para cobrir mais IPs
   - Use IPs específicos (ex: `/32`) apenas quando necessário

2. **Cloudflare:**
   - Os ranges da Cloudflare podem mudar ao longo do tempo
   - Consulte: https://www.cloudflare.com/ips/ para ranges atualizados

3. **Manutenção:**
   - Revise periodicamente os IPs na whitelist
   - Adicione novos IPs conforme necessário
   - Remova IPs que não são mais necessários

---

## 🚀 Scripts Disponíveis

- **`pfsense_snort_whitelist.py`**: Cria/atualiza o alias via API
- Execute periodicamente para garantir que o alias está atualizado

---

**Última atualização**: 2025-01-14
**Autor**: Auto Assistant - itecnologys.com

