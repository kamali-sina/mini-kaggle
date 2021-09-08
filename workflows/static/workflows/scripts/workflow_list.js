window.onload = () => {
    $('.ui.checkbox').checkbox();
}


function changePauseStatus(element, workflowId) {
    /* Requests to change the workflows schedule ON/OFF status on the checkbox value changed */

    isChecked = $(`.ui.checkbox#schedule_${workflowId}`).checkbox('is checked');
    element.parentNode.style.pointerEvents = 'none'

    const initObject = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRFToken
        },
        body: JSON.stringify({
            paused: !isChecked
        })
    }
    fetch(`${window.location.href}${workflowId}/schedule/paused/`, initObject)
        .then(handleErrors)
        .then(r => toggleLabel(element))
        .then(() => showToast(`Workflow scheduling ${(isChecked ? 'enabled' : 'disabled')}`))
        .catch(e => revertChange())
        .finally(element.parentNode.style.pointerEvents = 'auto')
}


function toggleLabel(element) {
    /* Toggles the scheduling ON/OFF status label. */

    if (element.parentNode.childNodes[3].textContent == 'OFF') {
        element.parentNode.childNodes[3].textContent = 'ON'
    } else {
        element.parentNode.childNodes[3].textContent = 'OFF'
    }
}


function revertChange() {
    /* Rolls back the choice in case of failure. */

    $('.ui.checkbox').checkbox('toggle');
    showToast('Connection failed')
}

function handleErrors(response) {
    /* Meant to handle response errors other than connection errors. Throws exception in case the response status is not ok' */

    if (!response.ok) {
        throw Error(response.statusText);
    }
    return response;
}
