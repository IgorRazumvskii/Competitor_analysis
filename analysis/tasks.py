from celery import shared_task
from .parsec import Parser
import time

@shared_task
def hello():
    parser = Parser()
    #TODO! Добавить сюда JSON
    print(parser.parseValta("70085281"))