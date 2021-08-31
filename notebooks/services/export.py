def get_notebook_code(notebook):
    return "\n".join(notebook.cells.order_by('id').values_list('code', flat=True))
