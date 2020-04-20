import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Temos que garantir que a fila existe primeiro, se mandarmos uma mensagem
# para uma fila que não existe, ela será perdida.
channel.queue_declare(queue='hello')

# "Exchanges" são as entidades usadas para colocar mensagens na fila. Para
# usar o exchange padrão, colocamos como nome uma string vazia. Esse exchange
# padrão permite que passemos o nome da fila em que queremos colocar a
# mensagem.
channel.basic_publish(exchange='', routing_key='hello', body='Hello World!!')
print(' [x] Sent \'Hello World!!\'')

# Isso garante que as mensagens foram realmente enviadas para o Rabbit.
connection.close()
