import os

rabbitmq_ip = os.getenv('RABBITMQ_IP', 'localhost')
rabbitmq_port = os.getenv('RABBITMQ_PORT', 5672)
rabbitmq_user = os.getenv('RABBITMQ_USER', 'admin')
rabbitmq_password = os.getenv('RABBITMQ_PWD', 'admin')