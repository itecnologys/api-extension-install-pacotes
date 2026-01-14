#!/usr/bin/env python3
"""
Script para limpar port forwards duplicados no pfSense
Mantém apenas os port forwards corretos para Traefik

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

# Configurações corretas
TRAEFIK_IP = '10.10.10.105'
TRAEFIK_HTTP_PORT = '8055'
TRAEFIK_HTTPS_PORT = '9055'

def get_port_forwards():
    """Obtém todos os port forwards"""
    try:
        response = requests.get(
            f'{PFSENSE_URL}firewall/nat/port_forwards',
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        return []
    except Exception as e:
        print(f"❌ Erro ao obter port forwards: {e}")
        return []

def delete_port_forward(fwd_id):
    """Remove um port forward"""
    try:
        response = requests.delete(
            f'{PFSENSE_URL}firewall/nat/port_forward?id={fwd_id}',
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=30
        )
        
        if response.status_code in [200, 204]:
            return True
        else:
            print(f"   ⚠️  Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 70)
    print("LIMPEZA DE PORT FORWARDS DUPLICADOS")
    print("=" * 70)
    
    forwards = get_port_forwards()
    
    # Filtrar port forwards WAN para portas 80/443
    wan_forwards_80 = [
        f for f in forwards 
        if f.get('interface') == 'wan'
        and str(f.get('destination_port')) == '80'
        and not f.get('disabled')
    ]
    
    wan_forwards_443 = [
        f for f in forwards 
        if f.get('interface') == 'wan'
        and str(f.get('destination_port')) == '443'
        and not f.get('disabled')
    ]
    
    print(f"\n📋 Port Forwards encontrados:")
    print(f"   Porta 80: {len(wan_forwards_80)}")
    print(f"   Porta 443: {len(wan_forwards_443)}")
    
    # Identificar os corretos (mais recentes ou com descrição correta)
    correct_80 = None
    correct_443 = None
    
    # Para porta 80: manter o mais recente que aponta para Traefik
    for fwd in sorted(wan_forwards_80, key=lambda x: x.get('id'), reverse=True):
        if fwd.get('target') == TRAEFIK_IP and str(fwd.get('local_port')) == TRAEFIK_HTTP_PORT:
            if not correct_80:
                correct_80 = fwd
                print(f"\n✅ Port forward 80 correto: ID {fwd.get('id')} - {fwd.get('descr', '')}")
    
    # Para porta 443: manter o mais recente que aponta para Traefik
    for fwd in sorted(wan_forwards_443, key=lambda x: x.get('id'), reverse=True):
        if fwd.get('target') == TRAEFIK_IP and str(fwd.get('local_port')) == TRAEFIK_HTTPS_PORT:
            if not correct_443:
                correct_443 = fwd
                print(f"✅ Port forward 443 correto: ID {fwd.get('id')} - {fwd.get('descr', '')}")
    
    # Remover duplicados
    print("\n" + "=" * 70)
    print("REMOVENDO DUPLICADOS")
    print("=" * 70)
    
    deleted_count = 0
    
    # Remover duplicados porta 80
    if correct_80:
        for fwd in wan_forwards_80:
            if fwd.get('id') != correct_80.get('id'):
                print(f"\n🗑️  Removendo port forward 80 duplicado:")
                print(f"   ID: {fwd.get('id')}")
                print(f"   Descrição: {fwd.get('descr', '')}")
                print(f"   Target: {fwd.get('target')}:{fwd.get('local_port')}")
                
                if delete_port_forward(fwd.get('id')):
                    print(f"   ✅ Removido!")
                    deleted_count += 1
                else:
                    print(f"   ❌ Falha ao remover")
    
    # Remover duplicados porta 443
    if correct_443:
        for fwd in wan_forwards_443:
            if fwd.get('id') != correct_443.get('id'):
                # Verificar se não é o dashboard do Traefik (pode ser necessário)
                desc = fwd.get('descr', '').lower()
                if 'dashboard' in desc or 'proxy.itecnologys.com' in desc:
                    print(f"\n⚠️  Mantendo port forward 443 (Dashboard):")
                    print(f"   ID: {fwd.get('id')}")
                    print(f"   Descrição: {fwd.get('descr', '')}")
                    continue
                
                print(f"\n🗑️  Removendo port forward 443 duplicado:")
                print(f"   ID: {fwd.get('id')}")
                print(f"   Descrição: {fwd.get('descr', '')}")
                print(f"   Target: {fwd.get('target')}:{fwd.get('local_port')}")
                
                if delete_port_forward(fwd.get('id')):
                    print(f"   ✅ Removido!")
                    deleted_count += 1
                else:
                    print(f"   ❌ Falha ao remover")
    
    if deleted_count > 0:
        print("\n" + "=" * 70)
        print("APLICANDO MUDANÇAS")
        print("=" * 70)
        
        try:
            response = requests.post(
                f'{PFSENSE_URL}firewall/apply',
                auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
                verify=False,
                timeout=30
            )
            
            if response.status_code == 200:
                print("✅ Mudanças aplicadas!")
        except Exception as e:
            print(f"⚠️  Erro ao aplicar mudanças: {e}")
        
        print(f"\n✅ {deleted_count} port forward(s) duplicado(s) removido(s)!")
    else:
        print("\n✅ Nenhum duplicado encontrado ou todos já estão corretos!")
    
    # Verificar resultado final
    print("\n" + "=" * 70)
    print("VERIFICAÇÃO FINAL")
    print("=" * 70)
    
    forwards_final = get_port_forwards()
    wan_forwards_80_final = [
        f for f in forwards_final 
        if f.get('interface') == 'wan'
        and str(f.get('destination_port')) == '80'
        and not f.get('disabled')
    ]
    
    wan_forwards_443_final = [
        f for f in forwards_final 
        if f.get('interface') == 'wan'
        and str(f.get('destination_port')) == '443'
        and not f.get('disabled')
    ]
    
    print(f"\n📋 Port Forwards finais:")
    print(f"   Porta 80: {len(wan_forwards_80_final)}")
    for fwd in wan_forwards_80_final:
        print(f"      ID {fwd.get('id')}: {fwd.get('descr', '')} → {fwd.get('target')}:{fwd.get('local_port')}")
    
    print(f"   Porta 443: {len(wan_forwards_443_final)}")
    for fwd in wan_forwards_443_final:
        print(f"      ID {fwd.get('id')}: {fwd.get('descr', '')} → {fwd.get('target')}:{fwd.get('local_port')}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

