data "aws_availability_zones" "default" {}

locals {
  name = "iac-exp-tf"
}

resource "tls_private_key" "private_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "ec2_key_pair" {
  key_name   = "${local.name}-ec2"
  public_key = tls_private_key.private_key.public_key_openssh

  tags = {
    Name    = "${local.name}-ec2"
    Creator = "AmitJ"
    Delete  = "True"
    Project = "iac"
  }
}

#resource "local_file" "pvt_key_pair" {
#  content  = tls_private_key.private_key.private_key_pem
#  filename = "${path.module}/${aws_key_pair.ec2_key_pair.key_name}.pem"
#}