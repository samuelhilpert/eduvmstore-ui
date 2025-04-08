document.addEventListener("DOMContentLoaded", function () {
    var scriptText = document.getElementById('scriptText').value;
    document.getElementById('hiddenScriptField').value = scriptText;
    document.querySelectorAll("input[type='text']").forEach(function(input) {
        input.value = input.value.replace(",", ".");
    });
});

document.getElementById('script_file').addEventListener('change', function(event) {
    var file = event.target.files[0];
    if (file) {
        var reader = new FileReader();

        reader.onload = function(e) {
            var fileContent = e.target.result;

            document.getElementById('hiddenScriptField').value = fileContent;

            document.getElementById('scriptText').value = fileContent;
        };

        reader.readAsText(file);
    }
});

function saveScript() {
    var scriptText = document.getElementById('scriptText').value;
    document.getElementById('hiddenScriptField').value = scriptText;

    closeModal();
}

let accountAttributes = {{ app_template.account_attributes|safe }};
let formattedAccounts = accountAttributes.map(acc => acc.name).join(":");
document.getElementById("account_attributes").value = formattedAccounts;

let instantiationAttributes = {{ app_template.instantiation_attributes|safe }};
let formattedInstatiation = instantiationAttributes.map(acc => acc.name).join(":");
document.getElementById("instantiation_attributes").value = formattedInstatiation;


function openModal() {
    let accountStructure = document.getElementById("account_attributes").value;
    let instantiationStructure = document.getElementById("instantiation_attributes").value;
    document.getElementById("accountContent").innerText = accountStructure;
    document.getElementById("instantiationContent").innerText = instantiationStructure;
    document.getElementById('scriptModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('scriptModal').style.display = 'none';
}




// Close the modal if the user clicks anywhere outside of it
window.onclick = function(event) {
    var modal = document.getElementById('scriptModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split("; ");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i];
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.split("=")[1]);
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie("csrftoken");


async function checkName() {
    const inputField = document.getElementById("name");
    const name = inputField.value;
    const url = inputField.dataset.url;
    const feedback = document.getElementById("name-feedback");
    const submitButton = document.getElementById("submit-button");


    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({ name: name })
        });

        if (!response.ok) {
            throw new Error(`HTTP-Fehler: ${response.status}`);
        }

        const result = await response.json();

        if (result.valid) {
            inputField.classList.remove("is-invalid");
            inputField.classList.add("is-valid");
            feedback.textContent = "Name available";
            feedback.style.color = "green";
            submitButton.disabled = false;
        } else {
            inputField.classList.remove("is-valid");
            inputField.classList.add("is-invalid");
            feedback.textContent = "Name already taken";
            feedback.style.color = "red";
            submitButton.disabled = true;
        }
    } catch (error) {
        console.error("Fehler bei der Validierung:", error);
    }
}
