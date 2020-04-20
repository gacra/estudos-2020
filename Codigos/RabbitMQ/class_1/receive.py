import pika

def callback(ch, method, properties, body):
    print(' [x] Receive %r' % body)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Se a fila já foi criada, o comando não faz nada. É melhor "criar" a fila
# várias vezes (em vários processos) do que esquecer de criar.
channel.queue_declare(queue='hello')

channel.basic_consume(queue='hello',
                      auto_ack=True,
                      on_message_callback=callback)

print(' [*] Wainting for messages. To exit press CTRL+C')
channel.start_consuming()


