# Cloud Bucket Tester
```
                              .--.
                         .-.,(    ).            
      .d8888b.  888  _.-(           ),-._  888  .d8888b.           d8b  .d888  .d888
     d88P  Y88b 888 (____________________) 888 d88P  Y88b          Y8P d88P"  d88P" 
     888    888 888                        888 Y88b.                   888    888
     888        888  .d88b.  888  888  .d88888  "Y888b.   88888b.  888 888888 888888
     888        888 d88""88b 888  888 d88" 888     "Y88b. 888 "88b 888 888    888
     888    888 888 888  888 888  888 888  888       "888 888  888 888 888    888
     Y88b  d88P 888 Y88..88P Y88b 888 Y88b 888 Y88b  d88P 888  888 888 888    888
      "Y8888P"  888  "Y88P"   "Y88888  "Y88888  "Y8888P"  888  888 888 888    888
```

O CloudSniff v3.0 é um testador avançado de buckets em múltiplos provedores de cloud com recursos expandidos e testes aprimorados.

## Novidades da v3.0

### Novos Parâmetros
- `--workers N` - Controla número de threads paralelas (padrão: 15)
- `--profile PERFIL` - Especifica perfil AWS para usar
- `--no-cli` - Pula testes de CLI (apenas HTTP)
- `--output ARQUIVO` - Arquivo personalizado de saída (com timestamp automático)

### Melhorias nos Relatórios
- Separação entre URLs padrão e avançadas
- Timestamps automáticos nos arquivos de saída
- Metadados detalhados nos resultados JSON
- Estatísticas expandidas

## Instalação

```bash
# Clone o repositório
git clone https://github.com/thezakman/cloudsniff.git
cd cloudsniff

# Instale as dependências
pip3 install -r requirements.txt

# Torne o script executável
chmod +x cloudSniff.py
```

## Exemplos de Uso

### Básico
```bash
# Teste um bucket específico
python3 cloudSniff.py meu-bucket

# Teste múltiplos buckets
python3 cloudSniff.py bucket1 bucket2 bucket3
```

### Com Lista de Buckets
```bash
# Carregue de arquivo TXT
python3 cloudSniff.py --list buckets.txt

# Com modo verboso
python3 cloudSniff.py --list buckets.txt --verbose
```

### Opções Avançadas
```bash
# Apenas testes HTTP (sem CLI)
python3 cloudSniff.py --list buckets.txt --no-cli

# Com mais workers para speed
python3 cloudSniff.py --list buckets.txt --workers 25

# Filtrar por status codes específicos
python3 cloudSniff.py --list buckets.txt --status 200,403,404

# Usar perfil AWS específico
python3 cloudSniff.py --list buckets.txt --profile production

# Timeout customizado
python3 cloudSniff.py --list buckets.txt --timeout 5

# Arquivo de saída personalizado
python3 cloudSniff.py --list buckets.txt --output meus_resultados.json
```

### Combinações Úteis
```bash
# Scan rápido sem CLI
python3 cloudSniff.py --list buckets.txt --no-cli --workers 30

# Scan completo com perfil AWS
python3 cloudSniff.py --list buckets.txt --profile pentest --verbose

# Apenas buckets com acesso público (200)
python3 cloudSniff.py --list buckets.txt --status 200
```

## Arquivo de Lista de Buckets

Crie um arquivo `buckets.txt` com um bucket por linha:

```
bennetto
getmailhive.com
glimages
gt40
lanternarius-carrierwave-storage
rcsclou
```

## Formato dos Resultados

Os resultados são salvos automaticamente em JSON com timestamp:

```json
{
  "metadata": {
    "version": "3.0",
    "timestamp": "2025-01-10T15:30:45",
    "total_buckets": 10,
    "tool": "CloudSniff"
  },
  "results": [
    {
      "bucket": "exemplo-bucket",
      "timestamp": 1641826245,
      "http_tests": [...],
      "cli_tests": [...],
      "advanced_tests": [...]
    }
  ]
}
```

## Tipos de Testes

### HTTP/HTTPS
- URLs padrão de todos os provedores
- Testes avançados específicos por provedor
- Verificação de redirecionamentos
- Medição de tempo de resposta

### CLI Tools
- AWS CLI (com e sem autenticação)
- Google Cloud CLI (gsutil)
- Azure CLI (az storage)

### Advanced Tests
- AWS: Website endpoints, acceleration endpoints
- GCP: XML/JSON APIs alternativas
- Azure: REST APIs, CDN endpoints

## Parâmetros Completos

```
positional arguments:
  buckets              Nome(s) do(s) bucket(s) para testar

optional arguments:
  -h, --help           Mostra esta mensagem e sai
  --list, -l FILE      Arquivo TXT com lista de buckets
  --timeout SECONDS    Timeout em segundos (padrão: 10)
  --workers N          Número de threads paralelas (padrão: 15)
  --output FILE        Arquivo para salvar resultados JSON
  --verbose, -v        Modo verboso com saída detalhada
  --status CODES       Filtrar por status codes (ex: 200,403,404)
  --profile PROFILE    Perfil AWS para usar com AWS CLI
  --no-cli             Pular testes de CLI (apenas HTTP)
```

## Nota Legal

Este tool é para fins educacionais e de teste de segurança autorizados. Use apenas em buckets que você possui ou tem permissão explícita para testar.

**TheZakMan**  
GitHub: [github.com/thezakman](https://github.com/thezakman)
