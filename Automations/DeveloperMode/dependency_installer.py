import subprocess


def install_dependencies(plan, root):

    deps = plan.get("dependencies", [])

    for dep in deps:
        subprocess.call(["pip", "install", dep])
