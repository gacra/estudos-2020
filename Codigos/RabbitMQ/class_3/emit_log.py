import sys
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Damos um nome qualquer ao exchange (no caso 'logs') e declaramos que ele é
# do tipo 'fanout'.
channel.exchange_declare(exchange='logs', exchange_type='fanout')

# Vamos declarar a fila apenas no consumidor, o produtor precisa saber apenas
# do exchange para o qual ele vai enviar a mensagem.

# Caso o produtor emita uma mensagem para o exchange e não haja uma fila
# relacionada a ele, a mensagem será perdida, mas não há problema nesse caso.

message = ' '.join(sys.argv[1:]) or 'info: Hello World!'

# Ao usar o 'basic_publish' temos sempre que passar um 'routing_key',
# entretanto nesse caso específico pode ser qualquer coisa, pois o exchange do
# tipo fanout o ignora.
channel.basic_publish(exchange='logs',
                      routing_key='',
                      body=message)
print(' [x] Sent %r' % message)

connection.close()
