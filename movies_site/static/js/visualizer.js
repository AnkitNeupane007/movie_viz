function fetchActorSuggestions() {
    const query = document.getElementById("searchActor").value.trim();
    if (query.length === 0) {
        document.getElementById("actorSuggestions").classList.add("hidden");
        return;
    }
    fetch(`/api/suggestions/actors?query=${query}`)
        .then(response => response.json())
        .then(data => {
            const suggestions = document.getElementById("actorSuggestions");
            suggestions.innerHTML = "";
            if (data.length > 0) {
                data.forEach(actor => {
                    const li = document.createElement("li");
                    li.textContent = actor[0];
                    li.className = "p-2 hover:bg-gray-700 cursor-pointer hover:text-white";
                    li.onclick = () => {
                        document.getElementById("searchActor").value = actor[0];
                        suggestions.classList.add("hidden");
                    };
                    suggestions.appendChild(li);
                });
                suggestions.classList.remove("hidden");
            } else {
                suggestions.classList.add("hidden");
            }
        });
}

function fetchDirectorSuggestions() {
    const query = document.getElementById("searchDirector").value.trim();
    if (query.length === 0) {
        document.getElementById("directorSuggestions").classList.add("hidden");
        return;
    }
    fetch(`/api/suggestions/directors?query=${query}`)
        .then(response => response.json())
        .then(data => {
            const suggestions = document.getElementById("directorSuggestions");
            suggestions.innerHTML = "";
            if (data.length > 0) {
                data.forEach(director => {
                    const li = document.createElement("li");
                    li.textContent = director[0];
                    li.className = "p-2 hover:bg-gray-700 cursor-pointer hover:text-white";
                    li.onclick = () => {
                        document.getElementById("searchDirector").value = director[0];
                        suggestions.classList.add("hidden");
                    };
                    suggestions.appendChild(li);
                });
                suggestions.classList.remove("hidden");
            } else {
                suggestions.classList.add("hidden");
            }
        });
}

function fetchMovieSuggestions(inputId) {
    const query = document.getElementById(inputId).value.trim();
    const suggestionsBox = document.getElementById(`${inputId}Suggestions`);

    if (query.length === 0) {
        suggestionsBox.classList.add("hidden");
        return;
    }

    fetch(`/api/suggestions?query=${query}`)
        .then(response => response.json())
        .then(data => {
            suggestionsBox.innerHTML = "";

            if (data.length > 0) {
                data.forEach(movie => {
                    const li = document.createElement("li");
                    li.textContent = movie;
                    li.className = "p-2 hover:bg-gray-700 cursor-pointer hover:text-white";
                    li.onclick = () => {
                        document.getElementById(inputId).value = movie;
                        suggestionsBox.classList.add("hidden");
                    };
                    suggestionsBox.appendChild(li);
                });
                suggestionsBox.classList.remove("hidden");
            } else {
                suggestionsBox.classList.add("hidden");
            }
        })
        .catch(error => console.error("Error fetching suggestions:", error));
}
