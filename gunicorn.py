import os
import multiprocessing

listen_ip = os.getenv('LISTEN_IP', '0.0.0.0')
listen_port = os.getenv('LISTEN_PORT', 5000)

# GUnicorn configuration
bind = "{}:{}".format(listen_ip, listen_port)
workers = multiprocessing.cpu_count() * 2 + 1
preload_app = True
accesslog = '-'
