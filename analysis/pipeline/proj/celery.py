from celery import Celery

from proj import RABBITMQ_USER, RABBITMQ_HOST, RABBITMQ_PORT, REDIS_HOST, REDIS_PORT

app = Celery("proj", 
             broker="pyamqp://{}@{}:{}//".format(RABBITMQ_USER, RABBITMQ_HOST, RABBITMQ_PORT), 
             backend="redis://{}:{}".format(REDIS_HOST, REDIS_PORT),
             include=["proj.tasks"]
            )

if __name__ == '__main__':
    app.start()
