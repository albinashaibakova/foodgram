from recipes.management.commands.base_migrate_from_json import Command

from recipes.models import Tag


class CommandIngredients(Command):
    """Команда для заполнения БД тэгами из файла формата JSON"""

    pass
