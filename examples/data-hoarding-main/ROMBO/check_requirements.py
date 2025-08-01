import subprocess
import sys

def check_requirements(file_path):
    def check_installation(module):
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'show', module], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False

    def install_module(module):
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', module], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Installing {module}...")
            return True
        except subprocess.CalledProcessError:
            return False

    try:
        with open(file_path, "r") as file:
            modules = file.readlines()
    except FileNotFoundError:
        print(f"{file_path} not found.")
        return

    module_list = [module.strip() for module in modules]

    modules_to_install = [module for module in module_list if not check_installation(module)]

    if modules_to_install:
        for module in modules_to_install:
            install_module(module)

if __name__ == "__main__":
    check_requirements("requirements.txt")