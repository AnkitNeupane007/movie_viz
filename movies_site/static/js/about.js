const contributors = [
    { name: "Aaditya Joshi", contribution: "Data Cleaning and Analyzing" },
    { name: "Abhijeet KC", contribution: "Designed the UI and animations, Developed the backend system." },
    { name: "Ankit Neupane", contribution: "Integrated database and APIs." }
];

let currentIndex = 0;
const contributorContainer = document.getElementById("contributor");

function showContributor(index) {
    const contributorElement = document.createElement("div");
    contributorElement.className = "slide-in text-center";
    contributorElement.innerHTML = `
        <h3 class="text-xl font-semibold">${contributors[index].name}</h3>
        <p class="text-gray-700 mt-2">${contributors[index].contribution}</p>
    `;
    contributorContainer.appendChild(contributorElement);

    setTimeout(() => {
        if (contributorContainer.children.length > 1) {
            contributorContainer.children[0].classList.add("slide-out");
            setTimeout(() => contributorContainer.children[0].remove(), 1000);
        }
    }, 2000);
}

showContributor(currentIndex);
setInterval(() => {
    currentIndex = (currentIndex + 1) % contributors.length;
    showContributor(currentIndex);
}, 4000);