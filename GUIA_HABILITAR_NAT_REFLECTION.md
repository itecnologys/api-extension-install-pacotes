# Guia: Habilitar NAT Reflection no Port Forward 443

## ⚠️ PROBLEMA IDENTIFICADO

O port forward 443 (ID 20) **NÃO tem NAT Reflection habilitado**, o que pode causar problemas de acesso externo.

## ✅ VERIFICAÇÃO ATUAL

- **Port Forward 80**: ✅ Configurado corretamente (NAT Reflection habilitado)
- **Port Forward 443**: ⚠️ Configurado mas **NAT Reflection NÃO habilitado**

## 📋 AÇÃO NECESSÁRIA

### Passo 1: Acessar Interface Web do pfSense

1. Acesse: **https://firewall.itecnologys.com**
2. Faça login com: `admin` / `pfsense`

### Passo 2: Editar Port Forward 443

1. Vá em: **Firewall** > **NAT** > **Port Forward**
2. Encontre a regra: **ID 20** - "Traefik Dashboard - proxy.itecnologys.com"
3. Clique no ícone de **Edit** (lápis) dessa regra

### Passo 3: Habilitar NAT Reflection

1. Role até a seção: **"NAT Reflection"**
2. Selecione: **"Enable (Pure NAT)"**
3. Clique em: **Save**

### Passo 4: Aplicar Mudanças

1. Clique em: **Apply Changes** (botão no topo da página)
2. Aguarde a confirmação

## ✅ VERIFICAÇÃO APÓS CORREÇÃO

Execute o script de verificação:

```bash
python3 /root/verificar_configuracao_traefik_carbonio.py
```

Ou teste manualmente:

```bash
# Teste interno (deve continuar funcionando)
curl -k -H "Host: mail.ligbox.com.br" https://10.10.10.105:9055

# Teste externo (deve começar a funcionar)
curl -I https://mail.ligbox.com.br
```

## 📊 STATUS ATUAL

### ✅ Configurado Corretamente:
- Port Forward 80 → Traefik:8055 (NAT Reflection: enable)
- Regras Firewall WAN (80 e 443)
- Cadeia interna funcionando (Traefik → Carbonio)

### ⚠️ Precisa Ajuste:
- Port Forward 443 → Traefik:9055 (NAT Reflection: **None** → precisa ser **enable**)

## 🔍 Por Que NAT Reflection é Importante?

**NAT Reflection** permite que:
- Clientes externos acessem serviços via IP público
- O pfSense redirecione corretamente o tráfego de volta
- Acesso externo funcione mesmo quando o cliente está "fora" da rede

**Sem NAT Reflection:**
- Acesso interno pode funcionar
- Acesso externo pode falhar ou ter problemas

---

**Data**: 2025-01-14  
**Autor**: Auto Assistant - itecnologys.com

