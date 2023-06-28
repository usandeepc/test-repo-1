import csv
import paramiko
import boto3

def fetch_ec2_instances():
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_instances()
    
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            if 'PrivateIpAddress' in instance:
                platform = instance['Platform'] if 'Platform' in instance else 'Unknown'
                instances.append({
                    'InstanceID': instance['InstanceId'],
                    'PrivateIP': instance['PrivateIpAddress'],
                    'Platform': platform
                })
    
    return instances

def get_os_details(instance_ip, key_path):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    ssh_key = paramiko.RSAKey.from_private_key_file(key_path)
    ssh_client.connect(instance_ip, username='ec2-user', pkey=ssh_key)
    
    stdin, stdout, stderr = ssh_client.exec_command('cat /etc/os-release')
    
    os_details = stdout.read().decode('utf-8').strip()
    
    ssh_client.close()
    
    return os_details

def create_csv_file(instances):
    with open('instance_details.csv', 'w', newline='') as csvfile:
        fieldnames = ['InstanceID', 'PrivateIP', 'Details']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for instance in instances:
            if instance['Platform'] == 'linux':
                os_details = get_os_details(instance['PrivateIP'], ssh_key_path)
                writer.writerow({
                    'InstanceID': instance['InstanceID'],
                    'PrivateIP': instance['PrivateIP'],
                    'Details': os_details
                })
            else:
                writer.writerow({
                    'InstanceID': instance['InstanceID'],
                    'PrivateIP': instance['PrivateIP'],
                    'Details': instance['Platform']
                })

# Fetch EC2 instances
ec2_instances = fetch_ec2_instances()

# Prompt user for SSH key file path
ssh_key_path = input("Enter the SSH key file path: ")

# Create CSV file
create_csv_file(ec2_instances)

print("CSV file 'instance_details.csv' created successfully.")

