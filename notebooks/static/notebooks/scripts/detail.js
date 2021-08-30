const EDITOR_CONFIG = {
    lineNumbers: true,
    mode:  "python",
    viewportMargin: Infinity
}


window.onload = function() {
    createEditorForCellElements()
}


function createEditorForCellElements() {
    /* creates an editor for each loaded cell of the notebook */

    cellElements = Array.from(document.querySelectorAll('[id^=cell_]'));
    cellElements.forEach(cellElement => createEditorForCellElement(cellElement))
}

function createEditorForCellElement(cellElement) {
    /* creates an editor for the given cell element */

    cellElement.value = cellElement.textContent
    window[`${cellElement.id}`] = CodeMirror.fromTextArea(cellElement, EDITOR_CONFIG);
}