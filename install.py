import subprocess

def check_dependencies():
    """
    """
    dependencies = ['telebot', 'requests', 'json']
    missing_dependencies = []
    for dependency in dependencies:
        try:
            __import__(dependency)
        except ImportError:
            missing_dependencies.append(dependency)

    return missing_dependencies

def install_dependencies(dependencies):
    """
    """
    if dependencies:
        print("As seguintes dependências não estão instaladas. Instalando-as...")
        for dependency in dependencies:
            subprocess.run(['pip', 'install', dependency])
        print("Dependências instaladas com sucesso!")

if __name__ == "__main__":
    missing_deps = check_dependencies()
    if missing_deps:
        install_dependencies(missing_deps)
    else:
        print("Todas as dependências estão instaladas.")