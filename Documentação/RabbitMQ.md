# RabbitMQ

## Conceitos

### Message Broker

O RabbitMQ é um "Message Broker" (Intermediário de mensagens). Semelhante à um 
serviço de Correios, o Rabbit aceita, armazena e encaminha blobs binário de 
dados (chamados de mensagens).

### Termos importantes:

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

Para deixar o modelo anterior mais condizente com a realidade, temos que 
introduzir mais um termo importante:

- **Exchanges (trocas):** De um lado ele recebe mensagens de produtores, de 
outro ele coloca a mensagem em filas. O exchange pode escolher colocar a 
mensagem em uma fila específica, em várias filas ou descartá-la. Existem 
diversos tipos de exchages:
    - fanout: envia as mensagens que recebe para todas as filas que conhece
    (broadcast).
    
    ```
             |-> Fila1 --> C1
    P--> X --|
             |-> Fila2 --> C2
    ```
    - direct: envia uma mensagem para uma fila se a `routing key` do binding 
    da fila com o exchange for igual ao `routing key` com o qual a mensagem 
    foi publicada. 
    ```
                 vermelho
              |----------> fila1 --> C1
    P --> X --|
              |    azul
              |----------> fila2 --> C2
              |              ^
              |  vermelho    |
              |-------------- 
    ```
    - Topic: Semelhante ao caso anterior, entretanto possui uma maior 
    complexidade. A `routing_key` precisa ser uma lista de termos separados 
    por ponto (ex.: `quick.orange.rabbit`). Os termos costumam ser 
    características atreladas às mensagens. Diferente do "direct", a chave do 
    binding não precisa ser exatamente igual à publicada. Aqui podemos usar 2 
    símbolos especiais para criar regras mais complexas.
        - `*`: pode substituir extamente um termo.
        - `#`: pode substituir zero ou mais termos.
    
        **Obs1:** Mensagens que casam com mais de um binding da mesma fila não 
        são enviadas mais de uma vez para tal fila (ex: `lazy.pink.rabbit` 
        para o caso abaixo).
        
        **Obs2:** Não há problema que as mensagens tenham um número de termos 
        variáveis. Inclusive se usarmos `#` em uma chave a fila irá pegar 
        chaves de vários tamanhos.
    ```
               *.orange.*
              |----------> fila1 --> C1
    P --> X --|
              |*.*.rabbit
              |----------> fila2 --> C2
              |              ^
              |    lazy.#    |
              |-------------- 
    ```
  

### Casos de uso

- **Work queues (Filas de tarefas):** 

    Usadas para evitar a realização imediata de tarefas itensas/demoradas, 
    tendo que ficar esperando sua resposta. A ideia é agendar a tarefa para 
    ser feita depois. O produtor solicita uma tarefa (descrita na mensagem) e 
    a coloca na fila. Um processo executor ("worker"), quando disponível, 
    pega a tarefa e a executa. Se houver multiplos workers, as tarefas serão 
    compartilhadas entre eles. 
    
    Nessa abordagem, no geral, queremos ter certeza que exatamente um worker 
    receba e execute a tarefa, nem mais, nem menos.
    
    Isso é especialmente útil para aplicações web, quando é impossível tratar 
    uma tarefa complexa durante a curta janela de tempo da requisição HTTP. 
    Exemplos de tarefas incluem: redimencionamento de imagens; renderização de 
    PDFs.
    
- **Publish/Subscribe:**
    
    Uma mensagem é enviada para múltiplos consumidores (em oposição ao caso 
    anterior em que uma tarefa é recebida e executada por apenas um worker).
    
    Como exemplo, podemos citar um sistema de logging. Um processo emite um 
    log, e vários consumidores recebem esse log, cada um deles fazendo algo 
    com ela (salvar em disco, imprimir na tela, etc). 
    
- **Remote procedure call (RPC - Chamada de Procedimento Remoto):**

    Usado quando precisamos rodar uma função em um computador remoto e 
    aguardar o resultado. Apesar do RPC ser um padrão bem comum na computação, 
    são necessários alguns cuidados:
        
    - Deixe claro no código quais funções são remotas.
    - Trate casos de erro. Como o cliente deve reagir quando o servidor de RPC 
    não responde por muito tempo? 

## Instalação

### Usando Docker

- A documentação completa se encontra [aqui](https://registry.hub.docker.com/_/rabbitmq/)

```commandline
docker pull rabbitmq
docker run -it --hostname my-rabbit --name some-rabbit -v /some-folder/in/your-computer:/var/lib/rabbitmq -p 5672:5672 rabbitmq
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
rabbitmqctl list_queues
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

- Para saber quantas mensagens estão "prontas" (aguardando um consumidor 
recebê-las) e quantas foram recebidas, mas não confirmadas, usar o comando na 
máquina rodando o broker:

```commandline
rabbitmqctl list_queues name messages_ready messages_unacknowledged
```

- Para garantir a persistência das mensagens no disco da máquina do broker, é 
necessário criar o volume ao rodar o container.

**Solicitante de tarefa (new_task.py)**

```python
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
```

**Trabalhador (worker.py)**

```python
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
```

### Aula 3 (Publish/Subscribe)

- Para listar os exchanges no servidor broker use o comando abaixo. O exchange 
padrão (sem nome) e os com nome `amq*` são criados por padrão. Nas aulas 
anteriores usamos o exchange padrão (`''`), que encaminha a mensagem para a 
fila com o nome dado por `routing_key`, caso ela exista.

```commandline
rabbitmqctl list_exchanges
```

- Para listar ligações entre exchanges e fila:

```commandline
rabbitmqctl list_bindings
```

**emit_log.py**
```python
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
```

**receive_logs.py**
```python
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
```

### Aula 4 (Routing)

**emit_log_direct.py**
```python
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
```

**receive_logs_direct.py**
```python
import pika
import sys


def callback(ch, method, properties, body):
    print(' [x] %r:%r' % (method.routing_key, body))


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

severities = sys.argv[1:]
if not severities:
    sys.stderr.write('Usage: %s [info] [warning] [error]\n' % sys.argv[0])
    sys.exit(1)

for severity in severities:
    channel.queue_bind(exchange='direct_logs',
                       queue=queue_name,
                       routing_key=severity)

print(' [*] Wainting for logs. To exit press CTRL+C')

channel.basic_consume(queue=queue_name,
                      on_message_callback=callback,
                      auto_ack=True)

channel.start_consuming()
```

### Aula 5 (Topics)

**emit_log_topic.py**

```python
import sys
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

routing_key = sys.argv[1] if len(sys.argv) > 2 else 'anonymous.info'
message = ' '.join(sys.argv[2:]) or 'Hello World!'

channel.basic_publish(exchange='topic_logs',
                      routing_key=routing_key,
                      body=message)
print(' [x] Sent %r:%r' % (routing_key, message))

connection.close()
```

**receive_logs_topic.py**

```python
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
```

### Aula 6 (RPC)

- Propriedades de mensagens enviadas comumente usadas:
    - `delivery_mode`: Se `2` a pensagem é persistente, caso contrário não é.
    - `content_type`: Descreve a codificação da mensagem. Por exemplo, se a 
    mensagem está em JSON, é uma boa colocar essa propriedade como 
    `application/json`.
    - `reply_to`: Para indicar a fila de resposta.
    - `correlation_id`: Usado para corelacionar respostas e requisições RPC.
    
- Funcionamento do RPC implementado:
    - Quando um cliente inicia, ele cria uma fila exclusiva e anônima para 
    respostas.
    - Para cada requisição RPC o cliente envia uma mensagem com duas 
    propriedades: `reply_to` com a fila de resposta e `correlation_id` com um 
    valor único para cada requisição.
    - A requisição é enviada para uma fila chamada `rpc_queue`.
    - O servidor RPC fica aguardando por requisições da fila. Quando uma 
    aparece, ele faz o trabalho e envia uma mensagem com a resposta de volta 
    ao cliente usando a fila do campo `reply_to`.
    - O cliente espera pelo dado na fila de resposta. Quando a mensagem 
    parece, ele checa pelap propriedade `correlation_id`. Se ela é igual ao 
    valor da requisição, ele retorna a resposta para a aplicação.

**rpc_server.py**
```python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='rpc_queue')

def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


def on_request(ch, method, props, body):
    n = int(body)

    print(' [.] fib(%s)' % n)
    response = fib(n)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(
                         correlation_id=props.correlation_id
                     ),
                     body=str(response)
                     )

    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

print(' [x] Awaiting RPC requests')
channel.start_consuming()
```

**rpc_client.py**

```python
import pika
import uuid

class FibonacciRpcClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(queue=self.callback_queue,
                                   on_message_callback=self.on_response,
                                   auto_ack=True)

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id
            ),
            body=str(n)
        )

        while self.response is None:
            self.connection.process_data_events()
        return int(self.response)

fibonacci_rpc = FibonacciRpcClient()

n = 2

print(f' [x] Requesting fib({n})')
response = fibonacci_rpc.call(n)
print(' [.] Got %r' % response)
```