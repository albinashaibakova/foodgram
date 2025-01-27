from recipes.management.commands.base_migrate_from_json import BaseImportCommand

from recipes.models import Tag


class Command(BaseImportCommand):
    """Команда для заполнения БД тэгами из файла формата JSON"""

    def import_data(self, data):

        try:
            Tag.objects.bulk_create(Tag(**tag) for tag in data)
            print('Тэги успешно загружены')

        except Exception as e:
            print(f'Error: {e}')
