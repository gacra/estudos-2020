import pika
import sys


def callback(ch, method, properties, body):
    print(' [x] %r:%r' % (method.routing_key, body))


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# Exemplos: "kern.*", "*.critical", "#",
binding_keys = sys.argv[1:]
if not binding_keys:
    sys.stderr.write('Usage: %s [binding_key]...]\n' % sys.argv[0])
    sys.exit(1)

for binding_key in binding_keys:
    channel.queue_bind(exchange='topic_logs',
                       queue=queue_name,
                       routing_key=binding_key)

print(' [*] Wainting for logs. To exit press CTRL+C')

channel.basic_consume(queue=queue_name,
                      on_message_callback=callback,
                      auto_ack=True)

channel.start_consuming()
