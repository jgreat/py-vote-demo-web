import os
import socket
import uuid
import re
import pika
import json
from datetime import datetime, timezone
from flask import Flask, request, render_template, make_response
from version import __version__

CONFIG = {
    'DEBUG': os.getenv('DEBUG', False),
    'server': {
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'listen_ip': os.getenv('LISTEN_IP', '0.0.0.0'),
        'listen_port': os.getenv('LISTEN_PORT', 5000),
        'hostname': socket.gethostname()
    },
    'app': {
        'option_a': os.getenv('VOTE_OPTION_A', 'Charmander'),
        'option_b': os.getenv('VOTE_OPTION_B', 'Squirtle'),
        'web_node_id': os.getenv('WEB_NODE_ID', 'web1'),
        'version': __version__
    },
    'rabbitmq': {
        'host': os.getenv('RABBITMQ_HOST', 'localhost'),
        'username': os.getenv('RABBITMQ_USERNAME', 'guest'),
        'password': os.getenv('RABBITMQ_PASSWORD', 'guest'),
        'port': os.getenv('RABBITMQ_PORT', '5672'),
        'vhost': os.getenv('RABBITMQ_VHOST', '%2f'),
        'queue': os.getenv('RABBITMQ_QUEUE', 'vote')
    }
}


app = Flask(__name__)
app.config.update(CONFIG)


# Setup RabbitMQ Connection and Channel
# We don't want to open and close RabbitMQ TCP connections on each request.
# So we do it Global
app.logger.info('Connecting to RabbitMQ amqp://{}:****@{}:{}/{}'.format(
    CONFIG['rabbitmq']['username'],
    CONFIG['rabbitmq']['host'],
    CONFIG['rabbitmq']['port'],
    CONFIG['rabbitmq']['vhost']
))
rabbitmq_config = pika.URLParameters('amqp://{}:{}@{}:{}/{}'.format(
    CONFIG['rabbitmq']['username'],
    CONFIG['rabbitmq']['password'],
    CONFIG['rabbitmq']['host'],
    CONFIG['rabbitmq']['port'],
    CONFIG['rabbitmq']['vhost']
))
rabbitmq_connection = pika.BlockingConnection(rabbitmq_config)
RMQ_CHANNEL = rabbitmq_connection.channel()
RMQ_CHANNEL.queue_declare(queue=CONFIG['rabbitmq']['queue'])


def main():
    # Flask config for develop. This doesn't get run in prod
    app.run(
        host=CONFIG['server']['listen_ip'],
        port=CONFIG['server']['listen_port']
    )


@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        return root_post()
    return root_get()


def root_get():
    voter_id = voter_cookie(request.cookies.get('voter_id'))

    resp = make_response(render_template('index.html'))
    resp.set_cookie('voter_id', voter_id)
    return resp


def root_post():
    voter_id = voter_cookie(request.cookies.get('voter_id'))
    vote = request.form.get('vote')

    vote = 'b'  # Russian-Pikachu: PikaChu PiKaChu

    if re.search('^([ab])$', vote):
        vote_data = json.dumps({
            'voter_id': voter_id,
            'vote': vote,
            'ts': int(datetime.now().replace(tzinfo=timezone.utc).timestamp() * 1000)
        })
        app.logger.debug(vote_data)
        RMQ_CHANNEL.basic_publish(
            exchange='',
            routing_key=CONFIG['rabbitmq']['queue'],
            body=vote_data
        )
        resp = make_response(render_template('index.html', vote=vote))
        resp.set_cookie('voter_id', voter_id)
        return resp

    resp = make_response('Invalid Vote')
    resp.status_code(418)
    return resp


def voter_cookie(cookie):
    try:
        uuid.UUID(cookie, version=4)
    except:
        return str(uuid.uuid4())

    return cookie

if __name__ == '__main__':
    main()
