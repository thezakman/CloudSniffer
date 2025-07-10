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

## Como Usar:

### Teste básico:
```
python3 cloudSniff.py bucket1 bucket2
```
### Com arquivo:
```
python3 cloudSniff.py --file buckets.txt
```
### Filtrar apenas status 200:
```
python3 cloudSniff.py --file buckets.txt --status 200
```
### Filtrar múltiplos status codes:
```
python3 cloudSniff.py --file buckets.txt --status 200,403,404
```
### Modo verboso:
```
python3 cloudSniff.py --file buckets.txt --verbose
```
