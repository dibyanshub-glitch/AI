import os


def build_structure(plan):

    root = f"Projects/{plan['name']}"

    os.makedirs(root, exist_ok=True)

    for file in plan["files"]:
        path = os.path.join(root, file)

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w") as f:
            f.write("")

    return root
