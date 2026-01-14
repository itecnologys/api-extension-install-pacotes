# Instruções para Reinstalar o Snort no pfSense

## 🔍 Problema Identificado

O pacote `pfSense-pkg-snort` está instalado, mas o serviço **não aparece** no menu `Services > Snort` do pfSense, mesmo após reboot.

## ✅ Solução: Reinstalação Completa

### Método 1: Via Interface Web (RECOMENDADO)

1. **Acesse a interface web do pfSense:**
   ```
   https://firewall.itecnologys.com
   ```

2. **Remover o pacote existente:**
   - Vá em: **System** > **Package Manager** > **Installed Packages**
   - Procure por: **pfSense-pkg-snort**
   - Clique no botão **Remove** (ícone de lixeira)
   - Aguarde a remoção completar (pode levar alguns minutos)

3. **Reinstalar o pacote:**
   - Vá em: **Available Packages**
   - No campo de busca, digite: **Snort**
   - Clique em: **Search**
   - Encontre: **pfSense-pkg-snort**
   - Clique no botão **Install**
   - Aguarde a instalação completar (pode levar 5-10 minutos)

4. **REBOOT COMPLETO do pfSense:**
   - Vá em: **System** > **Reboot**
   - Clique em: **Yes** para confirmar
   - Aguarde o sistema reiniciar completamente (2-5 minutos)

5. **Verificar após reboot:**
   - Após o login, vá em: **Services** > **Snort**
   - O serviço deve aparecer agora!

---

### Método 2: Via Console/SSH (Alternativo)

Se você tiver acesso SSH ao pfSense:

1. **Conectar via SSH:**
   ```bash
   ssh root@firewall.itecnologys.com
   ```

2. **Verificar pacote instalado:**
   ```bash
   pkg info | grep snort
   ```

3. **Remover o pacote:**
   ```bash
   pkg remove -y pfSense-pkg-snort
   ```

4. **Atualizar repositórios:**
   ```bash
   pkg update -f
   ```

5. **Reinstalar o pacote:**
   ```bash
   pkg install -y pfSense-pkg-snort
   ```

6. **Verificar dependências:**
   ```bash
   pkg check -d
   ```

7. **Se houver problema com libpcap (comum):**
   ```bash
   ln -s /usr/lib/libpcap.so /usr/lib/libpcap.so.1
   ```

8. **Reiniciar o pfSense:**
   ```bash
   reboot
   ```

---

## 🔧 Troubleshooting

### Problema: Instalação falha com erro de dependências

**Solução:**
1. Atualize os repositórios: `pkg update -f`
2. Verifique dependências: `pkg check -d`
3. Instale dependências faltantes manualmente
4. Tente reinstalar o Snort novamente

### Problema: libpcap não encontrada

**Solução:**
```bash
# Criar link simbólico
ln -s /usr/lib/libpcap.so /usr/lib/libpcap.so.1

# Verificar se funcionou
ls -la /usr/lib/libpcap.so*
```

### Problema: Serviço ainda não aparece após reinstalação

**Soluções:**
1. **Verifique os logs do sistema:**
   - Vá em: **Status** > **System Logs** > **System**
   - Procure por erros relacionados a "snort" ou "pkg"

2. **Verifique se o pacote está realmente instalado:**
   - Vá em: **System** > **Package Manager** > **Installed Packages**
   - Confirme que `pfSense-pkg-snort` aparece na lista

3. **Tente um segundo reboot:**
   - Às vezes é necessário mais de um reboot

4. **Verifique compatibilidade:**
   - Certifique-se de que a versão do pfSense é compatível
   - Verifique: **System** > **Information** > **Version**

---

## 📋 Checklist Pós-Instalação

Após reinstalar e fazer reboot, verifique:

- [ ] O pacote aparece em: **System** > **Package Manager** > **Installed Packages**
- [ ] O serviço aparece em: **Services** > **Snort**
- [ ] É possível acessar: **Services** > **Snort** > **Interfaces**
- [ ] É possível acessar: **Services** > **Snort** > **Pass Lists**
- [ ] Não há erros nos logs do sistema relacionados ao Snort

---

## ⚠️ Importante

1. **SEMPRE faça um reboot completo** após instalar/reinstalar pacotes no pfSense
2. **Aguarde a instalação completar** antes de fazer reboot
3. **Verifique os logs** se houver problemas
4. **Mantenha o pfSense atualizado** para evitar problemas de compatibilidade

---

## 📝 Notas

- O pacote foi removido via API com sucesso
- A reinstalação via API teve timeout (instalação leva muito tempo)
- **Recomendação**: Use a interface web para reinstalar (mais confiável)

---

**Data**: 2025-01-14  
**Autor**: Auto Assistant - itecnologys.com

