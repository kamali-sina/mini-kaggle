from workflows.models.workflow import Workflow
import json


def generate_dag(workflow: Workflow):
    dag = {"nodes": [], "edges": []}
    for task_dependency in workflow.task_dependencies.all():
        node = {
            "id": task_dependency.task.id,
            "label": task_dependency.task.name,
            "x": task_dependency.task.id,
            "y": task_dependency.task.id,
            "size": 4
        }
        dag["nodes"].append(node)

        for parent_task in task_dependency.parent_tasks:
            edge = {
                "id": "e" + parent_task.task.id,
                "source": "e" + parent_task.task.id,
                "target": task_dependency.task.id,
                "type": "arrow"
            }
            dag["edges"].append(edge)

    with open('dag.json', 'w') as outfile:
        json.dump(dag, outfile)

    print(dag)
