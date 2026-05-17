def create_tasks(ideas):

    tasks = []

    for idea in ideas:
        tasks.append({
            "type": "build_project",
            "idea": idea
        })

    return tasks
