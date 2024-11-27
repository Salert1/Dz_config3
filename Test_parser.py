import unittest
from io import StringIO
import toml
from unittest.mock import patch
from studylang import parse_toml, transform_to_custom_format, evaluate_expression, main

class TestConfigTranslator(unittest.TestCase):

    def test_parse_toml_valid(self):
        """Проверяет корректный парсинг TOML"""
        toml_data = """
        [server]
        host = "localhost"
        port = 8080
        """
        expected = {
            "server": {
                "host": "localhost",
                "port": 8080
            }
        }
        result = parse_toml(toml_data)
        self.assertEqual(result, expected)

    def test_parse_toml_invalid(self):
        """Проверяет синтаксические ошибки TOML"""
        toml_data = """
        [server
        host = "localhost"
        port = 8080
        """
        with self.assertRaises(SyntaxError):
            parse_toml(toml_data)

    import toml

    def test_transform_to_custom_format(self):
        """Проверяет преобразование данных в кастомный формат из TOML"""
        toml_data = """
        [server]
        host = "localhost"
        port = 8080

        [var]
        max_clients = 100

        calc = "$max_clients * 2$"
        """

        # Преобразуем TOML-данные в словарь
        parsed_data = toml.loads(toml_data)
        constants = {"max_clients": 100}
        expected = (
            "server struct {\n"
            "  host = localhost,\n"
            "  port = 8080,\n"
            "}\n"
            "var struct {\n"
            "  max_clients = 100,\n"
            "  calc = $max_clients * 2$,\n"
            "}"


        )
        result = transform_to_custom_format(parsed_data)
        self.assertEqual(result.strip(), expected)

    def test_evaluate_expression_valid(self):
        """Проверяет корректное вычисление выражения"""
        constants = {"max_clients": 100}
        expression = "$max_clients * 2$"
        print(expression.strip("$"))
        result = evaluate_expression(expression.strip("$"), constants)

        self.assertEqual(result, 200)

    def test_evaluate_expression_with_function(self):
        """Проверяет вычисление выражений с функциями"""
        constants = {"value": -50}
        expression = "$abs(value)$"
        result = evaluate_expression(expression.strip("$"), constants)
        self.assertEqual(result, 50)


if __name__ == "__main__":
    unittest.main()


