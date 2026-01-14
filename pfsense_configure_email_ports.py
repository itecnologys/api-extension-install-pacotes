#!/usr/bin/env python3
"""
Script para configurar port forwards de email no pfSense
Portas de email devem ir DIRETO para Carbonio (não via Traefik)

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

# Configurações
CARBONIO_IP = '10.10.10.108'

# Portas de email e suas descrições
EMAIL_PORTS = {
    '25': {
        'name': 'SMTP',
        'desc': 'SMTP (Envio/Recebimento)',
        'local_port': '25'
    },
    '465': {
        'name': 'SMTPS',
        'desc': 'SMTP Seguro (SSL/TLS)',
        'local_port': '465'
    },
    '587': {
        'name': 'SMTP Submission',
        'desc': 'SMTP Submission (TLS)',
        'local_port': '587'
    },
    '993': {
        'name': 'IMAPS',
        'desc': 'IMAP Seguro (SSL/TLS)',
        'local_port': '993'
    },
    '995': {
        'name': 'POP3S',
        'desc': 'POP3 Seguro (SSL/TLS)',
        'local_port': '995'
    }
}

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
            return response.json().get('data', [])
        return []
    except Exception as e:
        print(f"❌ Erro ao obter port forwards: {e}")
        return []

def get_existing_email_forwards():
    """Obtém port forwards de email existentes"""
    forwards = get_port_forwards()
    return [
        f for f in forwards 
        if f.get('interface') == 'wan'
        and str(f.get('destination_port')) in EMAIL_PORTS.keys()
        and not f.get('disabled')
    ]

def create_or_update_port_forward(port, port_info, existing=None):
    """Cria ou atualiza port forward de email"""
    desc = f"Carbonio {port_info['desc']} - {port_info['name']}"
    
    if existing:
        # Verificar se precisa atualizar
        if existing.get('target') == CARBONIO_IP and str(existing.get('local_port')) == port_info['local_port']:
            print(f"   ✅ Porta {port} já está configurada corretamente (ID: {existing.get('id')})")
            return True
        
        # Atualizar
        print(f"   🔄 Atualizando porta {port}...")
        try:
            payload = existing.copy()
            payload['target'] = CARBONIO_IP
            payload['local_port'] = port_info['local_port']
            payload['descr'] = desc
            payload['disabled'] = False
            
            # A API não suporta PUT, então vamos deletar e recriar
            # Ou apenas informar que precisa atualizar manualmente
            print(f"      ⚠️  API não suporta atualização. Precisa atualizar manualmente:")
            print(f"         ID: {existing.get('id')}")
            print(f"         Target atual: {existing.get('target')}")
            print(f"         Target correto: {CARBONIO_IP}")
            return False
        except Exception as e:
            print(f"      ❌ Erro: {e}")
            return False
    
    # Criar novo
    print(f"   📝 Criando port forward para porta {port}...")
    
    payload = {
        'interface': 'wan',
        'ipprotocol': 'inet',
        'protocol': 'tcp',
        'source': 'any',
        'destination': 'wan',
        'destination_port': port,
        'target': CARBONIO_IP,
        'local_port': port_info['local_port'],
        'descr': desc,
        'disabled': False,
        'natreflection': 'enable'
    }
    
    try:
        response = requests.post(
            f'{PFSENSE_URL}firewall/nat/port_forward',
            json=payload,
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"      ✅ Port forward criado!")
            return True
        else:
            try:
                error = response.json()
                print(f"      ⚠️  Erro: {error.get('message', '')}")
            except:
                print(f"      ⚠️  Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"      ❌ Erro: {e}")
        return False

def create_firewall_rules():
    """Cria regras de firewall para portas de email"""
    print("\n" + "=" * 70)
    print("VERIFICANDO REGRAS DE FIREWALL")
    print("=" * 70)
    
    try:
        response = requests.get(
            f'{PFSENSE_URL}firewall/rules',
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            rules = response.json().get('data', [])
            
            for port, port_info in EMAIL_PORTS.items():
                # Verificar se já existe regra WAN para esta porta
                existing_rules = [
                    r for r in rules 
                    if 'wan' in [i.lower() for i in r.get('interface', [])] 
                    and str(r.get('destination_port')) == port
                    and not r.get('disabled')
                ]
                
                if existing_rules:
                    print(f"   ✅ Regra WAN porta {port} já existe")
                else:
                    print(f"   ⚠️  Regra WAN porta {port} não encontrada")
                    print(f"      Criando regra...")
                    
                    payload = {
                        'type': 'pass',
                        'interface': ['wan'],
                        'ipprotocol': 'inet',
                        'protocol': 'tcp',
                        'source': 'any',
                        'destination': 'wan',
                        'destination_port': port,
                        'descr': f'Allow {port_info["name"]} WAN (Carbonio)',
                        'disabled': False,
                        'log': False,
                        'statetype': 'keep state'
                    }
                    
                    try:
                        response2 = requests.post(
                            f'{PFSENSE_URL}firewall/rule',
                            json=payload,
                            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
                            verify=False,
                            timeout=30
                        )
                        
                        if response2.status_code == 200:
                            print(f"      ✅ Regra criada!")
                        else:
                            print(f"      ⚠️  Erro ao criar regra: {response2.status_code}")
                    except Exception as e:
                        print(f"      ❌ Erro: {e}")
    except Exception as e:
        print(f"❌ Erro ao verificar regras: {e}")

def main():
    """Função principal"""
    print("=" * 70)
    print("CONFIGURAÇÃO DE PORT FORWARDS DE EMAIL")
    print("=" * 70)
    print(f"\n🎯 Objetivo:")
    print(f"   Configurar portas de email para ir DIRETO para Carbonio")
    print(f"   IP Carbonio: {CARBONIO_IP}")
    print(f"   Portas: {', '.join(EMAIL_PORTS.keys())}")
    
    # Obter port forwards existentes
    existing_forwards = get_existing_email_forwards()
    
    # Criar/atualizar port forwards
    print("\n" + "=" * 70)
    print("CONFIGURANDO PORT FORWARDS")
    print("=" * 70)
    
    created_count = 0
    needs_update = []
    
    for port, port_info in EMAIL_PORTS.items():
        existing = next(
            (f for f in existing_forwards if str(f.get('destination_port')) == port),
            None
        )
        
        if create_or_update_port_forward(port, port_info, existing):
            if not existing:
                created_count += 1
        else:
            if existing and existing.get('target') != CARBONIO_IP:
                needs_update.append((port, existing))
    
    # Criar regras de firewall
    create_firewall_rules()
    
    # Aplicar mudanças
    if created_count > 0:
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
            else:
                print(f"⚠️  Erro ao aplicar mudanças: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    # Resumo
    print("\n" + "=" * 70)
    print("RESUMO")
    print("=" * 70)
    
    if created_count > 0:
        print(f"\n✅ {created_count} port forward(s) criado(s)!")
    
    if needs_update:
        print(f"\n⚠️  {len(needs_update)} port forward(s) precisam ser atualizados manualmente:")
        for port, fwd in needs_update:
            print(f"   Porta {port} (ID {fwd.get('id')}):")
            print(f"      Atual: {fwd.get('target')}:{fwd.get('local_port')}")
            print(f"      Correto: {CARBONIO_IP}:{EMAIL_PORTS[port]['local_port']}")
            print(f"      Ação: Editar no pfSense e atualizar target")
    
    print("\n📋 Configuração esperada:")
    print("   Porta 80/443 → Traefik (10.10.10.105)")
    print("   Porta 25 → Carbonio (10.10.10.108:25)")
    print("   Porta 465 → Carbonio (10.10.10.108:465)")
    print("   Porta 587 → Carbonio (10.10.10.108:587)")
    print("   Porta 993 → Carbonio (10.10.10.108:993)")
    print("   Porta 995 → Carbonio (10.10.10.108:995)")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

