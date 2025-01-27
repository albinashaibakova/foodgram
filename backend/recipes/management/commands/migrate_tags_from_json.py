from recipes.management.commands.base_migrate_from_json import BaseImportCommand

from recipes.models import Tag


class Command(BaseImportCommand):
    """Команда для заполнения БД тэгами из файла формата JSON"""

    def import_data(self, data):
        for tag in data:
            Tag.objects.create(**tag)

        print('Тэги успешно загружены')
