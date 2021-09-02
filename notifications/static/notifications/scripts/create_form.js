window.onload = function() {
    document.getElementById('id_type').addEventListener('change', e => loadTypedNotificationForm(e))
}

function loadTypedNotificationForm(e) {
    fetch(`${url}/forms/${e.target.value}`)
        .then(response => response.json())
        .then(data => setTypedFormElement(data.form))
        .catch(e => showToast('Connection error'))
}

function setTypedFormElement(formHtmlString) {
    const typed_form = document.getElementById('typed_form')
    typed_form.innerHTML = formHtmlString
}
