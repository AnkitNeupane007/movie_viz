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

// Function to render genre ratings chart
function fetchAndRenderGenreChart() {
    const ctx = document.getElementById("genreChart").getContext("2d");

    fetch('/api/get_rating_by_genre')
        .then(response => response.json())
        .then(ratingList => {
            const genres = Object.keys(ratingList);
            const ratings = Object.values(ratingList);

            const genreChart = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: genres,
                    datasets: [{
                        label: "Average Rating",
                        data: ratings,
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.6)',
                            'rgba(75, 192, 192, 0.6)',
                            'rgba(153, 102, 255, 0.6)',
                            'rgba(255, 159, 64, 0.6)',
                            'rgba(255, 99, 132, 0.6)',
                            'rgba(255, 206, 86, 0.6)'
                        ],
                        borderColor: [
                            'rgba(54, 162, 235, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 159, 64, 1)',
                            'rgba(255, 99, 132, 1)',
                            'rgba(255, 206, 86, 1)'
                        ],
                        borderWidth: 1,
                        hoverBackgroundColor: 'rgba(54, 162, 235, 0.8)', // Hover effect
                        hoverBorderColor: 'rgba(54, 162, 235, 1)',  // Hover border color
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    onClick: (event, elements) => {
                        if (elements.length > 0) {
                            const genreClicked = genres[elements[0].index];
                            console.log("Genre clicked: ", genreClicked);
                            // Call the backend to fetch movies of the clicked genre
                            fetchMoviesByGenre(genreClicked, 1);
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Average Rating',
                                font: {
                                    size: 14
                                }
                            },
                            ticks: {
                                stepSize: 0.5,
                                max: 5,
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Genre',
                                font: {
                                    size: 14
                                }
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            enabled: true,
                            backgroundColor: 'rgba(0, 0, 0, 0.7)', // Tooltip background
                            titleColor: 'white',
                            bodyColor: 'white',
                            borderColor: 'rgba(255, 255, 255, 0.8)', // Tooltip border
                            borderWidth: 1,
                            padding: 10,
                        },
                        legend: {
                            position: 'top',
                            labels: {
                                font: {
                                    size: 14
                                }
                            }
                        }
                    },
                    animation: {
                        duration: 1000, // Smooth animation for bar rendering
                        easing: 'easeOutQuart',
                    }
                }
            });
        })
        .catch(error => console.error('Error fetching ratings data:', error));
}

function fetchMoviesByGenre(genre, page) {
    // Fetch movies for the selected genre and page
    fetch(`/api/get_movies_by_genre?genre=${genre}&page=${page}`)
        .then(response => response.json())
        .then(movies => {
            // Render movies and pagination buttons
            renderMovies(movies.movies, genre);
            renderPagination(movies.page, movies.total_pages, genre);
        })
        .catch(error => console.error('Error fetching movies:', error));
}

function renderMovies(movies, genre) {
    const movieList = document.getElementById('movie-list');
    movieList.innerHTML = ''; // Clear the previous movies

    // Display the genre at the top
    const genreElement = document.createElement('div');
    genreElement.classList.add('text-2xl', 'font-semibold', 'text-gray-800', 'mb-4');
    genreElement.innerHTML = `Movies in "${genre}" Genre`;
    movieList.appendChild(genreElement);

    // Render movie data
    movies.forEach(movie => {
        const movieElement = document.createElement('div');
        movieElement.classList.add('bg-gray-100', 'p-4', 'rounded-lg', 'shadow-sm', 'flex', 'justify-between', 'items-center');
        movieElement.innerHTML = `
            <div>
                <h3 class="text-xl font-semibold text-gray-800">${movie.title}</h3>
                <p class="text-sm text-gray-600">Rating: ${movie.rating}</p>
            </div>
            <button class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition" data-title="${movie.title}">View</button>
        `;
        movieList.appendChild(movieElement);
    });

    // Add click event listener to View buttons
    const viewButtons = movieList.querySelectorAll('button[data-title]');
    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const movieTitle = this.getAttribute('data-title');
            window.open(`/search?movie=${encodeURIComponent(movieTitle)}`, '_blank');
        });
    });
}


function renderPagination(currentPage, totalPages, genre) {
    const paginationContainer = document.getElementById('pagination-container');
    paginationContainer.innerHTML = ''; // Clear the previous pagination

    const paginationWrapper = document.createElement('div');
    paginationWrapper.classList.add('flex', 'items-center', 'space-x-4');

    // Previous Button
    if (currentPage > 1) {
        const prevButton = document.createElement('button');
        prevButton.classList.add('bg-gray-200', 'text-gray-700', 'px-4', 'py-2', 'rounded-md', 'hover:bg-gray-300', 'transition');
        prevButton.textContent = 'Previous';
        prevButton.onclick = () => fetchMoviesByGenre(genre, currentPage - 1);
        paginationWrapper.appendChild(prevButton);
    }

    // Page Number Buttons
    const pageRange = 3; // Show 3 page numbers before and after the current page
    const pageStart = Math.max(1, currentPage - pageRange);
    const pageEnd = Math.min(totalPages, currentPage + pageRange);

    for (let i = pageStart; i <= pageEnd; i++) {
        const pageButton = document.createElement('button');
        pageButton.classList.add('bg-blue-500', 'text-white', 'px-4', 'py-2', 'rounded-md', 'hover:bg-blue-600', 'transition');
        pageButton.textContent = i;
        if (i === currentPage) {
            pageButton.classList.add('bg-blue-700', 'font-semibold');
        }
        pageButton.onclick = () => fetchMoviesByGenre(genre, i);
        paginationWrapper.appendChild(pageButton);
    }

    // Next Button
    if (currentPage < totalPages) {
        const nextButton = document.createElement('button');
        nextButton.classList.add('bg-gray-200', 'text-gray-700', 'px-4', 'py-2', 'rounded-md', 'hover:bg-gray-300', 'transition');
        nextButton.textContent = 'Next';
        nextButton.onclick = () => fetchMoviesByGenre(genre, currentPage + 1);
        paginationWrapper.appendChild(nextButton);
    }

    // Go to page input box
    const pageInputWrapper = document.createElement('div');
    pageInputWrapper.classList.add('flex', 'items-center', 'space-x-2');
    const pageInput = document.createElement('input');
    pageInput.type = 'number';
    pageInput.classList.add('bg-white', 'border', 'border-gray-300', 'rounded-md', 'px-3', 'py-2', 'text-gray-700');
    pageInput.placeholder = `Go to page`;
    pageInput.min = 1;
    pageInput.max = totalPages;
    pageInput.value = currentPage;

    const goButton = document.createElement('button');
    goButton.classList.add('bg-blue-500', 'text-white', 'px-4', 'py-2', 'rounded-md', 'hover:bg-blue-600', 'transition');
    goButton.textContent = 'Go';
    goButton.onclick = () => {
        const pageNum = parseInt(pageInput.value);
        if (pageNum >= 1 && pageNum <= totalPages) {
            fetchMoviesByGenre(genre, pageNum);
        }
    };

    pageInputWrapper.appendChild(pageInput);
    pageInputWrapper.appendChild(goButton);

    paginationContainer.appendChild(paginationWrapper);
    paginationContainer.appendChild(pageInputWrapper);
}

// Run the function on page load
window.onload = function() {
    fetchAndRenderGenreChart();
};


// Define similar functions for actor and director charts.
