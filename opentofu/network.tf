resource "aws_vpc" "main" {
  cidr_block       = "10.92.0.0/16"
  instance_tenancy = "default"

  tags = {
    Name    = "${local.name}-vpc"
    Creator = "AmitJ"
    Delete  = "True"
    Project = "iac"
  }
}

resource "aws_subnet" "private_subnet" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  availability_zone = data.aws_availability_zones.default.names[count.index]

  tags = {
    Name    = "${local.name}-pvt-sn-${count.index}"
    Creator = "AmitJ"
    Delete  = "True"
    Project = "iac"
  }
}

resource "aws_subnet" "public_subnet" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index + 3)
  availability_zone = data.aws_availability_zones.default.names[count.index]

  tags = {
    Name    = "${local.name}-pub-sn-${count.index}"
    Creator = "AmitJ"
    Delete  = "True"
    Project = "iac"
  }
}

resource "aws_route_table" "public_route" {
  vpc_id = aws_vpc.main.id

  depends_on = [aws_subnet.public_subnet]

  tags = {
    Name    = "${local.name}-pub-rtb"
    Creator = "AmitJ"
    Delete  = "True"
    Project = "iac"
  }
}

resource "aws_route_table" "private_route" {
  vpc_id = aws_vpc.main.id

  depends_on = [aws_subnet.private_subnet]

  tags = {
    Name    = "${local.name}-pvt-rtb"
    Creator = "AmitJ"
    Delete  = "True"
    Project = "iac"
  }
}

resource "aws_route_table_association" "public_route_ass" {
  route_table_id = aws_route_table.public_route.id
  count          = 2
  subnet_id      = element(aws_subnet.public_subnet.*.id, count.index)
}

resource "aws_route_table_association" "private_route_ass" {
  route_table_id = aws_route_table.private_route.id
  count          = 2
  subnet_id      = element(aws_subnet.private_subnet.*.id, count.index)
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name    = "${local.name}-igw"
    Creator = "AmitJ"
    Delete  = "True"
    Project = "iac"
  }
}

resource "aws_route" "internet_route" {
  route_table_id         = aws_route_table.public_route.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw.id
}

resource "aws_eip" "nat_eip" {
  domain     = "vpc"
  depends_on = [aws_internet_gateway.igw]

  tags = {
    Name    = "${local.name}-nat-eip"
    Creator = "AmitJ"
    Delete  = "True"
    Project = "iac"
  }
}

resource "aws_nat_gateway" "nat_gw" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.public_subnet[0].id

  tags = {
    Name    = "${local.name}-nat"
    Creator = "AmitJ"
    Delete  = "True"
    Project = "iac"
  }
}

resource "aws_route" "nat_route" {
  route_table_id         = aws_route_table.private_route.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.nat_gw.id
}
