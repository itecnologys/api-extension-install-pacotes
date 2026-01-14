#!/usr/bin/env python3
"""
Script para remover e reinstalar o Snort no pfSense via API
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

def get_package_info():
    """Obtém informações do pacote Snort"""
    try:
        response = requests.get(
            f'{PFSENSE_URL}system/packages',
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            packages = data.get('data', [])
            
            for pkg in packages:
                if 'snort' in pkg.get('name', '').lower():
                    return pkg
        return None
    except Exception as e:
        print(f"❌ Erro ao obter informações: {e}")
        return None

def remove_package(pkg_id):
    """Remove o pacote Snort"""
    print(f"\n🗑️  Removendo pacote (ID: {pkg_id})...")
    
    try:
        response = requests.delete(
            f'{PFSENSE_URL}system/package?id={pkg_id}',
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=60
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 204]:
            print("   ✅ Pacote removido com sucesso!")
            return True
        else:
            try:
                error = response.json()
                print(f"   ⚠️  Erro: {error.get('message', '')}")
            except:
                print(f"   ⚠️  Resposta: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def install_package():
    """Instala o pacote Snort"""
    print(f"\n📦 Instalando pacote: {PACKAGE_NAME}...")
    
    try:
        payload = {'name': PACKAGE_NAME}
        
        response = requests.post(
            f'{PFSENSE_URL}system/package',
            json=payload,
            auth=HTTPBasicAuth(PFSENSE_USER, PFSENSE_PASSWORD),
            verify=False,
            timeout=180  # Timeout maior para instalação completa
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Instalação iniciada com sucesso!")
            try:
                data = response.json()
                if 'data' in data:
                    print(f"   Pacote instalado: {data['data'].get('name', '')}")
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

def main():
    """Função principal"""
    print("=" * 70)
    print("REINSTALAÇÃO DO SNORT NO PFSENSE")
    print("=" * 70)
    
    # Verificar se o pacote existe
    pkg = get_package_info()
    
    if pkg:
        print(f"\n✅ Pacote encontrado:")
        print(f"   Nome: {pkg.get('name')}")
        print(f"   Versão: {pkg.get('installed_version', 'N/A')}")
        print(f"   ID: {pkg.get('id')}")
        
        print("\n⚠️  O pacote está instalado mas o serviço não aparece.")
        print("   Vamos remover e reinstalar para corrigir o problema.")
        
        # Remover
        if remove_package(pkg.get('id')):
            print("\n⏳ Aguardando 10 segundos antes de reinstalar...")
            time.sleep(10)
            
            # Reinstalar
            if install_package():
                print("\n⏳ Aguardando 15 segundos para a instalação processar...")
                time.sleep(15)
                
                # Verificar
                new_pkg = get_package_info()
                if new_pkg:
                    print("\n✅ Reinstalação concluída!")
                    print("\n⚠️  IMPORTANTE:")
                    print("   1. Faça um REBOOT COMPLETO do pfSense")
                    print("   2. Após o reboot, verifique: Services > Snort")
                    print("   3. O serviço deve aparecer após o reboot")
                else:
                    print("\n⚠️  Pacote não encontrado após reinstalação.")
                    print("   Aguarde alguns minutos e verifique novamente.")
            else:
                print("\n❌ Falha na reinstalação via API")
                print("   Tente reinstalar manualmente via interface web")
        else:
            print("\n❌ Falha na remoção via API")
            print("   Tente remover manualmente via interface web")
    else:
        print("\n⚠️  Pacote não encontrado. Tentando instalar...")
        
        if install_package():
            print("\n✅ Instalação iniciada!")
            print("\n⚠️  IMPORTANTE:")
            print("   1. Aguarde alguns minutos para a instalação completar")
            print("   2. Faça um REBOOT COMPLETO do pfSense")
            print("   3. Após o reboot, verifique: Services > Snort")
        else:
            print("\n❌ Falha na instalação via API")
            print("   Tente instalar manualmente via interface web")
    
    print("\n" + "=" * 70)
    print("INSTRUÇÕES MANUAIS (se a API não funcionar)")
    print("=" * 70)
    print("\n1. Acesse: https://firewall.itecnologys.com")
    print("2. Vá em: System > Package Manager > Installed Packages")
    print("3. Encontre: pfSense-pkg-snort")
    print("4. Clique em: Remove")
    print("5. Aguarde a remoção")
    print("6. Vá em: Available Packages")
    print("7. Busque: Snort")
    print("8. Clique em: Install")
    print("9. Aguarde a instalação")
    print("10. REBOOT o pfSense")
    print("11. Após reboot: Services > Snort (deve aparecer)")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

