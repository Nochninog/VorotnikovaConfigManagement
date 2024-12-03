import click
import os
import re
import json

name_re = re.compile(r"[a-z][a-z0-9_]*")
number_re = re.compile(r"^[+-]?\d+(\.\d+)?([eE][+-]?\d+)?$")
string_re = re.compile(r"\".*\"")
constant_usage_re = re.compile(r"\^\[[a-z][a-z0-9_]*]")


def get_dict_from_symbol(parts, i):
    counter = 1
    dict_parts = ["@{"]
    while i < len(parts) and counter != 0:

        if parts[i] == "@{":
            counter += 1
        if parts[i] == "}":
            counter -= 1
        dict_parts.append(parts[i])
        i += 1

    if(counter > 0):
        click.echo(f"Словарь не закрыт")
        exit(1)
    dict_parts = dict_parts[1:]
    dict_parts = dict_parts[:len(dict_parts) - 1]

    dict_text = " ".join(dict_parts)

    return dict_text, i

class Root:
    def __init__(self, text):
        self.constants = {}
        self.dictionaries = []

        parts = text.split(" ")

        i = 0
        while i < len(parts):
            part = parts[i]
            if part == "var": # Константы

                if i + 3 >= len(parts) or parts[i + 2] != "=" or not bool(name_re.match(parts[i + 1])): # Если после константы не следует is, то это ошибка
                    click.echo(f"Ошибка чтения файла! Неверное указание константы")
                    exit(1)
                else:
                    name = parts[i + 1]
                    if parts[i + 3] == "@{": # Если значение константы начинается с фигурной скобки, то это словарь
                        i += 4
                        dict_text, i = get_dict_from_symbol(parts, i)
                        self.constants[name] = Dictionary(dict_text, False, self) # Словарь на верхнем уровне

                    elif bool(number_re.match(parts[i + 3])): # Если значение константы - это число, то это число :)
                        try:
                            self.constants[name] = int(parts[i + 3])
                        except Exception as e:
                            self.constants[name] = float(parts[i + 3])
                        i += 4

                    elif bool(string_re.match(parts[i + 3])): # Если значение константы - это строка, то это строка :)
                        self.constants[name] = str(parts[i + 3].replace("000NBSP000", " ").lstrip("\"").rstrip("\""))
                        i += 4
                    else:
                        click.echo("Ошибка! Неверный тип значения")
            elif part == "@{": # На новой строке начался словарь
                i += 1
                dict_text, i = get_dict_from_symbol(parts, i)
                self.dictionaries.append(Dictionary(dict_text, True, self))  # Словарь на верхнем уровне
            else: # Ошибка
                click.echo(f"Ошибка чтения файла! Неизвестная строка: {part}")
                exit(1)

        for d in self.dictionaries:
            d.compile_constants(self.constants)

    @property
    def json(self) -> dict:
        data = {}
        for d in self.dictionaries:
            d_data = d.json
            for key in d_data:
                data[key] = d_data[key]

        return data

    def make_json(self, json_file):
        string = json.dumps(self.json, indent=4)
        with open(json_file, 'w') as f:
            f.write(string)


class Dictionary:
    def __init__(self, text, can_use_constants=False, root=None):
        self.text = text
        self.root = root
        self.can_use_constants = can_use_constants
        self.data = {}

        parts = text.split(" ")

        i = 0
        while i < len(parts):
            part = parts[i]
            if bool(name_re.match(part)):  # Ключи
                name = part

                if i + 2 >= len(parts) or parts[i + 1] != "=":  # Если после ключа не следует =>, то это ошибка
                    click.echo(f"Ошибка чтения файла! Создан ключ без значения: {name}")
                    exit(1)
                else:
                    if parts[i + 2] == "@{":  # Если значение ключа начинается с фигурной скобки, то это словарь
                        i += 3
                        dict_text, i = get_dict_from_symbol(parts, i)
                        self.data[name] = Dictionary(dict_text, self.can_use_constants, self.root)  # Словарь на верхнем уровне

                    elif bool(number_re.match(parts[i + 2])):  # Если значение ключа - это число, то это число :)
                        try:
                            self.data[name] = int(parts[i + 2])
                        except Exception as e:
                            self.data[name] = float(parts[i + 2])
                        i += 3
                    elif bool(string_re.match(parts[i + 2])):  # Если значение ключа - это строка, то это строка :)
                        self.data[name] = str(parts[i + 2].replace("000NBSP000", " ").lstrip("\"").rstrip("\""))
                        i += 3
                    elif bool(constant_usage_re.match(parts[i + 2])): # Если значение ключа - это константа
                        self.data[name] = Constant(parts[i + 2])
                        i += 3
                    else:
                        click.echo(f"Ошибка чтения файла! Неверный токен: {parts[i + 2]}")
                        exit(1)
            else:  # Ошибка
                click.echo(f"Ошибка чтения файла! Неизвестная строка: {part}")
                exit(1)

    def compile_constants(self, constants):
        for key in self.data:
            if isinstance(self.data[key], Constant):
                self.data[key] = constants[self.data[key].name]
            if isinstance(self.data[key], Dictionary):
                self.data[key].compile_constants(constants)

    @property
    def json(self) -> dict:
        data = {}
        for key in self.data:
            if isinstance(self.data[key], Dictionary):
                data[key] = self.data[key].json
            else:
                data[key] = self.data[key]
        return data


class Constant:
    def __init__(self, name):
        self.name = name.replace("^[", "").replace("]", "")


@click.command()
@click.argument('source_file', type=click.Path(exists=True), required=True)
@click.argument('destination_file', type=click.Path(), required=True)
def convert(source_file, destination_file):
    """
    Конвертирует SOURCE_FILE в DESTINATION_FILE.
    """
    # Проверка на существование исходного файла
    if not os.path.isfile(source_file):
        click.echo(f"Ошибка: Файл '{source_file}' не существует.")
        return

    try:
        with open(source_file, encoding='utf-8') as f:
            full_text = ""
            for string in f.readlines():
                if not string.startswith("::"):
                    segments_of_strings = string.split("\"")
                    for i in range(1, len(segments_of_strings), 2):
                        segments_of_strings[i] = segments_of_strings[i].replace(" ", "000NBSP000")
                    full_text += "\"".join(segments_of_strings) + "\n"

            full_text = full_text.replace("\n", " ")
            full_text = full_text.replace("\r", " ")
            full_text = full_text.replace("\t", " ")
            full_text = full_text.replace("=", " = ")
            full_text = full_text.replace("}", " } ")
            full_text = full_text.replace("@{", " @{ ")
            full_text = full_text.replace("]", "] ")
            full_text = full_text.replace("^[", " ^[")
            full_text = full_text.replace(";", "")

            while "  " in full_text:
                full_text = full_text.replace("  ", " ")

            full_text = full_text.rstrip()
            full_text = full_text.lstrip()

            root = Root(full_text)
            root.make_json(destination_file)
    except Exception as e:
        click.echo(f"Ошибка при конвертации файла: {e}")

if __name__ == "__main__":
    convert()
