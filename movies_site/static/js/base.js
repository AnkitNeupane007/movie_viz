// For the popup menu
document.addEventListener("click", function (event) {
    const popup = document.querySelector(".popup");
    const input = popup.querySelector("input");
    if (!popup.contains(event.target)) {
        input.checked = false;
    }
});

// For search suggestions
async function fetchSuggestions() {
    let query = document.getElementById('movie').value.trim();
    let suggestionsBox = document.getElementById('suggestions');

    if (query.length < 1) {
        suggestionsBox.classList.add('hidden');
        return;
    }

    try {
        let response = await fetch(`/api/suggestions?query=${query}`);
        let suggestions = await response.json();
        
        suggestionsBox.innerHTML = '';
        if (suggestions.length > 0) {
            suggestions.forEach(movie => {
                let listItem = document.createElement('li');
                listItem.textContent = movie;
                listItem.classList.add('p-2', 'hover:bg-gray-200', 'cursor-pointer');
                listItem.onclick = () => {
                    document.getElementById('movie').value = movie;
                    suggestionsBox.classList.add('hidden');
                };
                suggestionsBox.appendChild(listItem);
            });
            suggestionsBox.classList.remove('hidden');
        } else {
            suggestionsBox.classList.add('hidden');
        }
    } catch (error) {
        console.error('Error fetching suggestions:', error);
    }
}

document.addEventListener('click', (event) => {
    let suggestionsBox = document.getElementById('suggestions');
    if (!event.target.closest('#movie') && !event.target.closest('#suggestions')) {
        suggestionsBox.classList.add('hidden');
    }
});