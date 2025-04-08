document.addEventListener("DOMContentLoaded", function () {
    let accountAttributes = {{ app_template.account_attributes|default:"[]"|safe }};
    let instantiationAttributes = {{ app_template.instantiation_attributes|default:"[]"|safe }};

    document.getElementById("structured-accounts").textContent =
        accountAttributes.length ? accountAttributes.map(acc => acc.name).join(": ") : "No account attributes available.";

    document.getElementById("structured-instantiation").textContent =
        instantiationAttributes.length ? instantiationAttributes.map(attr => attr.name).join(": ") : "No instantiation attributes available.";
});

let accountAttributes = {{ app_template.account_attributes|safe }};
let formattedAccounts = accountAttributes.map(acc => acc.name).join(":");
document.getElementById("formatted-accounts").textContent = formattedAccounts;
document.getElementById("structured-accounts").textContent = formattedAccounts;

let instantiationAttributes = {{ app_template.instantiation_attributes|safe }};
let formattedInstatiation = instantiationAttributes.map(acc => acc.name).join(":");
document.getElementById("structured-instantiation").textContent = formattedInstatiation;
document.getElementById("instantiationContent").textContent = formattedInstatiation;

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