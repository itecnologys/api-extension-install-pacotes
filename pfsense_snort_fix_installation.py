#!/usr/bin/env python3
"""
Script para diagnosticar e corrigir problemas de instalação do Snort no pfSense
Autor: Auto Assistant
Data: 2025-01-14
"""

import requests
import json
import sys
import time
from requests.auth import HTTPBasicAuth
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Configurações da API pfSense
PFSENSE_URL = 'https://firewall.itecnologys.com/api/v2/'
PFSENSE_USER = 'api_cursor'
PFSENSE_PASSWORD = '805353'
PACKAGE_NAME = 'pfSense-pkg-snort'

def check_package_status():
    """Verifica o status do pacote Snort"""
    print("=" * 70)
    print("VERIFICANDO STATUS DO PACOTE SNORT")
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
            
            snort_packages = [
                p for p in packages 
                if 'snort' in p.get('name', '').lower()
            ]
            
            if snort_packages:
                pkg = snort_packages[0]
                print(f"\n✅ Pacote encontrado:")
                print(f"   Nome: {pkg.get('name')}")
                print(f"   Versão: {pkg.get('installed_version', 'N/A')}")
                print(f"   ID: {pkg.get('id')}")
                return pkg
            else:
                print("\n❌ Pacote Snort NÃO encontrado nos pacotes instalados!")
                return None
        else:
            print(f"❌ Erro ao verificar pacotes: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def reinstall_package():
    """Reinstala o pacote Snort"""
    print("\n" + "=" * 70)
    print("REINSTALANDO PACOTE SNORT")
    print("=" * 70)
    
    # Primeiro, remover o pacote
    print("\n📦 Passo 1: Removendo pacote existente...")
    pkg = check_package_status()
    
    if pkg:
        pkg_id = pkg.get('id')
        print(f"   ID do pacote: {pkg_id}")
        
        try:
            # Tentar remover via API
            response = requests.delete(
                f'{PFSENSE_URL}system/package?id={pkg_id}',
                auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
                verify=False,
                timeout=30
            )
            
            print(f"   Status da remoção: {response.status_code}")
            
            if response.status_code in [200, 204]:
                print("   ✅ Pacote removido com sucesso!")
            else:
                print(f"   ⚠️  Status inesperado: {response.status_code}")
                try:
                    error = response.json()
                    print(f"   Erro: {error.get('message', '')}")
                except:
                    print(f"   Resposta: {response.text[:200]}")
        except Exception as e:
            print(f"   ⚠️  Erro ao remover: {e}")
            print("   Você precisará remover manualmente via interface web")
    
    # Aguardar um pouco
    print("\n⏳ Aguardando 5 segundos...")
    time.sleep(5)
    
    # Reinstalar o pacote
    print("\n📦 Passo 2: Reinstalando pacote...")
    try:
        payload = {'name': PACKAGE_NAME}
        
        response = requests.post(
            f'{PFSENSE_URL}system/package',
            json=payload,
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=120  # Timeout maior para instalação
        )
        
        print(f"   Status da instalação: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Pacote reinstalado com sucesso!")
            try:
                data = response.json()
                print(f"   Resposta: {json.dumps(data, indent=2)[:500]}")
            except:
                pass
            return True
        else:
            print(f"   ⚠️  Status inesperado: {response.status_code}")
            try:
                error = response.json()
                print(f"   Erro: {error.get('message', '')}")
            except:
                print(f"   Resposta: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao reinstalar: {e}")
        return False

def verify_installation():
    """Verifica se a instalação foi bem-sucedida"""
    print("\n" + "=" * 70)
    print("VERIFICANDO INSTALAÇÃO")
    print("=" * 70)
    
    # Aguardar um pouco para o sistema processar
    print("\n⏳ Aguardando 10 segundos para o sistema processar...")
    time.sleep(10)
    
    pkg = check_package_status()
    
    if pkg:
        print("\n✅ Pacote está instalado!")
        print("\n⚠️  IMPORTANTE: Se o serviço ainda não aparecer na interface web:")
        print("   1. Faça um reboot completo do pfSense")
        print("   2. Após o reboot, verifique: Services > Snort")
        print("   3. Se ainda não aparecer, verifique os logs do sistema")
        return True
    else:
        print("\n❌ Pacote não está instalado!")
        return False

def print_manual_fix_instructions():
    """Imprime instruções para correção manual"""
    print("\n" + "=" * 70)
    print("INSTRUÇÕES PARA CORREÇÃO MANUAL")
    print("=" * 70)
    
    print("\n📋 OPÇÃO 1: Reinstalar via Interface Web")
    print("   1. Acesse: https://firewall.itecnologys.com")
    print("   2. Vá em: System > Package Manager > Installed Packages")
    print("   3. Encontre: pfSense-pkg-snort")
    print("   4. Clique em: Remove (remover completamente)")
    print("   5. Aguarde a remoção completar")
    print("   6. Vá em: Available Packages")
    print("   7. Busque por: Snort")
    print("   8. Clique em: Install")
    print("   9. Aguarde a instalação completar")
    print("   10. Faça um reboot do pfSense")
    print("   11. Após reboot, verifique: Services > Snort")
    
    print("\n📋 OPÇÃO 2: Verificar via Console/SSH")
    print("   1. Acesse o console do pfSense (via SSH ou console físico)")
    print("   2. Execute: pkg info | grep snort")
    print("   3. Se aparecer, execute: pkg install -f pfSense-pkg-snort")
    print("   4. Verifique dependências: pkg check -d")
    print("   5. Se houver problemas com libpcap:")
    print("      ln -s /usr/lib/libpcap.so /usr/lib/libpcap.so.1")
    print("   6. Reinicie o pfSense")
    
    print("\n📋 OPÇÃO 3: Verificar Logs")
    print("   1. Acesse: Status > System Logs > System")
    print("   2. Procure por erros relacionados a 'snort' ou 'pkg'")
    print("   3. Verifique se há problemas de dependências")
    
    print("\n📋 OPÇÃO 4: Atualizar Repositórios")
    print("   1. Via console/SSH, execute: pkg update -f")
    print("   2. Aguarde a atualização completar")
    print("   3. Tente reinstalar o Snort novamente")

def main():
    """Função principal"""
    print("\n" + "=" * 70)
    print("DIAGNÓSTICO E CORREÇÃO DO SNORT NO PFSENSE")
    print("=" * 70)
    
    # Verificar status atual
    pkg = check_package_status()
    
    if not pkg:
        print("\n⚠️  Pacote não está instalado. Tentando instalar...")
        try:
            payload = {'name': PACKAGE_NAME}
            response = requests.post(
                f'{PFSENSE_URL}system/package',
                json=payload,
                auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
                verify=False,
                timeout=120
            )
            
            if response.status_code == 200:
                print("✅ Instalação iniciada!")
                verify_installation()
            else:
                print("❌ Falha na instalação via API")
                print_manual_fix_instructions()
        except Exception as e:
            print(f"❌ Erro: {e}")
            print_manual_fix_instructions()
    else:
        print("\n⚠️  Pacote está instalado mas o serviço não aparece.")
        print("   Isso pode indicar:")
        print("   - Instalação incompleta")
        print("   - Dependências faltando")
        print("   - Problema de compatibilidade")
        print("   - Necessidade de reboot")
        
        resposta = input("\n❓ Deseja tentar reinstalar? (s/n): ").strip().lower()
        
        if resposta == 's':
            if reinstall_package():
                verify_installation()
            else:
                print_manual_fix_instructions()
        else:
            print_manual_fix_instructions()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

