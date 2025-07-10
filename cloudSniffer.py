#!/usr/bin/env python3
"""
Cloud Bucket Tester - Version 3.0
Test different bucket configurations across multiple cloud providers.
Author: TheZakMan
"""

import random
import requests
import subprocess
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import json
import time
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from colorama import init, Fore, Back, Style

import random
from colorama import Fore, Style

def banner():
    b1 = f"""
{Fore.MAGENTA + Style.BRIGHT}
 .d8888b.  888                        888  .d8888b.           d8b  .d888  .d888
d88P  Y88b 888                        888 d88P  Y88b          Y8P d88P"  d88P" 
888    888 888                        888 Y88b.                   888    888   ,--.
888        888  .d88b.  888  888  .d88888  "Y888b.   88888b.  888 888888 888888    )
888        888 d88""88b 888  888 d88" 888     "Y88b. 888 "88b 888 888    888     _'-. _
888    888 888 888  888 888  888 888  888       "888 888  888 888 888    888    (    ) ),--.
Y88b  d88P 888 Y88..88P Y88b 888 Y88b 888 Y88b  d88P 888  888 888 888    888                )-._
 "Y8888P"  888  "Y88P"   "Y88888  "Y88888  "Y8888P"  888  888 888 888    888 ___________________)
"""

    b2 = f"""
{Fore.GREEN}
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
"""

    print(random.choice([b1, b2]))
    print(f"{Fore.RESET}{Fore.CYAN + Style.BRIGHT}☁️ Cloud Bucket Tester - v3.0{Fore.RESET}")
    print(f"{Fore.YELLOW}https://github.com/thezakman/cloudsniff{Fore.RESET}")

# Inicializa colorama
init(autoreset=True)

class Colors:
    """Classe para cores padronizadas"""
    SUCCESS = Fore.GREEN
    ERROR = Fore.RED
    WARNING = Fore.YELLOW
    INFO = Fore.CYAN
    HEADER = Fore.MAGENTA + Style.BRIGHT
    SUBHEADER = Fore.BLUE + Style.BRIGHT
    BOLD = Style.BRIGHT
    RESET = Style.RESET_ALL

class CloudBucketTester:
    def __init__(self, timeout: int = 10, workers: int = 15, aws_profile: Optional[str] = None):
        self.timeout = timeout
        self.workers = workers
        self.aws_profile = aws_profile
        self.results = []
        
    def test_http_endpoint(self, url: str, method: str = 'GET') -> Dict[str, Any]:
        """Testa endpoint HTTP/HTTPS"""
        try:
            response = requests.request(
                method=method,
                url=url,
                timeout=self.timeout,
                allow_redirects=True,
                verify=True
            )
            return {
                'url': url,
                'method': method,
                'status_code': response.status_code,
                'accessible': response.status_code < 500,  # Considera 4xx como acessível
                'headers': dict(response.headers),
                'size': len(response.content) if response.content else 0,
                'error': None,
                'response_time': response.elapsed.total_seconds()
            }
        except requests.exceptions.RequestException as e:
            return {
                'url': url,
                'method': method,
                'status_code': None,
                'accessible': False,
                'headers': {},
                'size': 0,
                'error': str(e),
                'response_time': 0
            }
    
    def test_aws_cli(self, bucket: str, no_sign_request: bool = False) -> Dict[str, Any]:
        """Testa AWS CLI"""
        cmd = ['aws', 's3', 'ls', f's3://{bucket}']
        if no_sign_request:
            cmd.append('--no-sign-request')
        if self.aws_profile:
            cmd.extend(['--profile', self.aws_profile])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            return {
                'command': ' '.join(cmd),
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode,
                'error': None
            }
        except subprocess.TimeoutExpired:
            return {
                'command': ' '.join(cmd),
                'success': False,
                'stdout': '',
                'stderr': 'Timeout',
                'return_code': -1,
                'error': 'Command timeout'
            }
        except Exception as e:
            return {
                'command': ' '.join(cmd),
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'return_code': -1,
                'error': str(e)
            }
    
    def test_gcp_cli(self, bucket: str) -> Dict[str, Any]:
        """Testa Google Cloud CLI"""
        cmd = ['gsutil', 'ls', f'gs://{bucket}']
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            return {
                'command': ' '.join(cmd),
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode,
                'error': None
            }
        except Exception as e:
            return {
                'command': ' '.join(cmd),
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'return_code': -1,
                'error': str(e)
            }
    
    def test_azure_cli(self, bucket: str) -> Dict[str, Any]:
        """Testa Azure CLI"""
        cmd = ['az', 'storage', 'blob', 'list', '--container-name', bucket]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            return {
                'command': ' '.join(cmd),
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode,
                'error': None
            }
        except Exception as e:
            return {
                'command': ' '.join(cmd),
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'return_code': -1,
                'error': str(e)
            }
    
    def generate_aws_urls(self, bucket: str) -> List[str]:
        """Gera URLs para AWS S3"""
        regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1', 'sa-east-1', 'us-east-2', 'eu-central-1']
        urls = []
        
        for region in regions:
            # Formato path-style
            urls.append(f'https://s3.{region}.amazonaws.com/{bucket}')
            urls.append(f'https://s3.{region}.amazonaws.com/{bucket}/')
            # Formato virtual-hosted-style
            urls.append(f'https://{bucket}.s3.{region}.amazonaws.com/')
            urls.append(f'https://{bucket}.s3.{region}.amazonaws.com')
            # Formato legacy
            if region == 'us-east-1':
                urls.append(f'https://s3.amazonaws.com/{bucket}')
                urls.append(f'https://s3.amazonaws.com/{bucket}/')
                urls.append(f'https://{bucket}.s3.amazonaws.com/')
                urls.append(f'https://{bucket}.s3.amazonaws.com')
        
        return urls
    
    def generate_gcp_urls(self, bucket: str) -> List[str]:
        """Gera URLs para Google Cloud Storage"""
        return [
            f'https://storage.googleapis.com/{bucket}',
            f'https://storage.googleapis.com/{bucket}/',
            f'https://{bucket}.storage.googleapis.com/',
            f'https://{bucket}.storage.googleapis.com',
            f'https://storage.cloud.google.com/{bucket}',
            f'https://storage.cloud.google.com/{bucket}/',
            f'https://console.cloud.google.com/storage/browser/{bucket}',
            f'https://www.googleapis.com/storage/v1/b/{bucket}/o',
        ]
    
    def generate_azure_urls(self, bucket: str) -> List[str]:
        """Gera URLs para Azure Blob Storage"""
        return [
            f'https://{bucket}.blob.core.windows.net/',
            f'https://{bucket}.blob.core.windows.net',
            f'https://{bucket}.blob.core.windows.net/?restype=container&comp=list',
            f'https://{bucket}.z1.web.core.windows.net/',
            f'https://{bucket}.z13.web.core.windows.net/',
            f'https://{bucket}.z22.web.core.windows.net/',
            f'https://{bucket}.azurewebsites.net/',
        ]
    
    def generate_firebase_urls(self, bucket: str) -> List[str]:
        """Gera URLs para Firebase Storage"""
        return [
            f'https://firebasestorage.googleapis.com/v0/b/{bucket}/o',
            f'https://firebasestorage.googleapis.com/v0/b/{bucket}.appspot.com/o',
            f'https://{bucket}.web.app/',
            f'https://{bucket}.firebaseapp.com/',
            f'https://{bucket}.firebaseio.com/',
        ]
    
    def generate_digitalocean_urls(self, bucket: str) -> List[str]:
        """Gera URLs para DigitalOcean Spaces"""
        regions = ['nyc3', 'ams3', 'sgp1', 'sfo3', 'fra1', 'blr1', 'syd1']
        urls = []
        
        for region in regions:
            urls.append(f'https://{bucket}.{region}.digitaloceanspaces.com/')
            urls.append(f'https://{bucket}.{region}.digitaloceanspaces.com')
            urls.append(f'https://{bucket}.{region}.cdn.digitaloceanspaces.com/')
            urls.append(f'https://{bucket}.{region}.cdn.digitaloceanspaces.com')
        
        return urls
    
    def generate_linode_urls(self, bucket: str) -> List[str]:
        """Gera URLs para Linode Object Storage"""
        regions = ['us-east-1', 'eu-central-1', 'ap-south-1', 'us-southeast-1']
        urls = []
        
        for region in regions:
            urls.append(f'https://{bucket}.{region}.linodeobjects.com/')
            urls.append(f'https://{bucket}.{region}.linodeobjects.com')
        
        return urls
    
    def generate_oracle_urls(self, bucket: str) -> List[str]:
        """Gera URLs para Oracle Cloud Storage"""
        regions = ['us-phoenix-1', 'us-ashburn-1', 'eu-frankfurt-1', 'ap-tokyo-1']
        urls = []
        
        for region in regions:
            urls.append(f'https://objectstorage.{region}.oraclecloud.com/n/namespace/b/{bucket}/o')
            urls.append(f'https://{bucket}.compat.objectstorage.{region}.oraclecloud.com/')
        
        return urls
    
    def generate_ibm_urls(self, bucket: str) -> List[str]:
        """Gera URLs para IBM Cloud Object Storage"""
        regions = ['us-south', 'eu-gb', 'ap-jp', 'us-east']
        urls = []
        
        for region in regions:
            urls.append(f'https://s3.{region}.cloud-object-storage.appdomain.cloud/{bucket}')
            urls.append(f'https://{bucket}.s3.{region}.cloud-object-storage.appdomain.cloud/')
        
        return urls
    
    def generate_backblaze_urls(self, bucket: str) -> List[str]:
        """Gera URLs para Backblaze B2"""
        return [
            f'https://f000.backblazeb2.com/file/{bucket}',
            f'https://f001.backblazeb2.com/file/{bucket}',
            f'https://f002.backblazeb2.com/file/{bucket}',
            f'https://f003.backblazeb2.com/file/{bucket}',
        ]
    
    def generate_wasabi_urls(self, bucket: str) -> List[str]:
        """Gera URLs para Wasabi Cloud Storage"""
        regions = ['us-east-1', 'us-east-2', 'us-west-1', 'eu-central-1', 'ap-northeast-1']
        urls = []
        
        for region in regions:
            urls.append(f'https://s3.{region}.wasabisys.com/{bucket}')
            urls.append(f'https://s3.{region}.wasabisys.com/{bucket}/')
            urls.append(f'https://{bucket}.s3.{region}.wasabisys.com/')
            urls.append(f'https://{bucket}.s3.{region}.wasabisys.com')
        
        return urls
    
    def generate_vultr_urls(self, bucket: str) -> List[str]:
        """Gera URLs para Vultr Object Storage"""
        regions = ['ewr1', 'sgp1', 'ams1', 'fra1', 'sjc1']
        urls = []
        
        for region in regions:
            urls.append(f'https://{bucket}.{region}.vultrobjects.com/')
            urls.append(f'https://{bucket}.{region}.vultrobjects.com')
        
        return urls
    
    def generate_scaleway_urls(self, bucket: str) -> List[str]:
        """Gera URLs para Scaleway Object Storage"""
        regions = ['fr-par', 'nl-ams', 'pl-waw']
        urls = []
        
        for region in regions:
            urls.append(f'https://s3.{region}.scw.cloud/{bucket}')
            urls.append(f'https://s3.{region}.scw.cloud/{bucket}/')
            urls.append(f'https://{bucket}.s3.{region}.scw.cloud/')
            urls.append(f'https://{bucket}.s3.{region}.scw.cloud')
        
        return urls
    
    def generate_ovh_urls(self, bucket: str) -> List[str]:
        """Gera URLs para OVH Object Storage"""
        regions = ['gra', 'sbg', 'rbx', 'bhs', 'waw', 'de', 'uk']
        urls = []
        
        for region in regions:
            urls.append(f'https://s3.{region}.cloud.ovh.net/{bucket}')
            urls.append(f'https://s3.{region}.cloud.ovh.net/{bucket}/')
            urls.append(f'https://{bucket}.s3.{region}.cloud.ovh.net/')
            urls.append(f'https://{bucket}.s3.{region}.cloud.ovh.net')
        
        return urls
    
    def generate_minio_urls(self, bucket: str) -> List[str]:
        """Gera URLs para MinIO (comum em ambientes self-hosted)"""
        common_ports = ['9000', '9001', '443', '80']
        common_hosts = ['minio', 's3', 'storage', 'object', 'bucket']
        urls = []
        
        for host in common_hosts:
            for port in common_ports:
                if port in ['443']:
                    urls.append(f'https://{host}:{port}/{bucket}')
                    urls.append(f'https://{host}:{port}/{bucket}/')
                elif port in ['80']:
                    urls.append(f'http://{host}:{port}/{bucket}')
                    urls.append(f'http://{host}:{port}/{bucket}/')
                else:
                    urls.append(f'http://{host}:{port}/{bucket}')
                    urls.append(f'http://{host}:{port}/{bucket}/')
                    urls.append(f'https://{host}:{port}/{bucket}')
                    urls.append(f'https://{host}:{port}/{bucket}/')
        
        return urls
    
    def generate_all_urls(self, bucket: str) -> List[str]:
        """Gera todas as URLs possíveis"""
        urls = []
        urls.extend(self.generate_aws_urls(bucket))
        urls.extend(self.generate_gcp_urls(bucket))
        urls.extend(self.generate_azure_urls(bucket))
        urls.extend(self.generate_firebase_urls(bucket))
        urls.extend(self.generate_digitalocean_urls(bucket))
        urls.extend(self.generate_linode_urls(bucket))
        urls.extend(self.generate_oracle_urls(bucket))
        urls.extend(self.generate_ibm_urls(bucket))
        urls.extend(self.generate_backblaze_urls(bucket))
        urls.extend(self.generate_wasabi_urls(bucket))
        urls.extend(self.generate_vultr_urls(bucket))
        urls.extend(self.generate_scaleway_urls(bucket))
        urls.extend(self.generate_ovh_urls(bucket))
        urls.extend(self.generate_minio_urls(bucket))
        
        return urls
    
    def test_advanced_aws_methods(self, bucket: str) -> List[Dict[str, Any]]:
        """Testes avançados específicos para AWS S3"""
        tests = []
        
        # Teste de website endpoints
        regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
        for region in regions:
            # Website endpoint format
            website_url = f'http://{bucket}.s3-website-{region}.amazonaws.com'
            tests.append(self.test_http_endpoint(website_url))
            
            # Alternative website format
            alt_website_url = f'http://{bucket}.s3-website.{region}.amazonaws.com'
            tests.append(self.test_http_endpoint(alt_website_url))
            
            # Transfer acceleration endpoint
            accel_url = f'https://{bucket}.s3-accelerate.amazonaws.com'
            tests.append(self.test_http_endpoint(accel_url))
            
            # Dual-stack endpoint
            dual_stack_url = f'https://{bucket}.s3.dualstack.{region}.amazonaws.com'
            tests.append(self.test_http_endpoint(dual_stack_url))
        
        return tests
    
    def test_advanced_gcp_methods(self, bucket: str) -> List[Dict[str, Any]]:
        """Testes avançados específicos para Google Cloud Storage"""
        tests = []
        
        # XML API endpoints
        xml_urls = [
            f'https://storage.googleapis.com/{bucket}?list-type=2',
            f'https://storage.googleapis.com/{bucket}?delimiter=%2F',
            f'https://{bucket}.storage.googleapis.com/?list-type=2',
        ]
        
        for url in xml_urls:
            tests.append(self.test_http_endpoint(url))
        
        # JSON API endpoints
        json_urls = [
            f'https://www.googleapis.com/storage/v1/b/{bucket}',
            f'https://www.googleapis.com/storage/v1/b/{bucket}/o',
            f'https://storage.googleapis.com/storage/v1/b/{bucket}',
        ]
        
        for url in json_urls:
            tests.append(self.test_http_endpoint(url))
        
        return tests
    
    def test_advanced_azure_methods(self, bucket: str) -> List[Dict[str, Any]]:
        """Testes avançados específicos para Azure Storage"""
        tests = []
        
        # REST API endpoints
        rest_urls = [
            f'https://{bucket}.blob.core.windows.net/?restype=container&comp=list&include=metadata',
            f'https://{bucket}.blob.core.windows.net/?restype=service&comp=properties',
            f'https://{bucket}.file.core.windows.net/',
            f'https://{bucket}.table.core.windows.net/',
            f'https://{bucket}.queue.core.windows.net/',
        ]
        
        for url in rest_urls:
            tests.append(self.test_http_endpoint(url))
        
        # CDN endpoints
        cdn_regions = ['akamai', 'verizon']
        for cdn in cdn_regions:
            cdn_url = f'https://{bucket}.azureedge.net/'
            tests.append(self.test_http_endpoint(cdn_url))
        
        return tests
    
    def sort_results_by_status(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ordena resultados por status code (200s primeiro, depois outros)"""
        def sort_key(result):
            status = result.get('status_code', 999)
            if status is None:
                return 999
            if 200 <= status < 300:
                return status
            if 300 <= status < 400:
                return status + 100
            if 400 <= status < 500:
                return status + 200
            return status + 300
        
        return sorted(results, key=sort_key)
    
    def filter_by_status_codes(self, results: List[Dict[str, Any]], status_codes: List[int]) -> List[Dict[str, Any]]:
        """Filtra resultados por status codes específicos"""
        return [r for r in results if r.get('status_code') in status_codes]
    
    def test_bucket_comprehensive(self, bucket: str, verbose: bool = False, status_filter: Optional[List[int]] = None, no_cli: bool = False) -> Dict[str, Any]:
        """Testa um bucket de forma abrangente"""
        if verbose:
            print(f"\n{Colors.HEADER}Testando bucket: {bucket}{Colors.RESET}")
        
        bucket_results = {
            'bucket': bucket,
            'timestamp': time.time(),
            'http_tests': [],
            'cli_tests': [],
            'advanced_tests': []
        }
        
        # Testa URLs HTTP
        urls = self.generate_all_urls(bucket)
        if verbose:
            print(f"{Colors.INFO}Testando {len(urls)} URLs HTTP...{Colors.RESET}")
        
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            future_to_url = {
                executor.submit(self.test_http_endpoint, url): url 
                for url in urls
            }
            
            for future in as_completed(future_to_url):
                result = future.result()
                bucket_results['http_tests'].append(result)
                
                if verbose and result['accessible']:
                    status = result['status_code']
                    time_ms = int(result['response_time'] * 1000)
                    
                    if status == 200:
                        color = Colors.SUCCESS
                    elif 200 <= status < 300:
                        color = Colors.SUCCESS
                    elif 300 <= status < 400:
                        color = Colors.WARNING
                    elif 400 <= status < 500:
                        color = Colors.WARNING
                    else:
                        color = Colors.ERROR
                    
                    print(f"{color}[{status}] {result['url']} ({time_ms}ms){Colors.RESET}")
        
        # Testes avançados específicos por provedor
        if verbose:
            print(f"\n{Colors.SUBHEADER}Executando testes avançados...{Colors.RESET}")
        
        # Testes avançados AWS
        aws_advanced = self.test_advanced_aws_methods(bucket)
        bucket_results['advanced_tests'].extend(aws_advanced)
        
        # Testes avançados GCP
        gcp_advanced = self.test_advanced_gcp_methods(bucket)
        bucket_results['advanced_tests'].extend(gcp_advanced)
        
        # Testes avançados Azure
        azure_advanced = self.test_advanced_azure_methods(bucket)
        bucket_results['advanced_tests'].extend(azure_advanced)
        
        # Ordena resultados por status code
        bucket_results['http_tests'] = self.sort_results_by_status(bucket_results['http_tests'])
        bucket_results['advanced_tests'] = self.sort_results_by_status(bucket_results['advanced_tests'])
        
        # Aplica filtro de status codes se especificado
        if status_filter:
            bucket_results['http_tests'] = self.filter_by_status_codes(bucket_results['http_tests'], status_filter)
            bucket_results['advanced_tests'] = self.filter_by_status_codes(bucket_results['advanced_tests'], status_filter)
        
        # Testa CLI apenas se não for especificado --no-cli
        if not no_cli:
            # Testa AWS CLI
            if verbose:
                print(f"\n{Colors.SUBHEADER}Testando AWS CLI...{Colors.RESET}")
            
            aws_test = self.test_aws_cli(bucket)
            bucket_results['cli_tests'].append(aws_test)
            
            aws_no_sign_test = self.test_aws_cli(bucket, no_sign_request=True)
            bucket_results['cli_tests'].append(aws_no_sign_test)
            
            if verbose:
                if aws_test['success']:
                    print(f"{Colors.SUCCESS}AWS CLI (autenticado): OK{Colors.RESET}")
                else:
                    print(f"{Colors.ERROR}AWS CLI (autenticado): ERRO{Colors.RESET}")
                
                if aws_no_sign_test['success']:
                    print(f"{Colors.SUCCESS}AWS CLI (público): OK{Colors.RESET}")
                else:
                    print(f"{Colors.ERROR}AWS CLI (público): ERRO{Colors.RESET}")
            
            # Testa GCP CLI
            if verbose:
                print(f"\n{Colors.SUBHEADER}Testando Google Cloud CLI...{Colors.RESET}")
            
            gcp_test = self.test_gcp_cli(bucket)
            bucket_results['cli_tests'].append(gcp_test)
            
            if verbose:
                if gcp_test['success']:
                    print(f"{Colors.SUCCESS}GCP CLI: OK{Colors.RESET}")
                else:
                    print(f"{Colors.ERROR}GCP CLI: ERRO{Colors.RESET}")
            
            # Testa Azure CLI
            if verbose:
                print(f"\n{Colors.SUBHEADER}Testando Azure CLI...{Colors.RESET}")
            
            azure_test = self.test_azure_cli(bucket)
            bucket_results['cli_tests'].append(azure_test)
            
            if verbose:
                if azure_test['success']:
                    print(f"{Colors.SUCCESS}Azure CLI: OK{Colors.RESET}")
                else:
                    print(f"{Colors.ERROR}Azure CLI: ERRO{Colors.RESET}")
        
        return bucket_results
    
    def test_buckets(self, buckets: List[str], verbose: bool = False, status_filter: Optional[List[int]] = None, no_cli: bool = False) -> List[Dict[str, Any]]:
        """Testa uma lista de buckets"""
        results = []
        
        for i, bucket in enumerate(buckets, 1):
            if not verbose:
                print(f"{Colors.INFO}[{i}/{len(buckets)}] {bucket}{Colors.RESET}", end=' ')
            
            result = self.test_bucket_comprehensive(bucket, verbose, status_filter, no_cli)
            results.append(result)
            
            if not verbose:
                # Mostra apenas resultados positivos
                accessible_urls = [t for t in result['http_tests'] if t['accessible']]
                advanced_accessible = [t for t in result.get('advanced_tests', []) if t['accessible']]
                successful_cli = [t for t in result['cli_tests'] if t['success']]
                
                total_accessible = len(accessible_urls) + len(advanced_accessible)
                
                if total_accessible > 0 or successful_cli:
                    print(f"{Colors.SUCCESS}FOUND{Colors.RESET}")
                    
                    # Mostra URLs HTTP regulares
                    for test in accessible_urls[:2]:  # Mostra apenas os 2 primeiros
                        status = test['status_code']
                        if status == 200:
                            color = Colors.SUCCESS
                        elif 200 <= status < 300:
                            color = Colors.SUCCESS
                        elif 300 <= status < 400:
                            color = Colors.WARNING
                        else:
                            color = Colors.WARNING
                        print(f"  {color}[{status}] {test['url']}{Colors.RESET}")
                    
                    # Mostra URLs avançadas
                    for test in advanced_accessible[:2]:  # Mostra apenas os 2 primeiros
                        status = test['status_code']
                        if status == 200:
                            color = Colors.SUCCESS
                        elif 200 <= status < 300:
                            color = Colors.SUCCESS
                        elif 300 <= status < 400:
                            color = Colors.WARNING
                        else:
                            color = Colors.WARNING
                        print(f"  {color}[{status}] {test['url']} (advanced){Colors.RESET}")
                    
                    if total_accessible > 4:
                        print(f"  {Colors.INFO}... e mais {total_accessible - 4} URLs{Colors.RESET}")
                    
                    for test in successful_cli:
                        print(f"  {Colors.SUCCESS}CLI: {test['command']}{Colors.RESET}")
                else:
                    print(f"{Colors.ERROR}NONE{Colors.RESET}")
        
        return results
    
    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """Gera relatório resumido dos resultados"""
        total_buckets = len(results)
        accessible_buckets = 0
        total_accessible_urls = 0
        total_advanced_urls = 0
        total_successful_cli = 0
        
        report = f"\n{Colors.HEADER}{'='*60}\n"
        report += f"              RELATÓRIO DE RESULTADOS v3.0\n"
        report += f"{'='*60}{Colors.RESET}\n"
        
        for result in results:
            bucket = result['bucket']
            accessible_urls = [t for t in result['http_tests'] if t['accessible']]
            advanced_urls = [t for t in result.get('advanced_tests', []) if t['accessible']]
            successful_cli = [t for t in result['cli_tests'] if t['success']]
            
            total_accessible = len(accessible_urls) + len(advanced_urls)
            
            if total_accessible > 0 or successful_cli:
                accessible_buckets += 1
                total_accessible_urls += len(accessible_urls)
                total_advanced_urls += len(advanced_urls)
                total_successful_cli += len(successful_cli)
                
                report += f"\n{Colors.SUBHEADER}BUCKET: {bucket}{Colors.RESET}\n"
                
                if accessible_urls:
                    report += f"   {Colors.INFO}URLs padrão encontradas ({len(accessible_urls)}){Colors.RESET}:\n"
                    # Agrupa por status code
                    status_groups = {}
                    for test in accessible_urls:
                        status = test['status_code']
                        if status not in status_groups:
                            status_groups[status] = []
                        status_groups[status].append(test)
                    
                    for status in sorted(status_groups.keys()):
                        tests = status_groups[status]
                        if status == 200:
                            color = Colors.SUCCESS
                        elif 200 <= status < 300:
                            color = Colors.SUCCESS
                        elif 300 <= status < 400:
                            color = Colors.WARNING
                        else:
                            color = Colors.WARNING
                        
                        report += f"     {color}[{status}] ({len(tests)} URLs){Colors.RESET}\n"
                        for test in tests[:3]:  # Mostra apenas os 3 primeiros de cada status
                            report += f"       {test['url']}\n"
                        if len(tests) > 3:
                            report += f"       ... e mais {len(tests) - 3} URLs\n"
                
                if advanced_urls:
                    report += f"   {Colors.INFO}URLs avançadas encontradas ({len(advanced_urls)}){Colors.RESET}:\n"
                    # Agrupa por status code
                    status_groups = {}
                    for test in advanced_urls:
                        status = test['status_code']
                        if status not in status_groups:
                            status_groups[status] = []
                        status_groups[status].append(test)
                    
                    for status in sorted(status_groups.keys()):
                        tests = status_groups[status]
                        if status == 200:
                            color = Colors.SUCCESS
                        elif 200 <= status < 300:
                            color = Colors.SUCCESS
                        elif 300 <= status < 400:
                            color = Colors.WARNING
                        else:
                            color = Colors.WARNING
                        
                        report += f"     {color}[{status}] ({len(tests)} URLs){Colors.RESET}\n"
                        for test in tests[:3]:  # Mostra apenas os 3 primeiros de cada status
                            report += f"       {test['url']}\n"
                        if len(tests) > 3:
                            report += f"       ... e mais {len(tests) - 3} URLs\n"
                
                if successful_cli:
                    report += f"   {Colors.INFO}CLI comandos ({len(successful_cli)}){Colors.RESET}:\n"
                    for test in successful_cli:
                        report += f"     {Colors.SUCCESS}{test['command']}{Colors.RESET}\n"
        
        report += f"\n{Colors.HEADER}ESTATÍSTICAS{Colors.RESET}:\n"
        report += f"   Buckets testados: {Colors.BOLD}{total_buckets}{Colors.RESET}\n"
        report += f"   Buckets encontrados: {Colors.SUCCESS}{accessible_buckets}{Colors.RESET}\n"
        report += f"   URLs padrão acessíveis: {Colors.SUCCESS}{total_accessible_urls}{Colors.RESET}\n"
        report += f"   URLs avançadas acessíveis: {Colors.SUCCESS}{total_advanced_urls}{Colors.RESET}\n"
        report += f"   CLI sucessos: {Colors.SUCCESS}{total_successful_cli}{Colors.RESET}\n"
        
        if accessible_buckets == 0:
            report += f"\n{Colors.ERROR}Nenhum bucket acessível encontrado.{Colors.RESET}\n"
        
        return report
    
    def save_results(self, results: List[Dict[str, Any]], filename: Optional[str] = None):
        """Salva resultados em arquivo JSON com timestamp automático"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'bucket_test_results_{timestamp}.json'
        
        # Adiciona metadados ao resultado
        output_data = {
            'metadata': {
                'version': '3.0',
                'timestamp': datetime.now().isoformat(),
                'total_buckets': len(results),
                'tool': 'CloudSniff'
            },
            'results': results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"\n{Colors.INFO}Resultados salvos em: {filename}{Colors.RESET}")

def load_buckets_from_file(filename: str) -> List[str]:
    """Carrega lista de buckets de um arquivo TXT"""
    buckets = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                bucket = line.strip()
                if bucket and not bucket.startswith('#'):  # Ignora linhas vazias e comentários
                    buckets.append(bucket)
        return buckets
    except FileNotFoundError:
        print(f"{Colors.ERROR}Arquivo não encontrado: {filename}{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.ERROR}Erro ao ler arquivo {filename}: {e}{Colors.RESET}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Cloud Bucket Tester v3.0 - Testa buckets em diferentes provedores de cloud')
    
    parser.add_argument('buckets', nargs='*', help='Nome(s) do(s) bucket(s) para testar')
    parser.add_argument('--list', '-l', type=str, help='Arquivo TXT com lista de buckets (um por linha)')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout em segundos (padrão: 10)')
    parser.add_argument('--workers', type=int, default=15, help='Número de threads para testes paralelos (padrão: 15)')
    parser.add_argument('--output', type=str, help='Arquivo para salvar resultados JSON (padrão: timestamp automático)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verboso')
    parser.add_argument('--status', type=str, help='Filtrar por status codes (ex: 200,403,404)')
    parser.add_argument('--profile', type=str, help='Perfil AWS para usar com AWS CLI')
    parser.add_argument('--no-cli', action='store_true', help='Pular testes de CLI (apenas HTTP)')
    
    args = parser.parse_args()
    
    # Determina a lista de buckets
    if args.list:
        buckets = load_buckets_from_file(args.list)
        print(f"{Colors.INFO}Carregados {len(buckets)} buckets do arquivo: {args.list}{Colors.RESET}")
    elif args.buckets:
        buckets = args.buckets
    else:
        print(f"{Colors.ERROR}Especifique buckets diretamente ou use --list para carregar de arquivo!{Colors.RESET}")
        print("Exemplos:")
        print("  python3 cloudSniff.py bucket1 bucket2")
        print("  python3 cloudSniff.py --list buckets.txt")
        print("  python3 cloudSniff.py --list buckets.txt --status 200,403")
        print("  python3 cloudSniff.py --list buckets.txt --workers 25 --no-cli")
        print("  python3 cloudSniff.py bucket1 --profile myprofile --verbose")
        sys.exit(1)
    
    # Processa filtro de status codes
    status_filter = None
    if args.status:
        try:
            status_filter = [int(s.strip()) for s in args.status.split(',')]
            print(f"{Colors.INFO}Filtrando por status codes: {status_filter}{Colors.RESET}")
        except ValueError:
            print(f"{Colors.ERROR}Status codes inválidos: {args.status}{Colors.RESET}")
            sys.exit(1)
    
    # Inicializa o tester com novos parâmetros
    tester = CloudBucketTester(
        timeout=args.timeout, 
        workers=args.workers, 
        aws_profile=args.profile
    )
    
    print(f"{Colors.HEADER}Iniciando testes de buckets...{Colors.RESET}")
    print(f"{Colors.INFO}Buckets a testar: {', '.join(buckets)}{Colors.RESET}")
    print(f"{Colors.INFO}Workers: {args.workers} | Timeout: {args.timeout}s{Colors.RESET}")
    
    if args.profile:
        print(f"{Colors.INFO}Usando perfil AWS: {args.profile}{Colors.RESET}")
    
    if args.no_cli:
        print(f"{Colors.WARNING}Modo --no-cli: pulando testes de linha de comando{Colors.RESET}")
    
    results = tester.test_buckets(buckets, verbose=args.verbose, status_filter=status_filter, no_cli=args.no_cli)
    
    # Gera e exibe relatório
    if not args.verbose:
        report = tester.generate_report(results)
        print(report)
    
    # Salva resultados
    tester.save_results(results, args.output)

if __name__ == '__main__':
    banner()
    main()
