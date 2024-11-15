import os

class ImproperlyConfigured(Exception):
    """Вызывается, когда отсутствует переменная окружения."""
    def __init__(self, variable_name: str, *args, **kwargs):
        self.variable_name = variable_name
        self.message = f"Установите переменную окружения {variable_name}."
        super().__init__(self.message, *args, **kwargs)

def getenv(var_name: str, cast_to=str) -> str:
    """Получает переменную окружения или вызывает исключение.
    Аргументы:
        var_name: Имя переменной окружения.
        cast_to: Тип для приведения.
    Возвращает:
        Значение переменной окружения.
    Вызывает:
        ImproperlyConfigured: Если переменная окружения отсутствует.
    """
    try:
        value = os.environ[var_name]
        return cast_to(value)
    except KeyError:
        raise ImproperlyConfigured(var_name)
    except ValueError:
        raise ValueError(f"Значение {value} не может быть приведено к {cast_to}.")
