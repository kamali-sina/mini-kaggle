function showToast(message) {
    const toastElement = document.getElementById("toast");
    toastElement.className = "show";
    toastElement.innerHTML = message
    setTimeout(function(){ toastElement.className = toastElement.className.replace("show", ""); }, 3000);
}
