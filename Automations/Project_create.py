import os

def create_project(name, tech="web"):
    base = f"Projects/{name}"
    os.makedirs(base, exist_ok=True)

    if tech == "web":
        os.makedirs(f"{base}/frontend", exist_ok=True)
        os.makedirs(f"{base}/backend", exist_ok=True)

    return base
