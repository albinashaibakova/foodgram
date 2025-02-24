from recipes.management.commands.migrate_from_json import BaseImportCommand

from recipes.models import Tag


class Command(BaseImportCommand):
    """Команда для заполнения БД тэгами из файла формата JSON"""

    def handle(self, model=None, **kwargs):
        super().handle(model=Tag, **kwargs)
