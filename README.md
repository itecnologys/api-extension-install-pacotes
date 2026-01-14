# API Extension - Instalação de Pacotes pfSense

Este repositório contém scripts para instalação e gerenciamento de pacotes no pfSense via API.

## Scripts Disponíveis

### `pfsense_install_snort.py`

Script Python para instalar o Snort no pfSense via API REST v2.

#### Funcionalidades

- ✅ Verifica se o Snort já está instalado
- ✅ Lista pacotes disponíveis
- ✅ Instala o Snort via API
- ✅ Valida a instalação

#### Requisitos

- Python 3.6+
- Biblioteca `requests`
- Acesso à API do pfSense (credenciais configuradas)

#### Configuração

Edite as variáveis no início do script:

```python
PFSENSE_URL = 'https://firewall.itecnologys.com/api/v2/'
PFSENSE_USER = 'api_cursor'
PFSENSE_PASSWORD = '805353'
PACKAGE_NAME = 'snort'
```

#### Uso

```bash
# Instalar Snort
python3 pfsense_install_snort.py
```

#### Método de Instalação

O script utiliza o endpoint da API do pfSense:

- **Endpoint**: `POST /api/v2/system/package`
- **Payload**: `{"name": "pfSense-pkg-snort"}`

#### Exemplo de Saída

```
======================================================================
INSTALAÇÃO DO SNORT NO PFSENSE VIA API
======================================================================
✅ Snort JÁ ESTÁ INSTALADO!
   Nome: pfSense-pkg-snort
   Versão instalada: 4.1.6_28
   Versão mais recente: 4.1.6_28
```

## Autor

Auto Assistant - itecnologys.com

## Licença

Este projeto é de uso interno da itecnologys.

