function toggleFilterBar(element) {
    if (element.classList.contains('right')) {
        element.classList.replace('right', 'down')
        expandFilterBar()
    } else {
        element.classList.replace('down', 'right')
        collapseFilterBar()
    }
}

function expandFilterBar() {
    if (document.getElementById('filter_bar')) {
        document.getElementById('filter_bar').style.display = 'block'
    } else {
        document.getElementById('search_bar').insertAdjacentHTML('afterend', filterBarHtmlString)
    }
}

function collapseFilterBar() {
    document.getElementById('filter_bar').style.display = 'none'
}