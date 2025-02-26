import json

from django.core.management.base import BaseCommand


class BaseImportCommand(BaseCommand):
    """Команда для заполнения БД из файла формата JSON"""

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str,
                            help='The JSON file to import data from')

    def handle(self, model, **kwargs):
        json_file = kwargs['json_file']
        with open(json_file) as file:
            try:
                created_objects = model.objects.bulk_create(
                [model(**element) for element in json.load(file)],
                    ignore_conflicts=True
                )
                print('Объекты {model} ({number}) успешно загружены'.format(
                    model=model._meta.object_name,
                    number=len(created_objects)
                )
                )
            except Exception as e:
                print(f'Ошибка: {e}. Файл - {json_file}')
