import sys
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# O parâmetro "durable" faz com que a fila seja gravada no disco da
# máquina do broker, assim, mesmo que o processo morra, ela não vai ser
# perdida.
channel.queue_declare(queue='task_queue', durable=True)

message = ' '.join(sys.argv[1:]) or 'Hello World!'

# O parâmetro "properties/delivery_mode" faz com que a mensagem seja gravada
# no disco da máquina do broker, assim, mesmo que o processo morra, ela não
# vai ser perdida.
channel.basic_publish(exchange='',
                      routing_key='task_queue',
                      body=message,
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
print(' [x] Sent %r' % message)

connection.close()
