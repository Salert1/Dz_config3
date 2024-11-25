import unittest
from io import StringIO
from unittest.mock import patch
from main import parse_toml, transform_to_custom_format, evaluate_expression

class TestConfigTranslator(unittest.TestCase):

    def test_parse_toml_valid(self):
        """Проверка корректного парсинга TOML"""
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
        """Проверка ошибки синтаксиса TOML"""
        toml_data = """
        [server
        host = "localhost"
        port = 8080
        """
        with self.assertRaises(SyntaxError):
            parse_toml(toml_data)

    def test_transform_simple(self):
        """Тест базового преобразования"""
        parsed_data = {
            "var_name": "100",
            "array": [1, 2, 3],
            "struct": {"key": "value"}
        }
        expected = (
            "var_name = 100\n"
            "array [1; 2; 3]\n"
            "struct struct {\n"
            "  key = value,\n"
            "}"
        )
        result = transform_to_custom_format(parsed_data)
        self.assertEqual(result, expected)

    def test_transform_with_constants(self):
        """Тест объявления и использования констант"""
        parsed_data = {
            "var": "var base_value 100",
            "calc": "$base_value + 50$"
        }
        expected = (
            "var base_value 100\n"
            "calc = 150"
        )
        result = transform_to_custom_format(parsed_data)
        self.assertEqual(result, expected)

    def test_evaluate_expression_valid(self):
        """Тест корректного вычисления выражений"""
        constants = {"base_value": 100}
        expression = "$base_value + 50$"
        result = evaluate_expression(expression.strip("$"), constants)
        self.assertEqual(result, 150)

    def test_evaluate_expression_invalid(self):
        """Тест ошибки в вычислении выражения"""
        constants = {"base_value": 100}
        expression = "$base_value / 0$"  # Деление на ноль
        with self.assertRaises(ValueError):
            evaluate_expression(expression.strip("$"), constants)

    def test_transform_with_comments(self):
        """Тест обработки комментариев"""
        parsed_data = {
            "server": {
                "host": "localhost",
                "port": 8080
            },
            "#comment": "# This is a comment"
        }
        expected = (
            "server struct {\n"
            "  host = localhost,\n"
            "  port = 8080,\n"
            "}\n"
            "\\ This is a comment"
        )
        result = transform_to_custom_format(parsed_data)
        self.assertEqual(result, expected)

    @patch("sys.stdin", StringIO("""
    # Конфигурация
    [server]
    host = "localhost"
    port = 8080

    var max_clients 100
    calc_result = $max_clients * 2$
    """))
    @patch("sys.stdout", new_callable=StringIO)
    def test_full_program(self, mock_stdout):
        """Интеграционный тест программы"""
        from main import main
        main()
        output = mock_stdout.getvalue().strip()
        expected = (
            "\\ Конфигурация\n"
            "server struct {\n"
            "  host = localhost,\n"
            "  port = 8080,\n"
            "}\n"
            "var max_clients 100\n"
            "calc_result = 200"
        )
        self.assertEqual(output, expected)

if __name__ == "__main__":
    unittest.main()
