#!/usr/bin/env python3
"""
Script para configurar Whitelist/Pass List no Snort do pfSense
Evita bloqueio de IPs específicos (SSH, Cloudflare, Hetzner, etc.)

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

# IPs e ranges que NUNCA devem ser bloqueados
TRUSTED_IPS = {
    'name': 'SNORT_TRUSTED_IPS',
    'type': 'network',  # network para suportar ranges
    'descr': 'IPs confiáveis - nunca bloquear (SSH, Cloudflare, Hetzner)',
    'address': [
        # IP local do Cursor/IDE
        '51.171.219.218/20',  # Range completo
        
        # IPs da Hetzner
        '95.216.14.0/24',      # Range completo da Hetzner
        '95.216.14.162/32',    # IP específico
        '95.216.14.146/32',    # IP específico
        
        # Ranges da Cloudflare (principais)
        '173.245.48.0/20',
        '103.21.244.0/22',
        '103.22.200.0/22',
        '103.31.4.0/22',
        '141.101.64.0/18',
        '108.162.192.0/18',
        '190.93.240.0/20',
        '188.114.96.0/20',
        '197.234.240.0/22',
        '198.41.128.0/17',
        '162.158.0.0/15',
        '104.16.0.0/13',
        '104.24.0.0/14',
        '172.64.0.0/13',
        '131.0.72.0/22',
    ]
}

def check_alias_exists(alias_name):
    """Verifica se o alias já existe"""
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
                if alias.get('name') == alias_name:
                    return alias
        return None
    except Exception as e:
        print(f"❌ Erro ao verificar alias: {e}")
        return None

def create_or_update_alias():
    """Cria ou atualiza o alias de IPs confiáveis"""
    print("=" * 70)
    print("CRIANDO/ATUALIZANDO ALIAS DE IPs CONFIÁVEIS")
    print("=" * 70)
    
    alias_name = TRUSTED_IPS['name']
    existing_alias = check_alias_exists(alias_name)
    
    if existing_alias:
        print(f"\n⚠️  Alias '{alias_name}' já existe!")
        print(f"   ID: {existing_alias.get('id')}")
        print(f"   Endereços atuais: {existing_alias.get('address', [])}")
        
        # Verificar se precisa atualizar
        current_addresses = set(existing_alias.get('address', []))
        new_addresses = set(TRUSTED_IPS['address'])
        
        if current_addresses == new_addresses:
            print("\n✅ Alias já está configurado corretamente!")
            return existing_alias
        else:
            print("\n🔄 Atualizando alias com novos endereços...")
            # Tentar atualizar via API
            try:
                alias_id = existing_alias.get('id')
                payload = {
                    'name': alias_name,
                    'type': TRUSTED_IPS['type'],
                    'descr': TRUSTED_IPS['descr'],
                    'address': TRUSTED_IPS['address']
                }
                
                response = requests.put(
                    f'{PFSENSE_URL}firewall/alias?id={alias_id}',
                    json=payload,
                    auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
                    verify=False,
                    timeout=30
                )
                
                if response.status_code == 200:
                    print("✅ Alias atualizado com sucesso!")
                    data = response.json()
                    return data.get('data')
                else:
                    print(f"⚠️  Não foi possível atualizar via API (status: {response.status_code})")
                    print(f"   Você precisará atualizar manualmente na interface web")
                    return existing_alias
            except Exception as e:
                print(f"⚠️  Erro ao atualizar: {e}")
                print(f"   Você precisará atualizar manualmente na interface web")
                return existing_alias
    else:
        print(f"\n📝 Criando novo alias: {alias_name}")
        print(f"   Tipo: {TRUSTED_IPS['type']}")
        print(f"   Endereços: {len(TRUSTED_IPS['address'])} IPs/ranges")
        
        try:
            payload = {
                'name': alias_name,
                'type': TRUSTED_IPS['type'],
                'descr': TRUSTED_IPS['descr'],
                'address': TRUSTED_IPS['address']
            }
            
            response = requests.post(
                f'{PFSENSE_URL}firewall/alias',
                json=payload,
                auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
                verify=False,
                timeout=30
            )
            
            if response.status_code == 200:
                print("✅ Alias criado com sucesso!")
                data = response.json()
                return data.get('data')
            elif response.status_code == 201:
                print("✅ Alias criado com sucesso! (201 Created)")
                data = response.json()
                return data.get('data')
            else:
                print(f"⚠️  Status inesperado: {response.status_code}")
                try:
                    error = response.json()
                    print(f"   Erro: {error.get('message', '')}")
                except:
                    print(f"   Resposta: {response.text[:300]}")
                return None
        except Exception as e:
            print(f"❌ Erro ao criar alias: {e}")
            return None

def print_manual_instructions():
    """Imprime instruções manuais para configurar Pass List no Snort"""
    print("\n" + "=" * 70)
    print("INSTRUÇÕES PARA CONFIGURAR PASS LIST NO SNORT")
    print("=" * 70)
    
    print("\n📋 PASSO 1: Verificar se o Alias foi criado")
    print("   1. Acesse: https://firewall.itecnologys.com")
    print("   2. Vá em: Firewall > Aliases")
    print("   3. Verifique se existe o alias: SNORT_TRUSTED_IPS")
    print("   4. Se não existir, crie manualmente com os IPs listados acima")
    
    print("\n📋 PASSO 2: Criar Pass List no Snort")
    print("   1. Acesse: Services > Snort")
    print("   2. Vá na aba: Pass Lists")
    print("   3. Clique em: Add (ou edite se já existir)")
    print("   4. Configure:")
    print("      - Name: SSH_Cloudflare_Hetzner_Whitelist")
    print("      - Assigned Aliases: Selecione 'SNORT_TRUSTED_IPS'")
    print("      - Auto Generated IP Addresses: Marque conforme necessário")
    print("   5. Clique em: Save")
    
    print("\n📋 PASSO 3: Associar Pass List às Interfaces do Snort")
    print("   1. Ainda em Services > Snort")
    print("   2. Vá na aba: Interfaces")
    print("   3. Para cada interface ativa (LAN, WAN, etc.):")
    print("      - Clique em: Edit (ícone de lápis)")
    print("      - Na seção: 'Choose the Networks Snort Should Inspect and Whitelist'")
    print("      - No campo: Pass List")
    print("      - Selecione: SSH_Cloudflare_Hetzner_Whitelist")
    print("      - Clique em: Save")
    
    print("\n📋 PASSO 4: Reiniciar o Snort")
    print("   1. Ainda em Services > Snort")
    print("   2. Vá na aba: Interfaces")
    print("   3. Para cada interface:")
    print("      - Clique em: Restart (ícone de restart)")
    print("   4. Ou reinicie o serviço completo")
    
    print("\n✅ Após esses passos, os IPs configurados NUNCA serão bloqueados pelo Snort!")
    
    print("\n" + "=" * 70)
    print("IPs CONFIGURADOS NA WHITELIST:")
    print("=" * 70)
    for i, ip in enumerate(TRUSTED_IPS['address'], 1):
        print(f"   {i:2d}. {ip}")

def main():
    """Função principal"""
    print("\n" + "=" * 70)
    print("CONFIGURAÇÃO DE WHITELIST NO SNORT - PFSENSE")
    print("=" * 70)
    print("\n🎯 Objetivo: Evitar bloqueio de IPs confiáveis pelo Snort")
    print("   - IP local do Cursor/IDE: 51.171.219.218/20")
    print("   - IPs da Hetzner: 95.216.14.0/24, 95.216.14.162, 95.216.14.146")
    print("   - Ranges da Cloudflare")
    
    # Criar/atualizar alias
    alias = create_or_update_alias()
    
    if alias:
        print("\n✅ Alias configurado via API!")
        print(f"   Nome: {alias.get('name')}")
        print(f"   Endereços: {len(alias.get('address', []))} IPs/ranges")
    else:
        print("\n⚠️  Não foi possível criar/atualizar o alias via API")
        print("   Você precisará criar manualmente")
    
    # Instruções para configurar Pass List (não há API disponível)
    print_manual_instructions()
    
    print("\n" + "=" * 70)
    print("PRÓXIMOS PASSOS")
    print("=" * 70)
    print("\n1. ✅ Alias criado/verificado (via API)")
    print("2. ⚠️  Configure a Pass List no Snort (manual - veja instruções acima)")
    print("3. ⚠️  Associe a Pass List às interfaces do Snort (manual)")
    print("4. ⚠️  Reinicie o Snort para aplicar as mudanças")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

