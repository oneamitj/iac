"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws
import pulumi_tls as tls
from helper_func import generate_sub_cidrs, check_nginx

# Global values
availability_zones = aws.get_availability_zones()
name = "iac-exp-pul"

# Network components
vpc = aws.ec2.Vpc("main",
                  cidr_block="10.91.0.0/16",
                  instance_tenancy="default",
                  tags={
                      "Name": f"{name}-vpc",
                      "Creator": "AmitJ",
                      "Delete": "True",
                      "Project": "iac",
                  })

subnet_cidrs = vpc.cidr_block.apply(lambda cidr: generate_sub_cidrs(cidr, 24, 4))

private_subnets = []
for i in range(2):
    subnet_cidr = subnet_cidrs[i]
    subnet = aws.ec2.Subnet(f"{name}-pvt-sn-{i}",
                            vpc_id=vpc.id,
                            cidr_block=subnet_cidr,
                            availability_zone=availability_zones.names[i],
                            tags={
                                "Name": f"{name}-pvt-sn-{i}",
                                "Creator": "AmitJ",
                                "Delete": "True",
                                "Project": "iac",
                            })
    private_subnets.append(subnet)

public_subnets = []
for i in range(2):
    subnet_cidr = subnet_cidrs[i + 2]
    subnet = aws.ec2.Subnet(f"{name}-pub-sn-{i}",
                            vpc_id=vpc.id,
                            cidr_block=subnet_cidr,
                            availability_zone=availability_zones.names[i],
                            tags={
                                "Name": f"{name}-pub-sn-{i}",
                                "Creator": "AmitJ",
                                "Delete": "True",
                                "Project": "iac",
                            })
    public_subnets.append(subnet)

public_route_table = aws.ec2.RouteTable(f"{name}-pub-rtb",
                                        vpc_id=vpc.id,
                                        tags={
                                            "Name": f"{name}-pub-rtb",
                                            "Creator": "AmitJ",
                                            "Delete": "True",
                                            "Project": "iac",
                                        })

private_route_table = aws.ec2.RouteTable(f"{name}-pvt-rtb",
                                         vpc_id=vpc.id,
                                         tags={
                                             "Name": f"{name}-pvt-rtb",
                                             "Creator": "AmitJ",
                                             "Delete": "True",
                                             "Project": "iac",
                                         })

for i in range(2):
    aws.ec2.RouteTableAssociation(f"{name}-public_route_ass-{i}",
                                  route_table_id=public_route_table.id,
                                  subnet_id=public_subnets[i].id)
    aws.ec2.RouteTableAssociation(f"{name}-private_route_ass-{i}",
                                  route_table_id=private_route_table.id,
                                  subnet_id=private_subnets[i].id)

igw = aws.ec2.InternetGateway(f"{name}-igw",
                              vpc_id=vpc.id,
                              tags={
                                  "Name": f"{name}-igw",
                                  "Creator": "AmitJ",
                                  "Delete": "True",
                                  "Project": "iac",
                              })

internet_route = aws.ec2.Route(f"{name}-internet_route",
                               route_table_id=public_route_table.id,
                               destination_cidr_block="0.0.0.0/0",
                               gateway_id=igw.id)

nat_eip = aws.ec2.Eip(f"{name}-nat-eip",
                      domain="vpc",
                      tags={
                          "Name": f"{name}-nat-eip",
                          "Creator": "AmitJ",
                          "Delete": "True",
                          "Project": "iac",
                      })

nat_gw = aws.ec2.NatGateway(f"{name}-nat",
                            allocation_id=nat_eip.id,
                            subnet_id=public_subnets[0].id,
                            tags={
                                "Name": f"{name}-nat",
                                "Creator": "AmitJ",
                                "Delete": "True",
                                "Project": "iac",
                            })

nat_route = aws.ec2.Route(f"{name}-nat_route",
                          route_table_id=private_route_table.id,
                          destination_cidr_block="0.0.0.0/0",
                          nat_gateway_id=nat_gw.id)

# EC2 with nginx
private_key = tls.PrivateKey("private_key",
                             algorithm="RSA",
                             rsa_bits=4096)

ec2_key_pair = aws.ec2.KeyPair(f"{name}-ec2",
                               key_name=f"{name}-ec2",
                               public_key=private_key.public_key_openssh,
                               tags={
                                   "Name": f"{name}-ec2",
                                   "Creator": "AmitJ",
                                   "Delete": "True",
                                   "Project": "iac",
                               })


def create_local_file(args):
    content, filename = args
    with open(filename, 'w') as file:
        file.write(content)
    return filename


filename = pulumi.Output.all(ec2_key_pair.key_name).apply(lambda args: f"{args[0]}.pem")
# resulting_filename = pulumi.Output.all(private_key.private_key_pem, filename).apply(create_local_file)

sg = aws.ec2.SecurityGroup(f"{name}-allow-http",
                           name=f"{name}-allow-http",
                           description="Allow HTTP & SSH inbound traffic",
                           vpc_id=vpc.id,
                           ingress=[
                               aws.ec2.SecurityGroupIngressArgs(
                                   description="HTTP from Public",
                                   from_port=80,
                                   to_port=80,
                                   protocol="tcp",
                                   cidr_blocks=["0.0.0.0/0"],
                                   ipv6_cidr_blocks=["::/0"]
                               ),
                               aws.ec2.SecurityGroupIngressArgs(
                                   description="SSH from Public",
                                   from_port=22,
                                   to_port=22,
                                   protocol="tcp",
                                   cidr_blocks=["0.0.0.0/0"],
                                   ipv6_cidr_blocks=["::/0"]
                               )
                           ],
                           egress=[
                               aws.ec2.SecurityGroupEgressArgs(
                                   from_port=0,
                                   to_port=0,
                                   protocol="-1",
                                   cidr_blocks=["0.0.0.0/0"],
                                   ipv6_cidr_blocks=["::/0"]
                               )
                           ],
                           tags={
                               "Name": f"{name}-allow-http",
                               "Creator": "AmitJ",
                               "Delete": "True",
                               "Project": "iac",
                           }
                           )

nginx_instance = aws.ec2.Instance(f"{name}-nginx",
                                  ami="ami-0f5ee92e2d63afc18",
                                  instance_type="t3.small",
                                  subnet_id=public_subnets[0].id,
                                  associate_public_ip_address=True,
                                  vpc_security_group_ids=[sg.id],
                                  key_name=ec2_key_pair.key_name,
                                  tags={
                                      "Name": f"{name}-nginx",
                                      "Creator": "AmitJ",
                                      "Delete": "True",
                                      "Project": "iac",
                                  },
                                  volume_tags={
                                      "Name": f"{name}-nginx",
                                      "Creator": "AmitJ",
                                      "Delete": "True",
                                      "Project": "iac",
                                  },
                                  user_data="""#!/bin/bash
                            sudo apt update
                            sudo apt install -y nginx
                            echo "<div style='background: #f26e7e; font-size: 40 ; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);'><p><strong>Pulumi</strong> is GOOOOOOOOD!</p></div>" | sudo tee /var/www/html/index.html
                            sudo systemctl enable nginx
                            sudo systemctl start nginx
                            """
                                  )

nginx_endpoint = nginx_instance.public_ip.apply(lambda ip: ip)
pulumi.Output.all(nginx_endpoint).apply(lambda args: check_nginx(*args))

pulumi.export('nginx-endpoint', pulumi.Output.concat('http://', nginx_instance.public_ip))
