document.addEventListener("click", function (event) {
    const popup = document.querySelector(".popup");
    const input = popup.querySelector("input");
    if (!popup.contains(event.target)) {
        input.checked = false;
    }
});