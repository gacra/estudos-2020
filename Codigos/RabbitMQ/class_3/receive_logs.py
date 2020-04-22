import pika


def callback(ch, method, properties, body):
    print(' [x] %r' % body)


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='logs', exchange_type='fanout')

# Não há necessidade em dar um nome específico para a fila, uma vez que ela
# só será usada por um único processo. O parâmetro 'exclusive' faz com que a
# fila seja deletada quando o consumidor que a criou parar de executar.
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

print(queue_name)
channel.queue_bind(exchange='logs', queue=queue_name)

print(' [*] Wainting for logs. To exit press CTRL+C')

channel.basic_consume(queue=queue_name,
                      on_message_callback=callback,
                      auto_ack=True)

channel.start_consuming()
