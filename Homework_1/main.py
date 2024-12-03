import tkinter as tk
import zipfile
import sys

#  Функция, которая получает все пути в архиве в виде списка списков [путь (str), является_ли_директорией (bool)]
def get_paths_from_zip(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        return [[info.filename.rstrip("/"), info.is_dir()] for info in zipf.infolist()]


# Функция, которая строит новый путь относительно предыдущего и дополнения
def build_new_path(base_path, additional_path):
    base_parts = base_path.split("/")
    if additional_path.startswith("/"):
        base_parts = []
    additional_parts = additional_path.split("/")

    for part in additional_parts:
        if part == "..":
            base_parts = base_parts[:-1]
        elif part != "." and part != "":
            base_parts.append(part)

    return "/".join(base_parts)


class CommandLineApp:
    def __init__(self, root):
        self.paths = get_paths_from_zip(sys.argv[1])
        print(*self.paths, sep="\n")
        self.current_path = self.paths[0][0].split("/")[0]

        self.root = root
        self.root.title("Homework 1")
        self.text_area = tk.Text(root, height=20, width=80, bg='black', fg='white', insertbackground='white')
        self.text_area.pack(padx=10, pady=10)
        self.default_enter_text = "nochninog@nochninog:"

        self.text_area.insert(tk.END, self.get_enter_text())
        self.text_area.bind("<Return>", self.process_command)
        self.text_area.config(state=tk.NORMAL)
        self.command_start_index = self.text_area.index(tk.END)

    # Вывести встречающий текст с именем пользователя
    def get_enter_text(self):
        return self.default_enter_text + self.current_path.split("/")[-1] + "/ $ "

    # Проверить, что объект с таким путем существует
    def check_object_exists(self, path):
        return any(
            [p[0] == path for p in self.paths]
        )

    # Проверить, что объект с таким путем существует и является директорией
    def check_object_is_directory(self, path):
        return any(
            [(p[0] == path and p[1]) for p in self.paths]
        )

    # Получить все дочерние пути директории
    def get_children(self, path):
        return [
            p[0] for p in self.paths if path in p[0] and p[0].count("/") == path.count("/") + 1
        ] # Мы пробегаем по всем путям, смотрим, какие из них содержат в себе искомый (то есть, являются его дочерними)
        # Так, например, /root/documents содержит в себе /root, а значит, /root/documents является дочерним для /root
        # Кроме того, мы проверяем, что путь является именно непосредственным ребенком. Если путь является дочерним,
        # он содержит ровно на 1 слэш больше

    # Получить элемент по пути
    def get_element(self, path):
        for p in self.paths:
            if p[0] == path:
                return p
        return None

    def process_command(self, event):
        current_text = self.text_area.get("1.0", tk.END) # Получает текущий текст
        command = current_text.split('$ ')[-1].strip() # Получаем последнюю команду
        if command == "":
            self.text_area.insert(tk.END, "\n" + self.get_enter_text())
            return
        cmd, *args = command.split() # Получаем саму команду и ее аргументы
        result = ""

        # Выполняем текущую команду
        if cmd == "cd":
            to_dir = args[0] if len(args) > 0 else "./"
            new_path = build_new_path(self.current_path, to_dir) # Получаем новый путь от старого и того,
            # что передали в команде cd

            # проверяем, что такая папка существует, и это именно папка
            if self.check_object_exists(new_path):
                if self.check_object_is_directory(new_path):
                    self.current_path = new_path # Если все успешно, меняем текущую папку
                else:
                    result += f"\ncd: not a directory: {to_dir}"
            else:
                result += f"\ncd: no such file or directory: {to_dir}"
        elif cmd == "ls":
            # Устанавливаем папку, в которой мы будем выводить дочерние элементы как:
            # - текущую папку, если аргумент не передан
            # - другую папку относительно текущей, если она пердеана
            path = self.current_path if len(args) == 0 else build_new_path(self.current_path, args[0])

            # Проверяешь, что это действительно папка
            if self.check_object_exists(path):
                if self.check_object_is_directory(path):
                    # Выводим содержимое в 3 колонки
                    for (i, child) in enumerate(self.get_children(path)):
                        if i % 3 == 0:
                            result += "\n"
                        result += f"{child.split('/')[-1]:<20}"
                else:
                    result += f"\nls: not a directory: {path}"
            else:
                result += f"\nls: no such file or directory: {path}"
        elif cmd == "exit":
            self.root.quit()
        elif cmd == "rmdir":
            dir_to_remove = args[0]
            path = build_new_path(self.current_path, dir_to_remove)  # Получаем путь до удаляемой папки

            # проверяем, что такая папка существует, и это именно папка
            if self.check_object_exists(path):
                if self.check_object_is_directory(path):
                    # Проверяем наличие детей у папки
                    children = self.get_children(path)
                    if len(children) == 0:
                        self.paths = list(filter(lambda x: x[0] != path, self.paths))
                    else:
                        result += f"\nrmdir: {dir_to_remove}: Directory not empty"
                else:
                    result += f"\nrmdir: not a directory: {dir_to_remove}"
            else:
                result += f"\nrmdir: no such file or directory: {dir_to_remove}"

        elif cmd == "mv":
            move_object = args[0]
            destination = args[1]

            path_to_move_object = build_new_path(self.current_path, move_object)
            path_to_destination = build_new_path(self.current_path, destination)

            # Выполняем необходимые проверки
            if not self.check_object_exists(path_to_move_object):
                result += f"\nmv: no such file or directory: {move_object}"
            elif not self.check_object_exists(path_to_destination):
                result += f"\nmv: no such file or directory: {destination}"
            elif not self.check_object_is_directory(path_to_destination):
                result += f"\nmv: not a directory: {move_object}"
            elif path_to_move_object in path_to_destination:
                result += f"\nmv: recursive moving"
            else:
                # Пробегаем по всем элементам и заменяем путь до перемещаемой папки на путь до папки в новом месте
                for path in self.paths:
                    path[0] = path[0].replace(
                        path_to_move_object,
                        path_to_destination + "/" + path_to_move_object.split("/")[-1]
                    )

        result += "\n" + self.get_enter_text()
        self.text_area.insert(tk.END, result)
        self.text_area.see(tk.END)
        return "break"


if __name__ == "__main__":
    root = tk.Tk()
    app = CommandLineApp(root)
    root.mainloop()
