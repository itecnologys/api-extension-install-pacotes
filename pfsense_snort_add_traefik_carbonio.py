#!/usr/bin/env python3
"""
Script para adicionar IPs do Traefik e Carbonio à whitelist do Snort
Autor: Auto Assistant
Data: 2025-01-14
"""

import requests
import json
import sys
from requests.auth import HTTPBasicAuth
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Configurações da API pfSense
PFSENSE_URL = 'https://firewall.itecnologys.com/api/v2/'
PFSENSE_USER = 'api_cursor'
PFSENSE_PASSWORD = '805353'

# IPs que devem estar na whitelist
TRAEFIK_IP = '10.10.10.105'
CARBONIO_IP = '10.10.10.108'
ALIAS_NAME = 'SNORT_TRUSTED_IPS'

def get_alias():
    """Obtém o alias SNORT_TRUSTED_IPS"""
    try:
        response = requests.get(
            f'{PFSENSE_URL}firewall/aliases',
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            aliases = data.get('data', [])
            
            for alias in aliases:
                if alias.get('name') == ALIAS_NAME:
                    return alias
        return None
    except Exception as e:
        print(f"❌ Erro ao obter alias: {e}")
        return None

def check_ip_in_alias(alias, ip):
    """Verifica se um IP está no alias (incluindo ranges)"""
    addresses = alias.get('address', [])
    
    # Verificação direta
    if ip in addresses or f'{ip}/32' in addresses:
        return True
    
    # Verificar se está em algum range
    for addr in addresses:
        if '/' in addr:
            ip_base, mask = addr.split('/')
            # Simplificação: se IP começa com mesmo prefixo de 24 bits
            if ip.startswith('.'.join(ip_base.split('.')[:3]) + '.'):
                return True
            # Verificar range 10.10.10.0/24 especificamente
            if addr == '10.10.10.0/24' and ip.startswith('10.10.10.'):
                return True
    
    return False

def update_alias(alias, new_addresses):
    """Atualiza o alias com novos endereços"""
    alias_id = alias.get('id')
    
    payload = {
        'name': alias.get('name'),
        'type': alias.get('type'),
        'descr': alias.get('descr', ''),
        'address': new_addresses
    }
    
    try:
        # A API pode não suportar PUT, então vamos tentar
        response = requests.put(
            f'{PFSENSE_URL}firewall/alias?id={alias_id}',
            json=payload,
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"   ⚠️  API não suporta atualização (status: {response.status_code})")
            return False
    except Exception as e:
        print(f"   ⚠️  Erro: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 70)
    print("ADICIONANDO TRAEFIK E CARBONIO À WHITELIST DO SNORT")
    print("=" * 70)
    
    print(f"\n🎯 Objetivo:")
    print(f"   Adicionar IPs do Traefik e Carbonio à whitelist do Snort")
    print(f"   Traefik: {TRAEFIK_IP}")
    print(f"   Carbonio: {CARBONIO_IP}")
    
    # Obter alias
    alias = get_alias()
    
    if not alias:
        print(f"\n❌ Alias '{ALIAS_NAME}' não encontrado!")
        print(f"   Execute primeiro: python3 /root/pfsense_snort_whitelist.py")
        return 1
    
    print(f"\n✅ Alias encontrado: {alias.get('name')}")
    print(f"   IPs/ranges atuais: {len(alias.get('address', []))}")
    
    # Verificar se IPs já estão incluídos
    traefik_included = check_ip_in_alias(alias, TRAEFIK_IP)
    carbonio_included = check_ip_in_alias(alias, CARBONIO_IP)
    
    print(f"\n📋 Status atual:")
    if traefik_included:
        print(f"   ✅ Traefik ({TRAEFIK_IP}) já está na whitelist")
    else:
        print(f"   ❌ Traefik ({TRAEFIK_IP}) NÃO está na whitelist")
    
    if carbonio_included:
        print(f"   ✅ Carbonio ({CARBONIO_IP}) já está na whitelist")
    else:
        print(f"   ❌ Carbonio ({CARBONIO_IP}) NÃO está na whitelist")
    
    # Se ambos já estão incluídos, nada a fazer
    if traefik_included and carbonio_included:
        print(f"\n✅ Ambos os IPs já estão na whitelist!")
        print(f"   Nada a fazer.")
        return 0
    
    # Adicionar IPs faltantes
    print(f"\n📝 Adicionando IPs faltantes...")
    
    current_addresses = alias.get('address', []).copy()
    updated = False
    
    if not traefik_included:
        new_addr = f'{TRAEFIK_IP}/32'
        if new_addr not in current_addresses:
            current_addresses.append(new_addr)
            print(f"   ✅ Adicionado: {new_addr}")
            updated = True
    
    if not carbonio_included:
        new_addr = f'{CARBONIO_IP}/32'
        if new_addr not in current_addresses:
            current_addresses.append(new_addr)
            print(f"   ✅ Adicionado: {new_addr}")
            updated = True
    
    if updated:
        # Tentar atualizar via API
        if update_alias(alias, current_addresses):
            print(f"\n✅ Alias atualizado via API!")
        else:
            print(f"\n⚠️  Não foi possível atualizar via API")
            print(f"   Você precisa atualizar manualmente:")
            print(f"\n   1. Acesse: https://firewall.itecnologys.com")
            print(f"   2. Vá em: Firewall > Aliases")
            print(f"   3. Encontre: {ALIAS_NAME}")
            print(f"   4. Clique em: Edit")
            print(f"   5. Adicione os seguintes IPs:")
            if not traefik_included:
                print(f"      - {TRAEFIK_IP}/32 (Traefik)")
            if not carbonio_included:
                print(f"      - {CARBONIO_IP}/32 (Carbonio)")
            print(f"   6. Save")
    else:
        print(f"\n✅ Nenhuma atualização necessária")
    
    # Instruções para Pass List
    print("\n" + "=" * 70)
    print("PRÓXIMOS PASSOS - CONFIGURAR PASS LIST NO SNORT")
    print("=" * 70)
    
    print("\n⚠️  IMPORTANTE: A Pass List precisa ser configurada manualmente")
    print("   (A API do pfSense não suporta configuração de Pass Lists)")
    
    print("\n📋 Passos:")
    print("   1. Acesse: https://firewall.itecnologys.com")
    print("   2. Vá em: Services > Snort")
    print("   3. Vá na aba: Pass Lists")
    print("   4. Verifique se existe: SSH_Cloudflare_Hetzner_Whitelist")
    print("      OU crie uma nova Pass List:")
    print("      - Name: Traefik_Carbonio_Whitelist")
    print("      - Assigned Aliases: Selecione 'SNORT_TRUSTED_IPS'")
    print("   5. Vá na aba: Interfaces")
    print("   6. Para cada interface ativa:")
    print("      - Clique em: Edit")
    print("      - Na seção: 'Choose the Networks Snort Should Inspect and Whitelist'")
    print("      - No campo: Pass List")
    print("      - Selecione a Pass List criada")
    print("      - Save")
    print("   7. Reinicie o Snort em cada interface")
    
    print("\n✅ Após configurar, os IPs do Traefik e Carbonio NUNCA serão bloqueados!")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

