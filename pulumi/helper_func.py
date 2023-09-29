import time
import requests
import pulumi
from ipaddress import ip_network


def generate_sub_cidrs(main_cidr: str, new_prefix: int, count: int):
    subnets = list(ip_network(main_cidr).subnets(new_prefix=new_prefix))
    return [str(subnet) for subnet in subnets[:count]]


def check_nginx(ip: str):
    while True:
        try:
            response = requests.get(f"http://{ip}", timeout=3)
            response.raise_for_status()
            break
        except requests.RequestException:
            print("Waiting for NGINX to be reachable...")
            time.sleep(10)
