import git
import csv
from graphviz import Digraph


def read_config(file_path):
    """
    Читает конфигурационный CSV файл и возвращает словарь с данными.
    """
    config_data = {}

    with open(file_path, mode='r') as file:
        reader = csv.reader(file)

        for row in reader:
            if len(row) == 2:
                key, value = row
                config_data[key] = value


    return config_data


config = read_config("config.csv")
print(config)

def list_of_commits(repo_path, file_path):
    """
    Получает список коммитов, в которых фигурирует указанный файл.
    """
    repo = git.Repo(repo_path)

    commits = list(repo.iter_commits(paths=file_path))

    return commits


def create_graph_for_repo(commits):
    """
    Строит граф, в котором узлы содержат информацию о коммитах: дата, время, автор.
    """
    dot = Digraph(comment='Commit History Graph')

    for i, commit in enumerate(commits):
        commit_info = f"Commit: {commit.hexsha[:7]}\nAuthor: {commit.author.name}\nDate: {commit.committed_datetime}"
        dot.node(str(i), commit_info)

        if i > 0:
            dot.edge(str(i - 1), str(i))

    return dot


def visualize_graph(dot, graph_file):
    """
    Визуализируем граф с помощью graphviz.
    """
    dot.render(graph_file.split(".")[0], format='png', cleanup=True)
    with open(graph_file, "w") as f:
        f.write(dot.source)
    print(dot.source)


repo_path = config["repository_path"]

commits = list_of_commits(repo_path, config["repository_file"])
dot = create_graph_for_repo(commits)
visualize_graph(dot, "graph.txt")

