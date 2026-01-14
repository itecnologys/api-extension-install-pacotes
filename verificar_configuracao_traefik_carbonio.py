#!/usr/bin/env python3
"""
Script para verificar configuração completa Traefik + Carbonio
Verifica port forwards, regras de firewall e testa a cadeia

Autor: Auto Assistant
Data: 2025-01-14
"""

import requests
import json
import sys
import subprocess
from requests.auth import HTTPBasicAuth
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Configurações da API pfSense
PFSENSE_URL = 'https://firewall.itecnologys.com/api/v2/'
PFSENSE_USER = 'api_cursor'
PFSENSE_PASSWORD = '805353'

# Configurações
TRAEFIK_IP = '10.10.10.105'
TRAEFIK_HTTP_PORT = '8055'
TRAEFIK_HTTPS_PORT = '9055'
CARBONIO_IP = '10.10.10.108'
CARBONIO_PORT = '443'

def check_port_forwards():
    """Verifica port forwards para Traefik"""
    print("=" * 70)
    print("1. VERIFICANDO PORT FORWARDS")
    print("=" * 70)
    
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
            
            # Port forwards WAN para Traefik
            forward_80 = [
                f for f in forwards 
                if f.get('interface') == 'wan'
                and str(f.get('destination_port')) == '80'
                and f.get('target') == TRAEFIK_IP
                and str(f.get('local_port')) == TRAEFIK_HTTP_PORT
                and not f.get('disabled')
            ]
            
            forward_443 = [
                f for f in forwards 
                if f.get('interface') == 'wan'
                and str(f.get('destination_port')) == '443'
                and f.get('target') == TRAEFIK_IP
                and str(f.get('local_port')) == TRAEFIK_HTTPS_PORT
                and not f.get('disabled')
            ]
            
            print(f"\n📋 Port Forward 80 (HTTP):")
            if forward_80:
                fwd = forward_80[0]
                print(f"   ✅ Configurado corretamente!")
                print(f"      ID: {fwd.get('id')}")
                print(f"      Descrição: {fwd.get('descr', '')}")
                print(f"      80 externa → {fwd.get('target')}:{fwd.get('local_port')}")
                print(f"      NAT Reflection: {fwd.get('natreflection', 'None')}")
                return True, True
            else:
                print(f"   ❌ NÃO configurado ou incorreto!")
                print(f"      Esperado: 80 → {TRAEFIK_IP}:{TRAEFIK_HTTP_PORT}")
                return False, False
            
            print(f"\n📋 Port Forward 443 (HTTPS):")
            if forward_443:
                fwd = forward_443[0]
                print(f"   ✅ Configurado corretamente!")
                print(f"      ID: {fwd.get('id')}")
                print(f"      Descrição: {fwd.get('descr', '')}")
                print(f"      443 externa → {fwd.get('target')}:{fwd.get('local_port')}")
                print(f"      NAT Reflection: {fwd.get('natreflection', 'None')}")
                return True, True
            else:
                print(f"   ❌ NÃO configurado ou incorreto!")
                print(f"      Esperado: 443 → {TRAEFIK_IP}:{TRAEFIK_HTTPS_PORT}")
                return False, False
                
        else:
            print(f"❌ Erro ao obter port forwards: {response.status_code}")
            return False, False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False, False

def check_firewall_rules():
    """Verifica regras de firewall WAN"""
    print("\n" + "=" * 70)
    print("2. VERIFICANDO REGRAS DE FIREWALL WAN")
    print("=" * 70)
    
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
            
            # Regras WAN para portas 80 e 443
            rule_80 = [
                r for r in rules 
                if 'wan' in [i.lower() for i in r.get('interface', [])] 
                and str(r.get('destination_port')) == '80'
                and r.get('type') == 'pass'
                and not r.get('disabled')
            ]
            
            rule_443 = [
                r for r in rules 
                if 'wan' in [i.lower() for i in r.get('interface', [])] 
                and str(r.get('destination_port')) == '443'
                and r.get('type') == 'pass'
                and not r.get('disabled')
            ]
            
            print(f"\n📋 Regra Firewall WAN - Porta 80:")
            if rule_80:
                r = rule_80[0]
                print(f"   ✅ Regra ativa!")
                print(f"      ID: {r.get('id')}")
                print(f"      Descrição: {r.get('descr', '')}")
                print(f"      Tipo: {r.get('type')}")
                print(f"      Protocolo: {r.get('protocol')}")
                rule_80_ok = True
            else:
                print(f"   ❌ Nenhuma regra ativa encontrada!")
                rule_80_ok = False
            
            print(f"\n📋 Regra Firewall WAN - Porta 443:")
            if rule_443:
                r = rule_443[0]
                print(f"   ✅ Regra ativa!")
                print(f"      ID: {r.get('id')}")
                print(f"      Descrição: {r.get('descr', '')}")
                print(f"      Tipo: {r.get('type')}")
                print(f"      Protocolo: {r.get('protocol')}")
                rule_443_ok = True
            else:
                print(f"   ❌ Nenhuma regra ativa encontrada!")
                rule_443_ok = False
            
            return rule_80_ok, rule_443_ok
        else:
            print(f"❌ Erro ao obter regras: {response.status_code}")
            return False, False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False, False

def test_traefik_internal():
    """Testa acesso interno ao Traefik"""
    print("\n" + "=" * 70)
    print("3. TESTANDO ACESSO INTERNO AO TRAEFIK")
    print("=" * 70)
    
    print(f"\n🔍 Teste 1: Traefik HTTPS (porta 9055) com Host header...")
    try:
        result = subprocess.run(
            ['curl', '-k', '-s', '-o', '/dev/null', '-w', '%{http_code}',
             '-H', 'Host: mail.ligbox.com.br',
             f'https://{TRAEFIK_IP}:{TRAEFIK_HTTPS_PORT}'],
            timeout=10,
            capture_output=True,
            text=True
        )
        
        http_code = result.stdout.strip()
        
        if http_code and http_code != '000' and http_code.isdigit():
            code = int(http_code)
            if code in [200, 301, 302, 307, 308]:
                print(f"   ✅ SUCESSO! HTTP {code}")
                print(f"      Traefik está roteando corretamente para Carbonio")
                
                # Mostrar headers completos
                print(f"\n   📋 Headers completos:")
                result2 = subprocess.run(
                    ['curl', '-k', '-s', '-I',
                     '-H', 'Host: mail.ligbox.com.br',
                     f'https://{TRAEFIK_IP}:{TRAEFIK_HTTPS_PORT}'],
                    timeout=10,
                    capture_output=True,
                    text=True
                )
                print(result2.stdout[:500])
                return True
            else:
                print(f"   ⚠️  Resposta HTTP {code} (pode ser erro)")
                return False
        else:
            print(f"   ❌ Falha na conexão")
            print(f"      Erro: {result.stderr[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ❌ Timeout - Traefik não respondeu")
        return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_traefik_http():
    """Testa acesso HTTP ao Traefik"""
    print(f"\n🔍 Teste 2: Traefik HTTP (porta 8055) com Host header...")
    try:
        result = subprocess.run(
            ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
             '-H', 'Host: mail.ligbox.com.br',
             f'http://{TRAEFIK_IP}:{TRAEFIK_HTTP_PORT}'],
            timeout=10,
            capture_output=True,
            text=True
        )
        
        http_code = result.stdout.strip()
        
        if http_code and http_code != '000' and http_code.isdigit():
            code = int(http_code)
            if code in [200, 301, 302, 307, 308]:
                print(f"   ✅ SUCESSO! HTTP {code}")
                return True
            else:
                print(f"   ⚠️  Resposta HTTP {code}")
                return False
        else:
            print(f"   ❌ Falha na conexão")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_carbonio_direct():
    """Testa acesso direto ao Carbonio"""
    print(f"\n🔍 Teste 3: Acesso direto ao Carbonio...")
    try:
        result = subprocess.run(
            ['curl', '-k', '-s', '-o', '/dev/null', '-w', '%{http_code}',
             f'https://{CARBONIO_IP}:{CARBONIO_PORT}'],
            timeout=10,
            capture_output=True,
            text=True
        )
        
        http_code = result.stdout.strip()
        
        if http_code and http_code != '000' and http_code.isdigit():
            code = int(http_code)
            if code in [200, 301, 302, 307, 308]:
                print(f"   ✅ SUCESSO! HTTP {code}")
                print(f"      Carbonio está respondendo diretamente")
                return True
            else:
                print(f"   ⚠️  Resposta HTTP {code}")
                return False
        else:
            print(f"   ❌ Falha na conexão")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("\n" + "=" * 70)
    print("VERIFICAÇÃO COMPLETA - TRAEFIK + CARBONIO")
    print("=" * 70)
    
    results = {
        'port_forward_80': False,
        'port_forward_443': False,
        'firewall_rule_80': False,
        'firewall_rule_443': False,
        'traefik_https': False,
        'traefik_http': False,
        'carbonio_direct': False
    }
    
    # 1. Verificar port forwards
    pf_80_ok, pf_443_ok = check_port_forwards()
    results['port_forward_80'] = pf_80_ok
    results['port_forward_443'] = pf_443_ok
    
    # 2. Verificar regras de firewall
    fw_80_ok, fw_443_ok = check_firewall_rules()
    results['firewall_rule_80'] = fw_80_ok
    results['firewall_rule_443'] = fw_443_ok
    
    # 3. Testar cadeia interna
    results['traefik_https'] = test_traefik_internal()
    results['traefik_http'] = test_traefik_http()
    results['carbonio_direct'] = test_carbonio_direct()
    
    # Resumo final
    print("\n" + "=" * 70)
    print("RESUMO DA VERIFICAÇÃO")
    print("=" * 70)
    
    print(f"\n✅ Configuração pfSense:")
    print(f"   Port Forward 80: {'✅ OK' if results['port_forward_80'] else '❌ FALTA'}")
    print(f"   Port Forward 443: {'✅ OK' if results['port_forward_443'] else '❌ FALTA'}")
    print(f"   Firewall Rule 80: {'✅ OK' if results['firewall_rule_80'] else '❌ FALTA'}")
    print(f"   Firewall Rule 443: {'✅ OK' if results['firewall_rule_443'] else '❌ FALTA'}")
    
    print(f"\n✅ Testes de Conectividade:")
    print(f"   Traefik HTTPS (9055): {'✅ OK' if results['traefik_https'] else '❌ FALHOU'}")
    print(f"   Traefik HTTP (8055): {'✅ OK' if results['traefik_http'] else '❌ FALHOU'}")
    print(f"   Carbonio Direto: {'✅ OK' if results['carbonio_direct'] else '❌ FALHOU'}")
    
    # Verificar se tudo está OK
    all_ok = all(results.values())
    
    if all_ok:
        print(f"\n✅ TUDO CONFIGURADO CORRETAMENTE!")
        print(f"   A cadeia completa está funcionando:")
        print(f"   Internet → pfSense → Traefik → Carbonio")
    else:
        print(f"\n⚠️  ALGUMAS CONFIGURAÇÕES FALTANDO OU COM PROBLEMAS")
        print(f"\n📋 Ações necessárias:")
        
        if not results['port_forward_80']:
            print(f"   - Configurar Port Forward: 80 → {TRAEFIK_IP}:{TRAEFIK_HTTP_PORT}")
        if not results['port_forward_443']:
            print(f"   - Configurar Port Forward: 443 → {TRAEFIK_IP}:{TRAEFIK_HTTPS_PORT}")
        if not results['firewall_rule_80']:
            print(f"   - Criar regra Firewall WAN: Allow TCP port 80")
        if not results['firewall_rule_443']:
            print(f"   - Criar regra Firewall WAN: Allow TCP port 443")
        if not results['traefik_https']:
            print(f"   - Verificar Traefik: docker logs traefik")
            print(f"   - Verificar configuração: mail.ligbox.com.br → {CARBONIO_IP}:{CARBONIO_PORT}")
        if not results['carbonio_direct']:
            print(f"   - Verificar Carbonio: https://{CARBONIO_IP}:{CARBONIO_PORT}")
    
    return 0 if all_ok else 1

if __name__ == '__main__':
    sys.exit(main())

