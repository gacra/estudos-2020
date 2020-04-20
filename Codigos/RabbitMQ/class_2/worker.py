import time
import pika

def callback(ch, method, properties, body):
    print(' [x] Receive %r' % body)
    time.sleep(body.count(b'.'))
    print(' [x] Done')

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello')

channel.basic_consume(queue='hello',
                      auto_ack=True,
                      on_message_callback=callback)

print(' [*] Wainting for messages. To exit press CTRL+C')
channel.start_consuming()


