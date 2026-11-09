data "aws_availability_zones" "available" { state = "available" }
resource "aws_vpc" "main" { cidr_block="10.40.0.0/16" enable_dns_hostnames=true tags={Name=var.project_name} }
resource "aws_internet_gateway" "gw" { vpc_id=aws_vpc.main.id }
resource "aws_subnet" "public" {
  count=2; vpc_id=aws_vpc.main.id; cidr_block="10.40.${count.index+1}.0/24"
  availability_zone=data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch=true
}
resource "aws_subnet" "private" {
  count=2; vpc_id=aws_vpc.main.id; cidr_block="10.40.${count.index+11}.0/24"
  availability_zone=data.aws_availability_zones.available.names[count.index]
}
resource "aws_route_table" "public" { vpc_id=aws_vpc.main.id }
resource "aws_route" "internet" { route_table_id=aws_route_table.public.id destination_cidr_block="0.0.0.0/0" gateway_id=aws_internet_gateway.gw.id }
resource "aws_route_table_association" "public" { count=2; subnet_id=aws_subnet.public[count.index].id; route_table_id=aws_route_table.public.id }
resource "aws_security_group" "alb" { name="${var.project_name}-alb"; vpc_id=aws_vpc.main.id
  ingress { from_port=80 to_port=80 protocol="tcp" cidr_blocks=["0.0.0.0/0"] }
  egress { from_port=0 to_port=0 protocol="-1" cidr_blocks=["0.0.0.0/0"] }
}
resource "aws_security_group" "api" { name="${var.project_name}-api"; vpc_id=aws_vpc.main.id
  ingress { from_port=8000 to_port=8000 protocol="tcp" security_groups=[aws_security_group.alb.id] }
  egress { from_port=0 to_port=0 protocol="-1" cidr_blocks=["0.0.0.0/0"] }
}
resource "aws_lb" "app" { name=substr(var.project_name,0,25); load_balancer_type="application"; subnets=aws_subnet.public[*].id; security_groups=[aws_security_group.alb.id] }
resource "aws_lb_target_group" "api" { name="${var.project_name}-tg"; port=8000; protocol="HTTP"; vpc_id=aws_vpc.main.id; target_type="ip"
  health_check { path="/api/health"; matcher="200" }
}
resource "aws_lb_listener" "http" { load_balancer_arn=aws_lb.app.arn; port=80; protocol="HTTP"
  default_action { type="forward"; target_group_arn=aws_lb_target_group.api.arn }
}
resource "aws_ecs_cluster" "main" { name=var.project_name }
resource "aws_iam_role" "ecs_task_execution" { name="${var.project_name}-execution"; assume_role_policy=jsonencode({Version="2012-10-17",Statement=[{Action="sts:AssumeRole",Effect="Allow",Principal={Service="ecs-tasks.amazonaws.com"}}]}) }
resource "aws_iam_role_policy_attachment" "execution" { role=aws_iam_role.ecs_task_execution.name; policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy" }
resource "aws_ecs_task_definition" "api" { family=var.project_name; requires_compatibilities=["FARGATE"]; network_mode="awsvpc"; cpu="512"; memory="1024"; execution_role_arn=aws_iam_role.ecs_task_execution.arn
  container_definitions=jsonencode([{name="api",image=var.container_image,essential=true,portMappings=[{containerPort=8000,hostPort=8000}],environment=[{name="DATABASE_URL",value="REPLACE_WITH_SECRETS_MANAGER_OR_RDS_URL"}],healthCheck={command=["CMD-SHELL","python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')\""],interval=30,timeout=5,retries=3}}])
}
resource "aws_ecs_service" "api" { name=var.project_name; cluster=aws_ecs_cluster.main.id; task_definition=aws_ecs_task_definition.api.arn; desired_count=1; launch_type="FARGATE"
  network_configuration { subnets=aws_subnet.public[*].id; security_groups=[aws_security_group.api.id]; assign_public_ip=true }
  load_balancer { target_group_arn=aws_lb_target_group.api.arn; container_name="api"; container_port=8000 }
  depends_on=[aws_lb_listener.http]
}
output "application_url" { value="http://${aws_lb.app.dns_name}" }
