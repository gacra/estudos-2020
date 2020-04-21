import time
import pika

def callback(ch, method, properties, body):
    print(' [x] Receive %r' % body)
    time.sleep(body.count(b'.'))
    print(' [x] Done')
    # Enviar a confirmação somente após a tarefa ser completada garante que,
    # se o processo morrer antes de terminar, a tarefa volta para a fila e
    # outro worker pode pegá-la.
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)

# Fala para o broker não mandar mais tarefa para um worker se ele ainda não
# tiver finalizado a tarefa anterior (mandado um ack)
channel.basic_qos(prefetch_count=1)

channel.basic_consume(queue='task_queue', on_message_callback=callback)

print(' [*] Wainting for messages. To exit press CTRL+C')
channel.start_consuming()


