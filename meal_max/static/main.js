// Login Form Handler
document.getElementById("login-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const response = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });

    const data = await response.json();
    const message = data.message || data.error;
    document.getElementById("login-message").innerText = message;
});
document.getElementById("search-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const query = document.getElementById("query").value.trim();

    if (!query) {
        document.getElementById("search-results").innerHTML = `<p>Please enter a search term.</p>`;
        return;
    }

    try {
        console.log(`Sending request to backend with query: ${query}`);
        const response = await fetch(`/api/search/movie?query=${encodeURIComponent(query)}`);
        
        console.log(`Response status: ${response.status}`);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Error ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log("Received data:", data);

        const resultsDiv = document.getElementById("search-results");
        if (data.results && data.results.length > 0) {
            resultsDiv.innerHTML = data.results
                .map(
                    (movie) =>
                        `<div>
                            <h3>${movie.title} (${movie.release_date || "N/A"})</h3>
                            <p>${movie.overview || "No overview available."}</p>
                            <p>Rating: ${movie.vote_average || "N/A"}</p>
                        </div>`
                )
                .join("");
        } else {
            resultsDiv.innerHTML = `<p>No results found for "${query}".</p>`;
        }
    } catch (error) {
        console.error("Error fetching search results:", error);
        document.getElementById("search-results").innerHTML = `
            <p>Error fetching search results: ${error.message}</p>
            <p>Check server logs for details.</p>
        `;
    }
});



// Movie Recommendations Form Handler
document.getElementById("recommendations-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const movieId = document.getElementById("movie-id").value;

    const response = await fetch(`/api/movie/${movieId}/recommendations`);
    const data = await response.json();

    const resultsDiv = document.getElementById("recommendations-results");
    if (data.recommendations) {
        resultsDiv.innerHTML = data.recommendations
            .map(
                (movie) =>
                    `<p>${movie.title} - ${movie.release_date}</p>`
            )
            .join("");
    } else {
        resultsDiv.innerText = data.error || "No recommendations found.";
    }
});
