import toml
import re


def parse_toml(input_text):
    """
    Парсинг TOML текста и преобразование в структуру данных Python.
    """
    try:
        return toml.loads(input_text)
    except toml.TomlDecodeError as e:
        raise SyntaxError(f"Ошибка синтаксиса: {e}")


def evaluate_expression(expression, constants):
    """
    Вычисление константного выражения. Использует словарь `constants` для замены значений.
    """
    # Заменяем константы в выражении на их значения
    for name, value in constants.items():
        expression = expression.replace(f"${name}$", str(value))

    # Разрешаем только определённые безопасные функции и операции
    allowed_names = {
        "max": max,
        "abs": abs
    }
    allowed_operators = "+-*/()"
    allowed_characters = "0123456789. " + allowed_operators + "".join(constants.keys())

    # Проверяем, чтобы в выражении были только разрешённые символы
    if not all(char in allowed_characters for char in expression):
        raise ValueError(f"Ошибка: запрещённые символы в выражении '{expression}'")

    # Вычисляем выражение
    try:
        result = eval(expression, {"__builtins__": None}, allowed_names)
        return result
    except Exception as e:
        raise ValueError(f"Ошибка вычисления выражения '{expression}': {e}")


def transform_to_custom_format(parsed_data):
    """
    Преобразование разобранных данных TOML в формат учебного конфигурационного языка.
    """
    output = []
    constants = {}  # Словарь для хранения констант

    for key, value in parsed_data.items():
        # Обработка однострочных комментариев
        if isinstance(value, str) and value.startswith("#"):
            output.append(f"\\ {value[1:].strip()}")

        # Обработка словарей
        elif isinstance(value, dict):
            output.append(f"{key} struct {{")
            for sub_key, sub_value in value.items():
                output.append(f"  {sub_key} = {sub_value},")
            output.append("}")

        # Обработка массивов
        elif isinstance(value, list):
            output.append(f"{key} [{'; '.join(map(str, value))}]")

        # Обработка объявления констант
        elif isinstance(value, str) and value.startswith("var "):
            _, const_name, const_value = value.split()
            constants[const_name] = eval(const_value)
            output.append(f"var {const_name} {constants[const_name]}")

        # Обработка выражений
        elif isinstance(value, str) and re.match(r"^\$.*\$$", value):
            expression = value.strip("$")
            result = evaluate_expression(expression, constants)
            output.append(f"{key} = {result}")

        # Преобразование простых значений
        elif isinstance(value, (int, float, str)):
            output.append(f"{key} = {value}")

    return "\n".join(output)


def process_input(input_text):
    """
    Основная функция для чтения входного текста и преобразования его в выходной формат.
    """
    # Парсим входной TOML текст
    parsed_data = parse_toml(input_text)

    # Преобразуем в учебный формат
    output_text = transform_to_custom_format(parsed_data)
    return output_text


def main():
    """
    Главная функция для работы программы.
    Принимает данные через стандартный ввод и выводит результат на стандартный вывод.
    """
    # Чтение всего ввода
    input_text = input()  # Ввод TOML текста
    result = process_input(input_text)
    print(result)


if __name__ == "__main__":
    main()
