#!/usr/bin/env python3
"""
Script para habilitar NAT Reflection no port forward 443 via API
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
PORT_FORWARD_ID = 20  # ID do port forward 443 para Traefik

def get_port_forward():
    """Obtém o port forward atual"""
    try:
        response = requests.get(
            f'{PFSENSE_URL}firewall/nat/port_forward?id={PORT_FORWARD_ID}',
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data')
        else:
            print(f"❌ Erro ao obter port forward: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def update_port_forward(fwd):
    """Atualiza o port forward com NAT Reflection habilitado"""
    print(f"\n📝 Atualizando port forward...")
    
    # Criar payload com NAT Reflection habilitado
    payload = fwd.copy()
    payload['natreflection'] = 'enable'
    
    # Tentar diferentes métodos da API
    methods = [
        ('PUT', f'{PFSENSE_URL}firewall/nat/port_forward?id={PORT_FORWARD_ID}'),
        ('PATCH', f'{PFSENSE_URL}firewall/nat/port_forward?id={PORT_FORWARD_ID}'),
        ('POST', f'{PFSENSE_URL}firewall/nat/port_forward'),
    ]
    
    for method, url in methods:
        try:
            print(f"   Tentando {method} {url}...")
            
            if method == 'PUT':
                response = requests.put(
                    url,
                    json=payload,
                    auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
                    verify=False,
                    timeout=30
                )
            elif method == 'PATCH':
                response = requests.patch(
                    url,
                    json=payload,
                    auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
                    verify=False,
                    timeout=30
                )
            else:  # POST
                response = requests.post(
                    url,
                    json=payload,
                    auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
                    verify=False,
                    timeout=30
                )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCESSO com método {method}!")
                try:
                    data = response.json()
                    return True, data
                except:
                    return True, None
            elif response.status_code == 405:
                print(f"   ⚠️  Método {method} não permitido")
                continue
            else:
                try:
                    error = response.json()
                    print(f"   ⚠️  Erro: {error.get('message', '')}")
                except:
                    print(f"   ⚠️  Resposta: {response.text[:200]}")
                continue
                
        except Exception as e:
            print(f"   ❌ Erro com {method}: {e}")
            continue
    
    return False, None

def apply_changes():
    """Aplica as mudanças no firewall"""
    try:
        response = requests.post(
            f'{PFSENSE_URL}firewall/apply',
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"⚠️  Erro ao aplicar mudanças: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 70)
    print("HABILITANDO NAT REFLECTION VIA API")
    print("=" * 70)
    
    print(f"\n🎯 Objetivo: Habilitar NAT Reflection no port forward ID {PORT_FORWARD_ID}")
    
    # Obter port forward atual
    print(f"\n📋 Passo 1: Obtendo port forward atual...")
    fwd = get_port_forward()
    
    if not fwd:
        print(f"❌ Não foi possível obter o port forward!")
        return 1
    
    print(f"   ✅ Port forward encontrado:")
    print(f"      ID: {fwd.get('id')}")
    print(f"      Descrição: {fwd.get('descr', '')}")
    print(f"      Porta: {fwd.get('destination_port')}")
    print(f"      Target: {fwd.get('target')}:{fwd.get('local_port')}")
    print(f"      NAT Reflection atual: {fwd.get('natreflection', 'None')}")
    
    # Verificar se já está habilitado
    if fwd.get('natreflection') == 'enable':
        print(f"\n✅ NAT Reflection já está habilitado!")
        return 0
    
    # Atualizar
    success, data = update_port_forward(fwd)
    
    if success:
        # Aplicar mudanças
        print(f"\n📡 Aplicando mudanças no firewall...")
        if apply_changes():
            print(f"✅ Mudanças aplicadas!")
            
            # Verificar resultado
            print(f"\n🔍 Verificando resultado...")
            fwd_updated = get_port_forward()
            if fwd_updated:
                nat_reflection = fwd_updated.get('natreflection', 'None')
                if nat_reflection == 'enable':
                    print(f"✅ NAT Reflection habilitado com sucesso!")
                    print(f"\n📋 Próximos passos:")
                    print(f"   1. Teste acesso externo: https://mail.ligbox.com.br")
                    print(f"   2. Teste porta externa: bash /root/test_port_443.sh")
                    return 0
                else:
                    print(f"⚠️  NAT Reflection ainda não está habilitado")
                    print(f"   Valor atual: {nat_reflection}")
                    print(f"   A API pode não suportar esta operação")
                    print(f"   Ação manual necessária via interface web")
                    return 1
        else:
            print(f"⚠️  Mudanças podem não ter sido aplicadas")
            return 1
    else:
        print(f"\n❌ Não foi possível atualizar via API")
        print(f"\n📋 AÇÃO MANUAL NECESSÁRIA:")
        print(f"   1. Acesse: https://firewall.itecnologys.com")
        print(f"   2. Vá em: Firewall > NAT > Port Forward")
        print(f"   3. Edite: ID {PORT_FORWARD_ID}")
        print(f"   4. NAT Reflection: Selecione 'Enable (Pure NAT)'")
        print(f"   5. Save → Apply Changes")
        return 1

if __name__ == '__main__':
    sys.exit(main())

