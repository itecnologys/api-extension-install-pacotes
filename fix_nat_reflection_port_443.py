#!/usr/bin/env python3
"""
Script para habilitar NAT Reflection no port forward ID 20 (porta 443)
Autor: Auto Assistant
Data: 2025-01-14
"""

import requests
import json
from requests.auth import HTTPBasicAuth
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

PFSENSE_URL = 'https://firewall.itecnologys.com/api/v2/'
PFSENSE_USER = 'api_cursor'
PFSENSE_PASSWORD = '805353'
PORT_FORWARD_ID = 20  # ID do port forward que está sendo usado primeiro

def main():
    print("=" * 70)
    print("HABILITANDO NAT REFLECTION NO PORT FORWARD ID 20")
    print("=" * 70)
    
    # Obter port forward atual
    try:
        response = requests.get(
            f'{PFSENSE_URL}firewall/nat/port_forward?id={PORT_FORWARD_ID}',
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Erro ao obter port forward: {response.status_code}")
            return
        
        data = response.json()
        fwd = data.get('data')
        
        if not fwd:
            print(f"❌ Port forward ID {PORT_FORWARD_ID} não encontrado!")
            return
        
        print(f"\n📋 Port Forward atual:")
        print(f"   ID: {fwd.get('id')}")
        print(f"   Descrição: {fwd.get('descr', '')}")
        print(f"   Porta: {fwd.get('destination_port')}")
        print(f"   Target: {fwd.get('target')}:{fwd.get('local_port')}")
        print(f"   NAT Reflection: {fwd.get('natreflection', 'None')}")
        
        # Verificar se já está habilitado
        if fwd.get('natreflection') == 'enable':
            print(f"\n✅ NAT Reflection já está habilitado!")
            return
        
        # Habilitar NAT Reflection
        print(f"\n🔧 Habilitando NAT Reflection...")
        
        payload = fwd.copy()
        payload['natreflection'] = 'enable'
        
        response = requests.put(
            f'{PFSENSE_URL}firewall/nat/port_forward?id={PORT_FORWARD_ID}',
            json=payload,
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ NAT Reflection habilitado!")
            
            # Aplicar mudanças
            print(f"\n📡 Aplicando mudanças no firewall...")
            response2 = requests.post(
                f'{PFSENSE_URL}firewall/apply',
                auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
                verify=False,
                timeout=30
            )
            
            if response2.status_code == 200:
                print(f"✅ Mudanças aplicadas!")
                print(f"\n📋 Próximos passos:")
                print(f"   1. Aguarde alguns segundos")
                print(f"   2. Teste novamente: bash /root/test_port_443.sh")
                print(f"   3. Se ainda não funcionar, verifique:")
                print(f"      - Firewall Hetzner (painel)")
                print(f"      - Traefik na VM 105 (docker ps, logs)")
            else:
                print(f"⚠️  Erro ao aplicar mudanças: {response2.status_code}")
        else:
            print(f"❌ Erro ao habilitar NAT Reflection: {response.status_code}")
            try:
                error = response.json()
                print(f"   Mensagem: {error.get('message', '')}")
            except:
                print(f"   Resposta: {response.text[:300]}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    main()

