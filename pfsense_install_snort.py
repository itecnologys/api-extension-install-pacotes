#!/usr/bin/env python3
"""
Script para instalar Snort no pfSense via API ou CLI alternativo
Autor: Auto (assistente)
Data: 2025-01-XX
"""

import requests
import json
import sys
import time
from requests.auth import HTTPBasicAuth
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Configurações
PFSENSE_URL = 'https://firewall.itecnologys.com/api/v2/'
PFSENSE_USER = 'api_cursor'
PFSENSE_PASSWORD = '805353'
PACKAGE_NAME = 'snort'

def check_snort_status():
    """Verifica se Snort está instalado"""
    print("=" * 70)
    print("VERIFICANDO STATUS DO SNORT")
    print("=" * 70)
    
    try:
        # Verificar pacotes instalados
        response = requests.get(
            f'{PFSENSE_URL}system/packages',
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            packages = data.get('data', [])
            
            snort_installed = [
                p for p in packages 
                if 'snort' in p.get('name', '').lower() or 
                   'snort' in p.get('shortname', '').lower()
            ]
            
            if snort_installed:
                print(f"✅ Snort JÁ ESTÁ INSTALADO!")
                for pkg in snort_installed:
                    print(f"   Nome: {pkg.get('name')}")
                    print(f"   Versão instalada: {pkg.get('installed_version', 'N/A')}")
                    print(f"   Versão mais recente: {pkg.get('latest_version', 'N/A')}")
                return True
            else:
                print("⚠️  Snort NÃO está instalado")
                return False
        else:
            print(f"❌ Erro ao verificar pacotes: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def check_snort_available():
    """Verifica se Snort está disponível para instalação"""
    print("\n" + "=" * 70)
    print("VERIFICANDO SE SNORT ESTÁ DISPONÍVEL")
    print("=" * 70)
    
    try:
        response = requests.get(
            f'{PFSENSE_URL}system/package/available',
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            packages = data.get('data', [])
            
            snort_packages = [
                p for p in packages 
                if 'snort' in p.get('name', '').lower() or 
                   'snort' in p.get('shortname', '').lower()
            ]
            
            if snort_packages:
                print("✅ Snort está disponível para instalação:")
                for pkg in snort_packages:
                    print(f"   Nome completo: {pkg.get('name')}")
                    print(f"   Shortname: {pkg.get('shortname')}")
                    print(f"   Versão: {pkg.get('version', 'N/A')}")
                    print(f"   Descrição: {pkg.get('descr', '')[:100]}...")
                    print(f"   Instalado: {pkg.get('installed', False)}")
                return snort_packages[0]
            else:
                print("❌ Snort não encontrado nos pacotes disponíveis")
                return None
        else:
            print(f"❌ Erro ao verificar pacotes disponíveis: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def try_install_via_api(package_info):
    """Instala pacote via API do pfSense"""
    print("\n" + "=" * 70)
    print("INSTALANDO VIA API")
    print("=" * 70)
    
    # O método correto é usar POST em system/package com o nome completo do pacote
    package_name = package_info.get('name')  # Nome completo, ex: 'pfSense-pkg-snort'
    
    print(f"\n🔍 Instalando pacote: {package_name}")
    print(f"   Shortname: {package_info.get('shortname')}")
    print(f"   Versão: {package_info.get('version', 'N/A')}")
    
    try:
        url = f'{PFSENSE_URL}system/package'
        payload = {'name': package_name}
        
        print(f"\n📡 Enviando requisição POST para: {url}")
        print(f"   Payload: {payload}")
        
        response = requests.post(
            url,
            json=payload,
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=120  # Timeout maior para instalação
        )
        
        print(f"\n📊 Resposta da API:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ SUCESSO! Pacote instalado ou já estava instalado")
                print(f"\n📦 Informações do pacote instalado:")
                print(json.dumps(data.get('data', {}), indent=2))
                return True
            except:
                print(f"   ✅ Resposta (texto): {response.text[:500]}")
                return True
        elif response.status_code == 202:
            print(f"   ✅ Instalação aceita (202 Accepted)")
            return True
        else:
            try:
                error_data = response.json()
                print(f"   ⚠️  Erro: {error_data.get('message', '')}")
                print(f"   Detalhes: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   ⚠️  Resposta: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao instalar: {e}")
        return False

def main():
    """Função principal"""
    print("\n" + "=" * 70)
    print("INSTALAÇÃO DO SNORT NO PFSENSE VIA API")
    print("=" * 70)
    
    # 1. Verificar se já está instalado
    is_installed = check_snort_status()
    if is_installed:
        print("\n✅ Snort já está instalado. Nada a fazer.")
        return 0
    
    # 2. Verificar se está disponível
    package_info = check_snort_available()
    if not package_info:
        print("\n❌ Snort não está disponível para instalação.")
        return 1
    
    # 3. Instalar via API
    print("\n" + "=" * 70)
    print("INSTALAÇÃO VIA API")
    print("=" * 70)
    
    success = try_install_via_api(package_info)
    
    if success:
        # Verificar novamente o status após instalação
        print("\n" + "=" * 70)
        print("VERIFICANDO STATUS APÓS INSTALAÇÃO")
        print("=" * 70)
        
        time.sleep(2)  # Aguardar um pouco para a instalação processar
        
        is_installed_now = check_snort_status()
        if is_installed_now:
            print("\n✅ Snort instalado com sucesso via API!")
            print("\n📋 PRÓXIMOS PASSOS:")
            print("   1. Acesse a interface web: https://firewall.itecnologys.com")
            print("   2. Vá em: Services > Snort")
            print("   3. Configure as interfaces e regras conforme necessário")
            return 0
        else:
            print("\n⚠️  Instalação pode estar em andamento.")
            print("   Aguarde alguns minutos e verifique novamente.")
            return 0
    else:
        print("\n" + "=" * 70)
        print("❌ INSTALAÇÃO VIA API FALHOU")
        print("=" * 70)
        print("\n📋 ALTERNATIVAS:")
        print("\n1. INSTALAÇÃO VIA INTERFACE WEB:")
        print("   - Acesse: https://firewall.itecnologys.com")
        print("   - Vá em: System > Package Manager > Available Packages")
        print("   - Busque por 'Snort' e clique em 'Install'")
        
        print("\n2. INSTALAÇÃO VIA SSH (se tiver acesso):")
        print("   ssh root@firewall.itecnologys.com")
        print("   pkg install pfSense-pkg-snort")
        
        return 1

if __name__ == '__main__':
    sys.exit(main())

