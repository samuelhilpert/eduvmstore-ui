document.addEventListener("DOMContentLoaded", function () {
    let items = document.querySelectorAll(".template-row");
    let itemsPerPage = 10;
    let currentItems = 0;

    function showNextItems() {
        console.log("Load More clicked!"); // Debugging log
        for (let i = currentItems; i < currentItems + itemsPerPage && i < items.length; i++) {
            items[i].style.display = "table-row";
        }
        currentItems += itemsPerPage;

        console.log(`Showing up to index: ${currentItems}, Total items: ${items.length}`);
    }

    showNextItems();
});
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".favorite-form").forEach(form => {
        form.addEventListener("submit", function () {
            let star = this.querySelector(".favorite-btn i");
            star.classList.add("temporary-favorite");

            setTimeout(() => {
                star.classList.remove("temporary-favorite");
            }, 1000);

        });
    });
});
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();

            let templateId = this.getAttribute("data-template-id");

            let authToken = localStorage.getItem("auth_token") || sessionStorage.getItem("auth_token");

            if (!authToken) {
                alert("Authentication token not found. Please log in again.");
                return;
            }

            let confirmDelete = confirm("Are you sure you want to delete this App-Template?");
            if (!confirmDelete) return;

            fetch(`/delete_template/${templateId}/`, {
                method: "DELETE",
                headers: {
                    "Authorization": `Bearer ${authToken}`,
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                }
            })
                .then(response => {
                    if (response.status === 204) {
                        alert("App-Template deleted successfully!");
                        location.reload();
                    } else {
                        return response.json().then(data => {
                            alert("Failed to delete: " + (data.error || response.status));
                        });
                    }
                })
                .catch(error => console.error("Error:", error));
        });
    });
    const searchInput = document.getElementById("search");
    const tableContainer = document.getElementById("table-container");

    searchInput.addEventListener("input", function () {
        const query = searchInput.value;

        fetch("{% url 'horizon:eduvmstore_dashboard:eduvmstore:index' %}?search="
            + encodeURIComponent(query), {
            headers: { "X-Requested-With": "XMLHttpRequest" }
        })
            .then(response => response.text())
            .then(data => {
                tableContainer.innerHTML = data;
            })
            .catch(error => console.error("Error fetching search results:", error));
    });


    // Function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            let cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});