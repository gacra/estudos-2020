# RabbitMQ

## Conceitos

### Message Broker

O RabbitMQ é um "Message Broker" (Intermediário de mensagens). Semelhante à um 
serviço de Correios, o Rabbit aceita, armazena e encaminha blobs binário de 
dados (chamados de mensagens).

###Termos importantes:

- **Producer (Produtor):** Programa que produz e envia mensagens.
- **Queue (Fila):** Fila que armazena as mensagens (buffer). Essa fila está 
dentro do processo do RabbitMQ e não possui limites (exceto, claro, de memória 
e armazenamento da máquina em que roda). Vários produtores e consumidores 
podem usar a mesma fila.
- **Consumer (Consumidor):** Aguarda para receber mensagens.

**Obs:** O produtor a fila e o consumidor não precisam estar na mesma máquina 
(no geral, não estão). Uma mesma aplicação pode ser produtora e consumidora ao 
mesmo tempo.

```
P --> Fila --> C  
```

###Casos de uso

- **Work queues (Filas de tarefas):** 

    Usadas para evitar a realização imediata de tarefas itensas/demoradas, 
    tendo que ficar esperando sua resposta. A ideia é agendar a tarefa para 
    ser feita depois. O produtor solicita uma tarefa (descrita na mensagem) e 
    a coloca na fila. Um processo executor ("worker"), quando disponível, 
    pega a tarefa e a executa. Se houver multiplos workers, as tarefas serão 
    compartilhadas entre eles. 
    
    Isso é especialmente útil para aplicações web, quando é impossível tratar 
    uma tarefa complexa durante a curta janela de tempo da requisição HTTP. 
    Exemplos de tarefas incluem: redimencionamento de imagens; renderização de 
    PDFs.  

## Instalação

### Usando Docker

- A documentação completa se encontra [aqui](https://registry.hub.docker.com/_/rabbitmq/)

```commandline
docker pull rabbitmq
docker run -it --hostname my-rabbit --name some-rabbit -p 5672:5672 rabbitmq
```

**Obs:** Para entrar no container rodando:

```commandline
docker exec -it some-rabbit bash
```

### Instalação no Python

```commandline
python -m pip install pika
```

## Tutorial

### Aula 1 ("Hello World!")

https://www.rabbitmq.com/tutorials/tutorial-one-python.html

- Para saber quantas mensagens estão aguardando nas filas do broker, entrar no 
container e usar:

```commandline
sudo rabbitmqctl list_queues
```

**Produtor (send.py)**
```python
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
```

**Consumidor (receive.py)**

```python
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
```

### Aula 2 (Work queues)

- Por padrão, se houver mais de um consumidor (worker, no caso) o Rabbit "faz 
uma fila" entre os workers e vai entregando a próxima mensagem sempre para o 
próximo worker. Ou seja, usa "round-robin". Isso faz com que, na média, todos, 
os workers recebam o mesmo número de tarefas. Entretando isso não leva em 
conta o tempo que o worker demorar para executar a tarefa. Caso um worker 
tenha o "azar" de pegar somente tarefas demoradas, as taregas atribuídas a ele 
podem ficar "represadas" na fila.


