output "nginx-endpoint" {
  value = "http://${aws_instance.nginx.public_ip}"
}
