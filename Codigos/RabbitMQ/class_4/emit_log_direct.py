import sys
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

severity = sys.argv[1] if len(sys.argv) > 1 else 'info'
message = ' '.join(sys.argv[2:]) or 'Hello World!'

# O exchange entregará a mensagem para todas as filas que fizeram bind com ele
# usando a "routing_key" especificado nesse comando.
channel.basic_publish(exchange='direct_logs',
                      routing_key=severity,
                      body=message)
print(' [x] Sent %r:%r' % (severity, message))

connection.close()
