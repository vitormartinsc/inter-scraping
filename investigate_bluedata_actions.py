#!/usr/bin/env python3
"""
Script para investigar ações do usuário BlueData na conta AWS
"""

import boto3
import json
from datetime import datetime, timedelta
import pandas as pd

def get_cloudtrail_events():
    """Busca eventos do CloudTrail dos últimos dias"""
    # CloudTrail para Identity Center deve usar us-east-1
    client = boto3.client('cloudtrail', region_name='us-east-1')
    
    # Buscar eventos dos últimos 7 dias
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    
    print(f"🔍 Buscando eventos do CloudTrail de {start_time.strftime('%Y-%m-%d')} até {end_time.strftime('%Y-%m-%d')}")
    
    try:
        response = client.lookup_events(
            LookupAttributes=[
                {
                    'AttributeKey': 'Username',
                    'AttributeValue': 'bluedata'
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            MaxResults=100
        )
        
        events = response.get('Events', [])
        print(f"📊 Encontrados {len(events)} eventos do usuário BlueData")
        
        return events
        
    except Exception as e:
        print(f"❌ Erro ao buscar eventos CloudTrail: {e}")
        return []

def analyze_iam_changes():
    """Analisa mudanças no IAM feitas por BlueData"""
    client = boto3.client('iam')
    
    print("\n🔐 Analisando usuários IAM...")
    
    try:
        # Listar usuários
        users = client.list_users()
        print(f"👥 Total de usuários: {len(users['Users'])}")
        
        for user in users['Users']:
            print(f"  - {user['UserName']} (criado em: {user['CreateDate']})")
            
            # Verificar políticas anexadas
            try:
                attached_policies = client.list_attached_user_policies(UserName=user['UserName'])
                if attached_policies['AttachedPolicies']:
                    print(f"    Políticas anexadas:")
                    for policy in attached_policies['AttachedPolicies']:
                        print(f"      - {policy['PolicyName']} ({policy['PolicyArn']})")
            except:
                pass
                
    except Exception as e:
        print(f"❌ Erro ao analisar IAM: {e}")

def analyze_ec2_changes():
    """Analisa mudanças no EC2"""
    client = boto3.client('ec2')
    
    print("\n🖥️  Analisando instâncias EC2...")
    
    try:
        # Listar instâncias
        reservations = client.describe_instances()
        
        for reservation in reservations['Reservations']:
            for instance in reservation['Instances']:
                print(f"  - Instância: {instance['InstanceId']}")
                print(f"    Estado: {instance['State']['Name']}")
                print(f"    Tipo: {instance['InstanceType']}")
                print(f"    Lançada em: {instance['LaunchTime']}")
                
                # Verificar tags
                if 'Tags' in instance:
                    print(f"    Tags:")
                    for tag in instance['Tags']:
                        print(f"      - {tag['Key']}: {tag['Value']}")
                print()
                
    except Exception as e:
        print(f"❌ Erro ao analisar EC2: {e}")

def analyze_s3_changes():
    """Analisa mudanças no S3"""
    client = boto3.client('s3')
    
    print("\n🗄️  Analisando buckets S3...")
    
    try:
        buckets = client.list_buckets()
        print(f"📦 Total de buckets: {len(buckets['Buckets'])}")
        
        for bucket in buckets['Buckets']:
            print(f"  - {bucket['Name']} (criado em: {bucket['CreationDate']})")
            
    except Exception as e:
        print(f"❌ Erro ao analisar S3: {e}")

def get_console_login_events():
    """Busca eventos de login no console"""
    # CloudTrail para Identity Center deve usar us-east-1
    client = boto3.client('cloudtrail', region_name='us-east-1')
    
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    
    print(f"\n🔑 Buscando eventos de login dos últimos 7 dias...")
    
    try:
        response = client.lookup_events(
            LookupAttributes=[
                {
                    'AttributeKey': 'EventName',
                    'AttributeValue': 'ConsoleLogin'
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            MaxResults=50
        )
        
        events = response.get('Events', [])
        print(f"🚪 Encontrados {len(events)} eventos de login")
        
        for event in events:
            event_time = event['EventTime'].strftime('%Y-%m-%d %H:%M:%S')
            username = event.get('Username', 'N/A')
            source_ip = 'N/A'
            
            # Extrair IP do evento
            if 'CloudTrailEvent' in event:
                try:
                    event_data = json.loads(event['CloudTrailEvent'])
                    source_ip = event_data.get('sourceIPAddress', 'N/A')
                except:
                    pass
                    
            print(f"  - {event_time}: {username} via {source_ip}")
            
    except Exception as e:
        print(f"❌ Erro ao buscar logins: {e}")

def main():
    print("🕵️  INVESTIGAÇÃO DE AÇÕES DO USUÁRIO BLUEDATA")
    print("=" * 50)
    
    # Verificar credenciais AWS
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"🔍 Investigando conta: {identity['Account']}")
        print(f"👤 Usuário atual: {identity.get('UserName', identity.get('Arn', 'N/A'))}")
        print()
    except Exception as e:
        print(f"❌ Erro ao verificar credenciais: {e}")
        return
    
    # Buscar eventos específicos do BlueData
    events = get_cloudtrail_events()
    
    if events:
        print("\n📋 EVENTOS DETALHADOS DO BLUEDATA:")
        print("-" * 40)
        
        for event in events[:10]:  # Mostrar últimos 10 eventos
            event_time = event['EventTime'].strftime('%Y-%m-%d %H:%M:%S')
            event_name = event['EventName']
            username = event.get('Username', 'N/A')
            
            print(f"⏰ {event_time}")
            print(f"🎯 Evento: {event_name}")
            print(f"👤 Usuário: {username}")
            
            if 'CloudTrailEvent' in event:
                try:
                    event_data = json.loads(event['CloudTrailEvent'])
                    source_ip = event_data.get('sourceIPAddress', 'N/A')
                    user_agent = event_data.get('userAgent', 'N/A')
                    print(f"🌐 IP: {source_ip}")
                    print(f"🖥️  User Agent: {user_agent}")
                except:
                    pass
            print("-" * 40)
    
    # Analisar mudanças em serviços
    analyze_iam_changes()
    analyze_ec2_changes()
    analyze_s3_changes()
    get_console_login_events()
    
    print("\n✅ Investigação concluída!")

if __name__ == "__main__":
    main()
