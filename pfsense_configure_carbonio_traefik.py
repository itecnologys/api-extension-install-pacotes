#!/usr/bin/env python3
"""
Script para configurar regras de firewall e port forwards no pfSense
para permitir acesso externo ao Carbonio via Traefik

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

# Configurações do Traefik
TRAEFIK_IP = '10.10.10.105'
TRAEFIK_HTTP_PORT = '8055'
TRAEFIK_HTTPS_PORT = '9055'

def check_existing_rules():
    """Verifica regras e port forwards existentes"""
    print("=" * 70)
    print("VERIFICANDO CONFIGURAÇÕES EXISTENTES")
    print("=" * 70)
    
    # Verificar regras WAN
    try:
        response = requests.get(
            f'{PFSENSE_URL}firewall/rules',
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            rules = data.get('data', [])
            
            wan_rules_80 = [
                r for r in rules 
                if 'wan' in [i.lower() for i in r.get('interface', [])] 
                and str(r.get('destination_port')) == '80'
            ]
            
            wan_rules_443 = [
                r for r in rules 
                if 'wan' in [i.lower() for i in r.get('interface', [])] 
                and str(r.get('destination_port')) == '443'
            ]
            
            print(f"\n📋 Regras WAN existentes:")
            print(f"   Porta 80: {len(wan_rules_80)} regra(s)")
            print(f"   Porta 443: {len(wan_rules_443)} regra(s)")
            
            return {
                'rule_80': wan_rules_80[0] if wan_rules_80 else None,
                'rule_443': wan_rules_443[0] if wan_rules_443 else None
            }
    except Exception as e:
        print(f"❌ Erro ao verificar regras: {e}")
        return {'rule_80': None, 'rule_443': None}
    
    # Verificar port forwards
    try:
        response = requests.get(
            f'{PFSENSE_URL}firewall/nat/port_forwards',
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            forwards = data.get('data', [])
            
            forward_80 = [
                f for f in forwards 
                if str(f.get('destination_port')) == '80'
                and f.get('interface') == 'wan'
            ]
            
            forward_443 = [
                f for f in forwards 
                if str(f.get('destination_port')) == '443'
                and f.get('interface') == 'wan'
            ]
            
            print(f"\n📋 Port Forwards existentes:")
            print(f"   Porta 80: {len(forward_80)} forward(s)")
            if forward_80:
                print(f"      → {forward_80[0].get('target')}:{forward_80[0].get('local_port')}")
            print(f"   Porta 443: {len(forward_443)} forward(s)")
            if forward_443:
                print(f"      → {forward_443[0].get('target')}:{forward_443[0].get('local_port')}")
            
            return {
                'forward_80': forward_80[0] if forward_80 else None,
                'forward_443': forward_443[0] if forward_443 else None
            }
    except Exception as e:
        print(f"❌ Erro ao verificar port forwards: {e}")
        return {'forward_80': None, 'forward_443': None}

def create_firewall_rule(port, existing_rule=None):
    """Cria regra de firewall WAN para porta específica"""
    rule_name = f"Traefik {'HTTPS' if port == '443' else 'HTTP'} (mail.ligbox.com.br)"
    
    if existing_rule:
        print(f"\n⚠️  Regra WAN porta {port} já existe (ID: {existing_rule.get('id')})")
        if existing_rule.get('disabled'):
            print(f"   ⚠️  Regra está DESABILITADA! Habilitando...")
            # Tentar atualizar para habilitar
            try:
                payload = existing_rule.copy()
                payload['disabled'] = False
                payload['descr'] = rule_name
                
                response = requests.put(
                    f'{PFSENSE_URL}firewall/rule?id={existing_rule.get("id")}',
                    json=payload,
                    auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
                    verify=False,
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"   ✅ Regra habilitada!")
                    return True
            except Exception as e:
                print(f"   ⚠️  Erro ao habilitar: {e}")
        else:
            print(f"   ✅ Regra já está ativa")
        return True
    
    print(f"\n📝 Criando regra WAN para porta {port}...")
    
    payload = {
        'type': 'pass',
        'interface': ['wan'],
        'ipprotocol': 'inet',
        'protocol': 'tcp',
        'source': 'any',
        'destination': 'wan',
        'destination_port': port,
        'descr': rule_name,
        'disabled': False,
        'log': False,
        'statetype': 'keep state'
    }
    
    try:
        response = requests.post(
            f'{PFSENSE_URL}firewall/rule',
            json=payload,
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Regra criada com sucesso!")
            try:
                data = response.json()
                print(f"   ID: {data.get('data', {}).get('id', 'N/A')}")
            except:
                pass
            return True
        else:
            try:
                error = response.json()
                print(f"   ⚠️  Erro: {error.get('message', '')}")
            except:
                print(f"   ⚠️  Resposta: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def create_port_forward(port, target_port, existing_forward=None):
    """Cria port forward para redirecionar porta externa para Traefik"""
    desc = f"Traefik {'HTTPS' if port == '443' else 'HTTP'} → {TRAEFIK_IP}:{target_port}"
    
    if existing_forward:
        print(f"\n⚠️  Port forward porta {port} já existe (ID: {existing_forward.get('id')})")
        
        # Verificar se está configurado corretamente
        if existing_forward.get('target') == TRAEFIK_IP and str(existing_forward.get('local_port')) == target_port:
            if existing_forward.get('disabled'):
                print(f"   ⚠️  Port forward está DESABILITADO! Habilitando...")
                try:
                    payload = existing_forward.copy()
                    payload['disabled'] = False
                    payload['descr'] = desc
                    
                    response = requests.put(
                        f'{PFSENSE_URL}firewall/nat/port_forward?id={existing_forward.get("id")}',
                        json=payload,
                        auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
                        verify=False,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        print(f"   ✅ Port forward habilitado!")
                        return True
                except Exception as e:
                    print(f"   ⚠️  Erro ao habilitar: {e}")
            else:
                print(f"   ✅ Port forward já está ativo e configurado corretamente")
            return True
        else:
            print(f"   ⚠️  Port forward existe mas aponta para lugar diferente!")
            print(f"      Atual: {existing_forward.get('target')}:{existing_forward.get('local_port')}")
            print(f"      Esperado: {TRAEFIK_IP}:{target_port}")
            print(f"   Vamos atualizar...")
            
            try:
                payload = existing_forward.copy()
                payload['target'] = TRAEFIK_IP
                payload['local_port'] = target_port
                payload['descr'] = desc
                payload['disabled'] = False
                
                response = requests.put(
                    f'{PFSENSE_URL}firewall/nat/port_forward?id={existing_forward.get("id")}',
                    json=payload,
                    auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
                    verify=False,
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"   ✅ Port forward atualizado!")
                    return True
            except Exception as e:
                print(f"   ⚠️  Erro ao atualizar: {e}")
    
    print(f"\n📝 Criando port forward {port} → {TRAEFIK_IP}:{target_port}...")
    
    payload = {
        'interface': 'wan',
        'ipprotocol': 'inet',
        'protocol': 'tcp',
        'source': 'any',
        'destination': 'wan',
        'destination_port': port,
        'target': TRAEFIK_IP,
        'local_port': target_port,
        'descr': desc,
        'disabled': False,
        'natreflection': 'enable'  # Para permitir acesso interno (hairpin)
    }
    
    try:
        response = requests.post(
            f'{PFSENSE_URL}firewall/nat/port_forward',
            json=payload,
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Port forward criado com sucesso!")
            try:
                data = response.json()
                print(f"   ID: {data.get('data', {}).get('id', 'N/A')}")
            except:
                pass
            return True
        else:
            try:
                error = response.json()
                print(f"   ⚠️  Erro: {error.get('message', '')}")
            except:
                print(f"   ⚠️  Resposta: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def apply_changes():
    """Aplica as mudanças no firewall"""
    print("\n" + "=" * 70)
    print("APLICANDO MUDANÇAS NO FIREWALL")
    print("=" * 70)
    
    try:
        response = requests.post(
            f'{PFSENSE_URL}firewall/apply',
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=30
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Mudanças aplicadas com sucesso!")
            return True
        else:
            print("⚠️  Status inesperado ao aplicar mudanças")
            try:
                error = response.json()
                print(f"   Erro: {error.get('message', '')}")
            except:
                print(f"   Resposta: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao aplicar mudanças: {e}")
        return False

def main():
    """Função principal"""
    print("\n" + "=" * 70)
    print("CONFIGURAÇÃO DE FIREWALL E PORT FORWARDS PARA CARBONIO/TRAEFIK")
    print("=" * 70)
    print(f"\n🎯 Objetivo:")
    print(f"   Permitir acesso externo ao Carbonio via Traefik")
    print(f"   Porta 80 externa → {TRAEFIK_IP}:{TRAEFIK_HTTP_PORT}")
    print(f"   Porta 443 externa → {TRAEFIK_IP}:{TRAEFIK_HTTPS_PORT}")
    
    # Verificar configurações existentes
    existing = check_existing_rules()
    
    # Criar regras de firewall
    print("\n" + "=" * 70)
    print("CRIANDO REGRAS DE FIREWALL")
    print("=" * 70)
    
    rule_80_ok = create_firewall_rule('80', existing.get('rule_80'))
    rule_443_ok = create_firewall_rule('443', existing.get('rule_443'))
    
    # Criar port forwards
    print("\n" + "=" * 70)
    print("CRIANDO PORT FORWARDS")
    print("=" * 70)
    
    forward_80_ok = create_port_forward('80', TRAEFIK_HTTP_PORT, existing.get('forward_80'))
    forward_443_ok = create_port_forward('443', TRAEFIK_HTTPS_PORT, existing.get('forward_443'))
    
    # Aplicar mudanças
    if rule_80_ok and rule_443_ok and forward_80_ok and forward_443_ok:
        apply_changes()
        
        print("\n" + "=" * 70)
        print("✅ CONFIGURAÇÃO CONCLUÍDA!")
        print("=" * 70)
        print("\n📋 Próximos passos:")
        print("   1. Teste as portas externas:")
        print("      - Porta 80: https://canyouseeme.org (IP: 95.216.14.162)")
        print("      - Porta 443: https://canyouseeme.org (IP: 95.216.14.162)")
        print("\n   2. Teste acesso externo:")
        print("      - https://mail.ligbox.com.br")
        print("      - http://mail.ligbox.com.br (deve redirecionar para HTTPS)")
        print("\n   3. Teste acesso interno:")
        print("      - curl -I https://mail.ligbox.com.br")
        print("      - curl -I -k https://10.10.10.105:9055 -H 'Host: mail.ligbox.com.br'")
    else:
        print("\n" + "=" * 70)
        print("⚠️  ALGUMAS CONFIGURAÇÕES FALHARAM")
        print("=" * 70)
        print("\nVerifique os erros acima e tente novamente.")
        print("Ou configure manualmente via interface web do pfSense.")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

