function bindTo(event, bindInputId) {
    const boundInput = document.getElementById(bindInputId)
    boundInput.value = event.target.innerText
    highlightWords(event)
}

function highlightWords(event) {
    if (event.keyCode == 32 || event.keyCode == 13) {
        const words = Array.from(event.target.innerText.split(/\s+/))

        let highlighted_words = ''
        words.forEach(function(word) {
            if (word) {
                highlighted_words += `<span class="ui label" style="margin-top: 5px;">${word}</span> `
            }
        })
        highlighted_words += '&nbsp'

        event.target.innerHTML = highlighted_words

        //move cursor to the end of input field
        event.target.focus();
        document.execCommand('selectAll', false, null);
        document.getSelection().collapseToEnd();
    }
}
