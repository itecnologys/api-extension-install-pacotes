#!/usr/bin/env python3
"""
Script para diagnosticar e corrigir problema da porta 443 fechada
Autor: Auto Assistant
Data: 2025-01-14
"""

import requests
import json
import sys
from requests.auth import HTTPBasicAuth
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

PFSENSE_URL = 'https://firewall.itecnologys.com/api/v2/'
PFSENSE_USER = 'api_cursor'
PFSENSE_PASSWORD = '805353'
TRAEFIK_IP = '10.10.10.105'
TRAEFIK_HTTPS_PORT = '9055'

def get_port_forwards():
    """Obtém port forwards"""
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
    except:
        return []

def get_firewall_rules():
    """Obtém regras de firewall"""
    try:
        response = requests.get(
            f'{PFSENSE_URL}firewall/rules',
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get('data', [])
        return []
    except:
        return []

def main():
    print("=" * 70)
    print("DIAGNÓSTICO E CORREÇÃO - PORTA 443 FECHADA")
    print("=" * 70)
    
    forwards = get_port_forwards()
    rules = get_firewall_rules()
    
    # Port forwards WAN 443
    wan_443 = [
        f for f in forwards 
        if f.get('interface') == 'wan'
        and str(f.get('destination_port')) == '443'
        and not f.get('disabled')
    ]
    
    # Ordenar por ID
    wan_443_sorted = sorted(wan_443, key=lambda x: x.get('id', 0))
    
    print(f"\n📋 Port Forwards WAN 443 encontrados: {len(wan_443_sorted)}")
    
    if not wan_443_sorted:
        print("\n❌ NENHUM port forward ativo para porta 443!")
        print("   Vamos criar um...")
        
        payload = {
            'interface': 'wan',
            'ipprotocol': 'inet',
            'protocol': 'tcp',
            'source': 'any',
            'destination': 'wan',
            'destination_port': '443',
            'target': TRAEFIK_IP,
            'local_port': TRAEFIK_HTTPS_PORT,
            'descr': 'Carbonio HTTPS via Traefik',
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
                print("✅ Port forward criado!")
                
                # Aplicar mudanças
                requests.post(
                    f'{PFSENSE_URL}firewall/apply',
                    auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
                    verify=False,
                    timeout=30
                )
                print("✅ Mudanças aplicadas!")
            else:
                print(f"❌ Erro ao criar: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        return
    
    # Verificar primeiro port forward
    first = wan_443_sorted[0]
    print(f"\n⭐ PRIMEIRO port forward (será usado):")
    print(f"   ID: {first.get('id')}")
    print(f"   Descrição: {first.get('descr', '')}")
    print(f"   Target: {first.get('target')}:{first.get('local_port')}")
    
    # Verificar se aponta para Traefik
    if first.get('target') != TRAEFIK_IP or str(first.get('local_port')) != TRAEFIK_HTTPS_PORT:
        print(f"\n⚠️  PROBLEMA: Primeiro port forward NÃO aponta para Traefik!")
        print(f"   Esperado: {TRAEFIK_IP}:{TRAEFIK_HTTPS_PORT}")
        print(f"   Atual: {first.get('target')}:{first.get('local_port')}")
        print(f"\n   Opções:")
        print(f"   1. Desabilitar port forwards anteriores")
        print(f"   2. Deletar port forwards incorretos")
        print(f"   3. Criar novo port forward que será o primeiro")
        
        # Verificar se há port forward correto
        correct = [
            f for f in wan_443_sorted
            if f.get('target') == TRAEFIK_IP and str(f.get('local_port')) == TRAEFIK_HTTPS_PORT
        ]
        
        if correct:
            correct_fwd = correct[0]
            print(f"\n   ✅ Existe port forward correto (ID: {correct_fwd.get('id')})")
            print(f"   ⚠️  Mas ele não é o primeiro, então não está sendo usado!")
            print(f"\n   Vamos desabilitar os anteriores...")
            
            # Desabilitar port forwards anteriores ao correto
            for fwd in wan_443_sorted:
                if fwd.get('id') < correct_fwd.get('id'):
                    print(f"\n   🗑️  Desabilitando ID {fwd.get('id')}...")
                    try:
                        payload = fwd.copy()
                        payload['disabled'] = True
                        
                        response = requests.put(
                            f'{PFSENSE_URL}firewall/nat/port_forward?id={fwd.get("id")}',
                            json=payload,
                            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
                            verify=False,
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            print(f"      ✅ Desabilitado!")
                        else:
                            print(f"      ⚠️  Erro: {response.status_code}")
                    except Exception as e:
                        print(f"      ❌ Erro: {e}")
            
            # Aplicar mudanças
            try:
                requests.post(
                    f'{PFSENSE_URL}firewall/apply',
                    auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
                    verify=False,
                    timeout=30
                )
                print("\n✅ Mudanças aplicadas!")
            except:
                pass
        else:
            print(f"\n   ❌ Não há port forward correto!")
            print(f"   Vamos criar um novo...")
            
            payload = {
                'interface': 'wan',
                'ipprotocol': 'inet',
                'protocol': 'tcp',
                'source': 'any',
                'destination': 'wan',
                'destination_port': '443',
                'target': TRAEFIK_IP,
                'local_port': TRAEFIK_HTTPS_PORT,
                'descr': 'Carbonio HTTPS via Traefik (PRIORIDADE)',
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
                    print("✅ Port forward criado!")
                    
                    # Aplicar
                    requests.post(
                        f'{PFSENSE_URL}firewall/apply',
                        auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
                        verify=False,
                        timeout=30
                    )
                    print("✅ Mudanças aplicadas!")
                else:
                    print(f"❌ Erro: {response.status_code}")
            except Exception as e:
                print(f"❌ Erro: {e}")
    else:
        print(f"\n✅ Port forward está correto!")
        print(f"   Mas a porta ainda está fechada...")
        print(f"\n   Possíveis causas:")
        print(f"   1. Regra de firewall bloqueando")
        print(f"   2. Traefik não está escutando na porta 9055")
        print(f"   3. Problema de rede/firewall externo")
        
        # Verificar regras
        wan_rules_443 = [
            r for r in rules 
            if 'wan' in [i.lower() for i in r.get('interface', [])] 
            and str(r.get('destination_port')) == '443'
            and not r.get('disabled')
        ]
        
        if not wan_rules_443:
            print(f"\n   ⚠️  Nenhuma regra WAN para porta 443!")
            print(f"   Vamos criar uma...")
            
            payload = {
                'type': 'pass',
                'interface': ['wan'],
                'ipprotocol': 'inet',
                'protocol': 'tcp',
                'source': 'any',
                'destination': 'wan',
                'destination_port': '443',
                'descr': 'Allow HTTPS WAN (Carbonio)',
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
                
                if response.status_code == 200:
                    print("✅ Regra criada!")
                    
                    # Aplicar
                    requests.post(
                        f'{PFSENSE_URL}firewall/apply',
                        auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
                        verify=False,
                        timeout=30
                    )
                    print("✅ Mudanças aplicadas!")
            except Exception as e:
                print(f"❌ Erro: {e}")
        else:
            print(f"\n   ✅ Regras WAN para porta 443 existem ({len(wan_rules_443)})")
    
    print("\n" + "=" * 70)
    print("TESTE NOVAMENTE:")
    print("=" * 70)
    print("bash /root/test_port_443.sh")
    print("=" * 70)

if __name__ == '__main__':
    main()

