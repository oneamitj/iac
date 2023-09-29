# Note
I created this just to test out simple difference between viability of [OpenTofu](https://opentofu.org/), as Terraform (HashiCorp) has moved to [BSL v1.1](https://www.hashicorp.com/blog/hashicorp-adopts-business-source-license).

Additionally, a simple experiment to explore [Pulumi](https://www.pulumi.com/).

All three IaC contains exactly same task.
1. Create an AWS VPC with 2 private and 2 public subnet.
2. Start an EC2 instance with key pair.
3. Install nginx in EC2 and edit its default page via `userdata`.
4. Wait until nginx is up and running.
5. Output http://ip-of-ec2.