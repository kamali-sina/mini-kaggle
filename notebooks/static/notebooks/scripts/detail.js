const EDITOR_CONFIG = {
    lineNumbers: true,
    mode: "python",
    viewportMargin: Infinity
}


window.onload = function() {
    createEditorForCellElements()
}


function createEditorForCellElements() {
    /* creates an editor for each loaded cell of the notebook */

    const cellElements = Array.from(document.querySelectorAll('[id^=cell_code_]'));
    cellElements.forEach(cellElement => createEditorForCellElement(cellElement, cellElement.id.split('_').pop()))
}


function createEditorForCellElement(cellElement, cellId) {
    /* creates an editor for the given cell element */

    cellElement.value = cellElement.textContent
    window[getCellEditorName(cellId)] = CodeMirror.fromTextArea(cellElement, EDITOR_CONFIG);
    window[getCellEditorName(cellId)].on('change', () => markUnsaved(cellId))
}

function getCellEditorName(cellId) {
    /* returns the name of the editor created for the given cell */

    return `cell_editor_${cellId}`
}


function getCellCodeElementId(cellId) {
    /* returns the id of the rendered cell code element by cell id */

    return `cell_code_${cellId}`
}


function getCellStatElementId(cellId) {
    /* returns the id of the rendered cell status element by cell id */

    return `cell_stat_${cellId}`
}


function getCellResElementId(cellId) {
    /* returns the id of the rendered cell result element by cell id */

    return `cell_res_${cellId}`
}


function handleErrors(response) {
    /* Meant to handle response errors other than connection errors. Throws exception in case the response status is not ok' */

    if (!response.ok) {
        throw Error(response.statusText);
    }
    return response;
}


function addCell() {
    /* Creates a new cell at the end of the current notebook's cells and adds it to the DOM */


    const initObject = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({code: ""})
    }
    fetch(`${url}cell/create`, initObject)
        .then(handleErrors)
        .then(response => response.json())
        .then(data => data.cell)
        .then(cell => addCellElement(cell))
        .then(() => showToast('New cell created'))
        .catch(e => showToast('Failed to create the new cell'))
}


function addCellElement(cell) {
    /* Creates a cell element for the given cell */

    document.getElementsByClassName('cell-list')[0].insertAdjacentHTML('beforeend', cellItemHtmlString.replaceAll('{id_placeholder}', cell.id))
    const cellElement = document.getElementById(getCellCodeElementId(cell.id))
    cellElement.innerHTML = cell.code
    createEditorForCellElement(cellElement)
}


function saveCell(cellId) {
    /* Is called on focus out of the cell; In any changes are detected, saves the given cell for the current notebook
    and marks the cell as saved */

    const cellStatElement = document.getElementById(getCellStatElementId(cellId))
    if (cellStatElement.childNodes[1].classList.contains('sync')) {

        const cellEditor = window[getCellEditorName(cellId)]
        const initObject = {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({code: cellEditor.getValue()})
        }
        fetch(`${url}cell/update/${cellId}`, initObject)
            .then(handleErrors)
            .then(r => markSaved(cellId))
            .catch(e => showToast('Failed to save the cell'))
    }
}


function markUnsaved(cellId) {
    /* Is called on changes of the cell's editor. Marks the cell status as unsaved */

    const cellStatElement = document.getElementById(getCellStatElementId(cellId))
    cellStatElement.childNodes[2].nodeValue = "syncing ..."
    cellStatElement.childNodes[1].className = "sync alternate icon"
}


function markSaved(cellId) {
    /* Marks the cell status as saved */

    const cellStatElement = document.getElementById(getCellStatElementId(cellId))
    cellStatElement.childNodes[2].nodeValue = "saved"
    cellStatElement.childNodes[1].className = "cloud icon"
}


function deleteCell(cellId) {
    /* Deletes the given cell of the current notebook and removes it from the DOM */

    if (confirm('Are you sure you want to delete this cell?')) {

        const initObject = {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        }
        fetch(`${url}cell/delete/${cellId}`, initObject)
            .then(handleErrors)
            .then(r => showToast('Cell deleted'))
            .then(() => removeCellElement(cellId))
            .catch(e => showToast('Failed to delete the cell'))
    }
}


function removeCellElement(cellId) {
    /* Removes the given cell's entire elements from the DOM */

    const cellElement = document.getElementById(getCellCodeElementId(cellId)).parentNode.parentNode.parentNode
    cellElement.remove()
}


function startSession() {
    /* Starts a new session for the current notebook */

    console.log("Not implemented")
}


function restartSession() {
    /* Restarts the session for the current notebook */

    console.log("Not implemented")
}


function runCell(cellId) {
    /* Runs the given cell for the current notebook and renders the results in the DOM */

    console.log("Not implemented")
}


function showCellResult(resultData, cellId) {
    /* renders the result of running the given cell */

    const cellElement = document.getElementById(getCellCodeElementId(cellId)).parentNode.parentNode
    cellElement.insertAdjacentHTML('afterend', cellResultHtmlString.replace('{id_placeholder}', cellId))

    const resElement = document.getElementById(getCellResElementId(cellId))
    resElement.innerHTML = resultData.result
    resElement.classList.add(resultData.status ? 'cell-res-succeeded' : 'cell-res-failed')
}