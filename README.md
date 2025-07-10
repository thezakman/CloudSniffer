## Como Usar:

# Teste básico
python3 cloudSniff.py bucket1 bucket2

# Com arquivo
python3 cloudSniff.py --file buckets.txt

# Filtrar apenas status 200
python3 cloudSniff.py --file buckets.txt --status 200

# Filtrar múltiplos status codes
python3 cloudSniff.py --file buckets.txt --status 200,403,404

# Modo verboso
python3 cloudSniff.py --file buckets.txt --verbose
