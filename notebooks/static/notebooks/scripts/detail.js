!function(a,b){"function"==typeof define&&define.amd?define([],b):"undefined"!=typeof module&&module.exports?module.exports=b():a.ReconnectingWebSocket=b()}(this,function(){function a(b,c,d){function l(a,b){var c=document.createEvent("CustomEvent");return c.initCustomEvent(a,!1,!1,b),c}var e={debug:!1,automaticOpen:!0,reconnectInterval:1e3,maxReconnectInterval:3e4,reconnectDecay:1.5,timeoutInterval:2e3};d||(d={});for(var f in e)this[f]="undefined"!=typeof d[f]?d[f]:e[f];this.url=b,this.reconnectAttempts=0,this.readyState=WebSocket.CONNECTING,this.protocol=null;var h,g=this,i=!1,j=!1,k=document.createElement("div");k.addEventListener("open",function(a){g.onopen(a)}),k.addEventListener("close",function(a){g.onclose(a)}),k.addEventListener("connecting",function(a){g.onconnecting(a)}),k.addEventListener("message",function(a){g.onmessage(a)}),k.addEventListener("error",function(a){g.onerror(a)}),this.addEventListener=k.addEventListener.bind(k),this.removeEventListener=k.removeEventListener.bind(k),this.dispatchEvent=k.dispatchEvent.bind(k),this.open=function(b){h=new WebSocket(g.url,c||[]),b||k.dispatchEvent(l("connecting")),(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","attempt-connect",g.url);var d=h,e=setTimeout(function(){(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","connection-timeout",g.url),j=!0,d.close(),j=!1},g.timeoutInterval);h.onopen=function(){clearTimeout(e),(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onopen",g.url),g.protocol=h.protocol,g.readyState=WebSocket.OPEN,g.reconnectAttempts=0;var d=l("open");d.isReconnect=b,b=!1,k.dispatchEvent(d)},h.onclose=function(c){if(clearTimeout(e),h=null,i)g.readyState=WebSocket.CLOSED,k.dispatchEvent(l("close"));else{g.readyState=WebSocket.CONNECTING;var d=l("connecting");d.code=c.code,d.reason=c.reason,d.wasClean=c.wasClean,k.dispatchEvent(d),b||j||((g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onclose",g.url),k.dispatchEvent(l("close")));var e=g.reconnectInterval*Math.pow(g.reconnectDecay,g.reconnectAttempts);setTimeout(function(){g.reconnectAttempts++,g.open(!0)},e>g.maxReconnectInterval?g.maxReconnectInterval:e)}},h.onmessage=function(b){(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onmessage",g.url,b.data);var c=l("message");c.data=b.data,k.dispatchEvent(c)},h.onerror=function(b){(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onerror",g.url,b),k.dispatchEvent(l("error"))}},1==this.automaticOpen&&this.open(!1),this.send=function(b){if(h)return(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","send",g.url,b),h.send(b);throw"INVALID_STATE_ERR : Pausing to reconnect websocket"},this.close=function(a,b){"undefined"==typeof a&&(a=1e3),i=!0,h&&h.close(a,b)},this.refresh=function(){h&&h.close()}}return a.prototype.onopen=function(){},a.prototype.onclose=function(){},a.prototype.onconnecting=function(){},a.prototype.onmessage=function(){},a.prototype.onerror=function(){},a.debugAll=!1,a.CONNECTING=WebSocket.CONNECTING,a.OPEN=WebSocket.OPEN,a.CLOSING=WebSocket.CLOSING,a.CLOSED=WebSocket.CLOSED,a});

const webSocket = new ReconnectingWebSocket(`ws://${window.location.host}/ws/notebook/${notebookId}/`);
webSocket.onmessage = function (message) {
    responseData = JSON.parse(message.data)
    markStopped(responseData.cell_id)
    if (responseData.message_type === "notification") {
        showToast(responseData.result)
    } else {
        showCellResult(responseData.cell_id, responseData.result)
    }
}


const EDITOR_CONFIG = {
    lineNumbers: true,
    mode: "python",
    viewportMargin: Infinity,
    extraKeys: {
        "Shift-Enter": function (cm) {
            cm.getWrapperElement().closest(".cell").querySelector(".cell-run").click()
        }
    }
}


window.onload = function () {
    if (document.querySelectorAll('[id^=cell_code_]').length) {
        // Initialize notebook cells with editor
        createEditorForCellElements()
    } else {
        // Add an initial empty cell
        addCell("")
    }


    // Initialize Semantic dropdown
    $('.ui.dropdown').dropdown({
        apiSettings: {
            url: `${window.location.origin}/notebooks/snippets/`
        }
    })
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


function getCellRunElementId(cellId) {
    /* returns the id of the cell's running elements by cell id */

    return `cell_run_${cellId}`
}

function handleErrors(response) {
    /* Meant to handle response errors other than connection errors. Throws exception in case the response status is not ok' */

    if (!response.ok) {
        throw Error(response.statusText);
    }
    return response;
}


function addCell(code) {
    /* Creates a new cell at the end of the current notebook's cells and adds it to the DOM */

    const initObject = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRFToken
        },
        body: JSON.stringify({code: code})
    }
    fetch(`${window.location.href}cell/create/`, initObject)
        .then(handleErrors)
        .then(response => response.json())
        .then(data => addCellElement(data.id, data.code))
        .then(() => showToast('New cell created'))
        .catch(e => showToast('Failed to create the new cell'))
}


function addCellElement(cellId, cellCode) {
    /* Creates a cell element for the given cell */

    document.getElementsByClassName('cell-list')[0].insertAdjacentHTML('beforeend', cellItemHtmlString.replaceAll('{id_placeholder}', cellId))
    const cellElement = document.getElementById(getCellCodeElementId(cellId))
    cellElement.innerHTML = cellCode
    createEditorForCellElement(cellElement, cellId)
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
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRFToken
            },
            body: JSON.stringify({code: cellEditor.getValue()})
        }
        fetch(`${window.location.href}cell/update/${cellId}/`, initObject)
            .then(handleErrors)
            .then(r => markSaved(cellId))
            .catch(e => showToast('Failed to save the cell'))
    } else {
        markSaved(cellId)
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
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRFToken
            }
        }
        fetch(`${window.location.href}cell/delete/${cellId}/`, initObject)
            .then(handleErrors)
            .then(r => showToast('Cell deleted'))
            .then(() => removeCellElement(cellId))
            .catch(e => showToast('Failed to delete the cell'))
    }
}


function clearResults() {
    /* Clear all results after success restart session */
    const resultElements = document.getElementsByClassName("cell-res")
    while(resultElements.length > 0){
        resultElements[0].parentNode.parentNode.remove();
    }
}

function removeCellElement(cellId) {
    /* Removes the given cell's entire elements from the DOM */

    const cellElement = document.getElementById(getCellCodeElementId(cellId)).parentNode.parentNode.parentNode
    cellElement.remove()
}


function restartSession() {
    /* Restart the session for the current notebook */
    document.getElementById("page-loading").style.display = "block"
    const initObject = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRFToken
        }
    }
    markRestarting()
    fetch(`${window.location.href}restart_kernel/`, initObject)
        .then(handleErrors)
        .then(() => showToast('Session restarted'))
        .then(() => clearResults())
        .catch(function (e) {
            showToast('Failed to restart the session');
        })
        .finally(() => {
            markStoppedRestarting()
        });
}


function markRestarting() {
    const restartSessionIcon = document.getElementById("restart-session-icon")
    restartSessionIcon.classList.add('loading')
    restartSessionIcon.parentNode.style.pointerEvents = 'none'
    document.getElementById("page-loading").style.display = "block"
}


function markStoppedRestarting() {
    const restartSessionIcon = document.getElementById("restart-session-icon")
    restartSessionIcon.classList.remove('loading')
    restartSessionIcon.parentNode.style.pointerEvents = 'auto'
    document.getElementById("page-loading").style.display = "none"
}


function runCell(cellId) {
    /* Runs the given cell for the current notebook and renders the results in the DOM */

    markRunning(cellId)
    const cellEditor = window[getCellEditorName(cellId)]
    if (webSocket.readyState == 1) {
        data = JSON.stringify({cell_id: cellId, code: cellEditor.getValue()})
        webSocket.send(data)
    } else {
        showToast('The connection has been lost. Please Wait...');
        markStopped(cellId);
    }
}


function markRunning(cellId) {
    const runElement = document.getElementById(getCellRunElementId(cellId))
    runElement.style.pointerEvents = 'none'
    const iconElement = runElement.childNodes[1]
    iconElement.classList = ""
    iconElement.classList.add('ui', 'mini', 'active', 'inline', 'loader')
}


function markStopped(cellId) {
    const runElement = document.getElementById(getCellRunElementId(cellId))
    runElement.style.pointerEvents = 'auto'
    const iconElement = runElement.childNodes[1]
    iconElement.classList = ""
    iconElement.classList.add('play', 'icon')
}


function showCellResult(cellId, result) {
    /* renders the result of running the given cell */

    if (!document.getElementById(getCellResElementId(cellId))) {
        const cellElement = document.getElementById(getCellCodeElementId(cellId)).parentNode.parentNode
        cellElement.insertAdjacentHTML('afterend', cellResultHtmlString.replace('{id_placeholder}', cellId))
    }
    const resElement = document.getElementById(getCellResElementId(cellId))
    resElement.innerText = result
}


function addSnippet() {
    /* adds the selected code snippet from the dropdown menu to the notebook cells */

    fetch(`${window.origin}/notebooks/snippets/${$('.ui.dropdown').dropdown('get value')}/`)
        .then(handleErrors)
        .then(response => response.json())
        .then(data => addCell(data.snippet))
        .then(() => showToast('Snippet added successfully'))
        .catch(e => showToast('Failed to add the snippet'))
}

$(document).bind('keydown', function (e) {
    if (e.shiftKey && e.which === 78) {
        addCell('')
        return false;
    }
});
