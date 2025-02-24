import json

from django.core.management.base import BaseCommand
from django.db import IntegrityError


class BaseImportCommand(BaseCommand):
    """Команда для заполнения БД из файла формата JSON"""

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str,
                            help='The JSON file to import data from')

    def handle(self, model=None, **kwargs):
        json_file = kwargs['json_file']
        with open(json_file) as file:
            data = json.load(file)

        try:
            model.objects.bulk_create(
                model(**element) for element in data
            )
            print('Объекты {model} ({number}) успешно загружены'.format(
                model=model._meta.object_name,
                number=len(data)
            )
            )
        except IntegrityError:
            pass
        except Exception as e:
            print(f'Error: {e}')
