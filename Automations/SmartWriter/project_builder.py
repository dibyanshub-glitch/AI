import os

def create_project_structure(name, lang):

    root = f"Projects/{name}"
    os.makedirs(root, exist_ok=True)

    if lang == "react":
        os.makedirs(f"{root}/src", exist_ok=True)
        os.makedirs(f"{root}/public", exist_ok=True)

    return root
