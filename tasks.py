from invoke import task, run


@task
def build_exe(c):
    cmd = "pyinstaller --name tcexplorer --onefile implementations/tc/main.py"
    result = run(cmd, hide=True, warn=True)
    print(result)
