// Utility function to handle clicks outside the suggestion box
function handleClickOutsideSuggestions(suggestionBoxId) {
    document.addEventListener('click', function(event) {
        const suggestions = document.getElementById(suggestionBoxId);
        const inputField = document.getElementById(suggestionBoxId.replace('Suggestions', ''));

        // Hide the suggestion box if the click was outside the input or suggestions box
        if (!suggestions.contains(event.target) && event.target !== inputField) {
            suggestions.classList.add('hidden');
        }
    });
}

function fetchActorSuggestions() {
    const query = document.getElementById("searchActor").value.trim();
    const suggestions = document.getElementById("actorSuggestions");

    if (query.length === 0) {
        suggestions.classList.add("hidden");
        return;
    }

    fetch(`/api/suggestions/actors?query=${query}`)
        .then(response => response.json())
        .then(data => {
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

    handleClickOutsideSuggestions('actorSuggestions');
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

        handleClickOutsideSuggestions('directorSuggestions');

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

        handleClickOutsideSuggestions(`${inputId}Suggestions`);
}

// Function to render genre ratings chart
function fetchAndRenderGenreChart() {
    const ctx = document.getElementById("genreChart").getContext("2d");

    fetch('/api/get_rating_by_genre')
        .then(response => response.json())
        .then(ratingList => {
            const genres = Object.keys(ratingList);
            const ratings = Object.values(ratingList);

            // Create gradient background for bars

            const genreChart = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: genres,
                    datasets: [{
                        label: null,
                        data: ratings,
                        backgroundColor: "rgba(0, 0, 0, 0.8)", // Use gradient colors
                        borderColor: "rgba(255, 255, 255, 0.8)",
                        borderWidth: 2,
                        borderRadius: 8, // Rounded corners
                        hoverBackgroundColor: "rgba(56, 56, 56, 0.8)", // Prevent flickering
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    onClick: (event, elements) => {
                        if (elements.length > 0) {
                            const genreClicked = genres[elements[0].index];
                            // console.log("Genre clicked: ", genreClicked);
                            fetchMoviesByGenre(genreClicked, 1);
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: '⭐Average Rating',
                                font: { size: 16, weight: "bold" },
                                color: "#4A5568",
                            },
                            ticks: {
                                stepSize: 1,
                                max: 5,
                                font: { size: 14, weight: "bold" },
                                color: "#2D3748",
                            },
                            grid: {
                                display: false,
                                drawBorder: true,
                            },
                        },
                        x: {
                            title: {
                                display: true,
                                text: '🎬Genre',
                                font: { size: 16, weight: "bold" },
                                color: "#4A5568",
                            },
                            ticks: {
                                font: { size: 14, weight: "bold" },
                                color: "#2D3748",
                            },
                            grid: {
                                display: false,
                                drawBorder: true,
                            },
                        }
                    },
                    plugins: {
                        tooltip: {
                            enabled: true,
                            backgroundColor: "rgba(0, 0, 0, 0.8)",
                            titleColor: "white",
                            bodyColor: "white",
                            borderColor: "rgba(255, 255, 255, 0.8)",
                            borderWidth: 1,
                            padding: 12,
                            titleFont: { weight: "bold", size: 16 },
                            bodyFont: { size: 14 },
                        },
                        legend: {
                            display: false
                        }
                    },
                    animation: {
                        duration: 1500,
                        easing: "easeOutBounce",
                    }
                }
            });
        })
        .catch(error => console.error('Error fetching ratings data:', error));
}

// Function to fetch and render top grossing movies chart
function fetchAndRenderTopGrossingMovies() {
    const ctx = document.getElementById("topGrossingMoviesChart").getContext("2d");

    fetch('/api/top_grossing_movies')
        .then(response => response.json())
        .then(movies => {
            const movieTitles = movies.map(movie => movie[0]); // Extract movie titles
            const movieRevenues = movies.map(movie => movie[1]); // Extract movie revenues

            const topGrossingMoviesChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: movieTitles,
                    datasets: [{
                        label: 'Revenue ($)',
                        data: movieRevenues,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)', // Bar color
                        borderColor: 'rgb(255, 255, 255)',
                        borderWidth: 1,
                        borderRadius: 8,
                        hoverBackgroundColor: "rgba(56, 56, 56, 0.8)",
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Revenue ($)',
                                font: { size: 16, weight: 'bold' },
                                color: '#4A5568'
                            },
                            ticks: {
                                font: { size: 14, weight: 'bold' },
                                color: '#2D3748'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Movie Title',
                                font: { size: 16, weight: 'bold' },
                                color: '#4A5568'
                            },
                            ticks: {
                                font: { size: 14, weight: 'bold' },
                                color: '#2D3748'
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            enabled: true,
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: 'white',
                            bodyColor: 'white',
                            borderColor: 'rgba(255, 255, 255, 0.8)',
                            borderWidth: 1,
                            padding: 12,
                            titleFont: { weight: 'bold', size: 16 },
                            bodyFont: { size: 14 }
                        },
                        legend: {
                            display: false
                        }
                    },
                    onClick: function (event, elements) {
                        if (elements.length > 0) {
                            const index = elements[0].index;
                            const movieName = movieTitles[index]; // Get the movie name
                            window.open(`/search?movie=${encodeURIComponent(movieName)}`, '_blank');
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error fetching top grossing movies data:', error));
}

// Function to fetch and render top rated movies chart
function fetchAndRenderTopRatedMovies() {
    const ctx = document.getElementById("topRatedMoviesChart").getContext("2d");

    // Fetch top rated movies from the Flask API
    fetch('/api/top_rated_movies')
        .then(response => response.json())
        .then(movies => {
            const movieTitles = movies.map(movie => movie[0]); // Extract movie titles
            const movieRatings = movies.map(movie => movie[1]); // Extract movie ratings

            // Create the bar chart
            const topRatedMoviesChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: movieTitles,
                    datasets: [{
                        label: 'Rating',
                        data: movieRatings,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)', // Blue bars
                        borderColor: 'rgb(255, 255, 255)',
                        borderWidth: 1,
                        borderRadius: 8, // Rounded corners
                        hoverBackgroundColor: "rgba(56, 56, 56, 0.8)"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y', // Horizontal bar chart
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Rating',
                                font: { size: 16, weight: 'bold' },
                                color: '#4A5568'
                            },
                            ticks: {
                                font: { size: 14, weight: 'bold' },
                                color: '#2D3748'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Movie Title',
                                font: { size: 16, weight: 'bold' },
                                color: '#4A5568'
                            },
                            ticks: {
                                font: { size: 14, weight: 'bold' },
                                color: '#2D3748'
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            enabled: true,
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: 'white',
                            bodyColor: 'white',
                            borderColor: 'rgba(255, 255, 255, 0.8)',
                            borderWidth: 1,
                            padding: 12,
                            titleFont: { weight: 'bold', size: 16 },
                            bodyFont: { size: 14 }
                        },
                        legend: {
                            display: false
                        }
                    },
                    onClick: function (event, elements) {
                        if (elements.length > 0) {
                            const index = elements[0].index;
                            const movieName = movieTitles[index]; // Get the movie name
                            window.open(`/search?movie=${encodeURIComponent(movieName)}`, '_blank'); // Open in new tab
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error fetching top rated movies data:', error));
}

// Fucntion to fetch adn render actors who have worked in the most movies
function fetchAndRenderTopActorsInMovies() {
    const ctx = document.getElementById("topActorsInMoviesChart").getContext("2d");

    // Fetch top actors in movies from the Flask API
    fetch('/api/top_movies_actors')
        .then(response => response.json())
        .then(actors => {
            const actorNames = actors.map(actor => actor[0]); // Extract actor names
            const movieCount = actors.map(actor => actor[1]); // Extract number of movies

            // Create the bar chart
            const topActorsInMoviesChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: actorNames,
                    datasets: [{
                        label: 'Number of movies',
                        data: movieCount,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)', // Blue bars
                        borderColor: 'rgb(255, 255, 255)',
                        borderWidth: 1,
                        borderRadius: 8, // Rounded corners
                        hoverBackgroundColor: "rgba(56, 56, 56, 0.8)"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y', // Horizontal bar chart
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Movie Count',
                                font: { size: 16, weight: 'bold' },
                                color: '#4A5568'
                            },
                            ticks: {
                                font: { size: 14, weight: 'bold' },
                                color: '#2D3748'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Actor Name',
                                font: { size: 16, weight: 'bold' },
                                color: '#4A5568'
                            },
                            ticks: {
                                font: { size: 14, weight: 'bold' },
                                color: '#2D3748'
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            enabled: true,
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: 'white',
                            bodyColor: 'white',
                            borderColor: 'rgba(255, 255, 255, 0.8)',
                            borderWidth: 1,
                            padding: 12,
                            titleFont: { weight: 'bold', size: 16 },
                            bodyFont: { size: 14 }
                        },
                        legend: {
                            display: false
                        }
                    },
                    onClick: function (event, elements) {
                        if (elements.length > 0) {
                            const index = elements[0].index;
                            const actorName = actorNames[index]; // Get the actor name
                            window.open(`/fetch_actor_stats?actor=${encodeURIComponent(actorName)}`, '_blank'); // Open in new tab
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error fetching top actors data:', error));
}

// Function to fetch and render directors who have worked in most movies
function fetchAndRenderTopDirectorsInMovies() {
    const ctx = document.getElementById("topDirectorsInMoviesChart").getContext("2d");

    // Fetch top directors in movies from the Flask API
    fetch('/api/top_movies_directors')
        .then(response => response.json())
        .then(directors => {
            const directorNames = directors.map(director => director[0]); // Extract director names
            const numOfMovies = directors.map(director => director[1]); // Extract number of movies

            // Create the bar chart
            const topDirectorsInMoviesChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: directorNames,
                    datasets: [{
                        label: 'Number of Movies',
                        data: numOfMovies,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)', // Red bars
                        borderColor: 'rgb(255, 255, 255)',
                        borderWidth: 1,
                        borderRadius: 8, // Rounded corners
                        hoverBackgroundColor: "rgba(56, 56, 56, 0.8)"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y', // Horizontal bar chart
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Number of Movies',
                                font: { size: 16, weight: 'bold' },
                                color: '#4A5568'
                            },
                            ticks: {
                                font: { size: 14, weight: 'bold' },
                                color: '#2D3748'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Director Name',
                                font: { size: 16, weight: 'bold' },
                                color: '#4A5568'
                            },
                            ticks: {
                                font: { size: 14, weight: 'bold' },
                                color: '#2D3748'
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            enabled: true,
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: 'white',
                            bodyColor: 'white',
                            borderColor: 'rgba(255, 255, 255, 0.8)',
                            borderWidth: 1,
                            padding: 12,
                            titleFont: { weight: 'bold', size: 16 },
                            bodyFont: { size: 14 }
                        },
                        legend: {
                            display: false
                        }
                    },
                    onClick: function (event, elements) {
                        if (elements.length > 0) {
                            const index = elements[0].index;
                            const directorName = directorNames[index]; // Get the director name
                            window.open(`/fetch_director_stats?director=${encodeURIComponent(directorName)}`, '_blank'); // Open in new tab
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error fetching top directors data:', error));
}


// WHen a genre is clicked, fetch movies for that genre and page
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

// Function to render movies and pagination buttons
function renderMovies(movies, genre) {
    const movieList = document.getElementById('movie-list');
    movieList.innerHTML = ''; // Clear the previous movies

    // Display the genre at the top
    const genreElement = document.createElement('div');
    genreElement.classList.add('text-2xl', 'font-semibold', 'text-gray-600', 'mb-4');
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

// Function to render pagination buttons
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
    fetchAndRenderTopGrossingMovies();
    fetchAndRenderTopRatedMovies();
    fetchAndRenderTopActorsInMovies();
    fetchAndRenderTopDirectorsInMovies();
};

