import sys
from assembler import process_file
from interpreter import run

def main():
    if len(sys.argv) < 2:
        print("Ошибка: не указана команда.")
        sys.exit(1)

    command = sys.argv[1]

    if command == "assembler":
        if len(sys.argv) != 5:
            print("Ошибка: неверное количество аргументов для команды 'assembler'.")
            sys.exit(1)
        input_file, output_file, log_file = sys.argv[2:5]
        try:
            process_file(input_file, output_file, log_file)
            print(f"Сборка завершена. Результат сохранен в {output_file}. Лог: {log_file}.")
        except Exception as e:
            print(f"Ошибка при сборке: {e}")
            sys.exit(1)

    elif command == "interpreter":
        if len(sys.argv) != 4:
            print("Ошибка: неверное количество аргументов для команды 'interpreter'.")
            sys.exit(1)
        input_file, result_file = sys.argv[2:4]
        try:
            run(input_file, result_file)
            print(f"Интерпретация завершена. Результат сохранен в {result_file}.")
        except Exception as e:
            print(f"Ошибка при интерпретации: {e}")
            sys.exit(1)

    else:
        print(f"Ошибка: неизвестная команда '{command}'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
