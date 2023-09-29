resource "aws_security_group" "allow_http" {
  name        = "${local.name}-allow-http"
  description = "Allow HTTP & SSH inbound traffic"
  vpc_id      = aws_vpc.main.id

  ingress {
    description      = "HTTP from Public"
    from_port        = 80
    to_port          = 80
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    description      = "SSH from Public"
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = {
    Name    = "${local.name}-allow-http"
    Creator = "AmitJ"
    Delete  = "True"
    Project = "iac"
  }
}

resource "aws_instance" "nginx" {
  ami                         = "ami-0f5ee92e2d63afc18"
  instance_type               = "t3.small"
  subnet_id                   = aws_subnet.public_subnet[0].id
  associate_public_ip_address = true

  security_groups = [aws_security_group.allow_http.id]
  key_name        = aws_key_pair.ec2_key_pair.key_name

  tags = {
    Name    = "${local.name}-nginx"
    Creator = "AmitJ"
    Delete  = "True"
    Project = "iac"
  }

  volume_tags = {
    Name    = "${local.name}-nginx"
    Creator = "AmitJ"
    Delete  = "True"
    Project = "iac"
  }

  user_data = <<EOF
#!/bin/bash
sudo apt update
sudo apt install -y nginx
echo "<div style='background: #ffda18; font-size: 40 ; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);'><p><strong>OpenTofu</strong> is same as, you know who!</p></div>" | sudo tee /var/www/html/index.html
sudo systemctl enable nginx
sudo systemctl start nginx
EOF

}

resource "null_resource" "check_instance_reachable" {
  triggers = {
    instance_ip = aws_instance.nginx.public_ip
  }

  provisioner "local-exec" {
    command = <<-EOL
      until curl -s ${aws_instance.nginx.public_ip}; do
        echo "Waiting for NGINX to be reachable"
        sleep 10
      done
    EOL
  }

  depends_on = [aws_instance.nginx]
}
