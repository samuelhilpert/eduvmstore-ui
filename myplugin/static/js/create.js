document.addEventListener("DOMContentLoaded", function () {
    const data = window.templateContext || {};

    // Name-Validierung nur bei Create
    if (!data.isEdit) {
        checkName(data.nameValidationUrl, data.csrfToken);
    } else {
        document.getElementById("name-feedback").textContent = "";
        document.getElementById("submit-button").disabled = false;
    }

    // Fülle account_attributes und instantiation_attributes
    if (data.accountAttributes) {
        const formatted = data.accountAttributes.map(acc => acc.name).join(":");
        document.getElementById("account_attributes").value = formatted;
    }

    if (data.instantiationAttributes) {
        const formatted = data.instantiationAttributes.map(acc => acc.name).join(":");
        document.getElementById("instantiation_attributes").value = formatted;
    }

    // Fülle hidden script field
    const scriptText = document.getElementById('scriptText');
    if (scriptText) {
        document.getElementById('hiddenScriptField').value = scriptText.value;
    }

    // Zahlenformat angleichen
    document.querySelectorAll("input[type='text']").forEach(function (input) {
        input.value = input.value.replace(",", ".");
    });

    $('[data-toggle="tooltip"]').tooltip();

    // Initialisiere Dropdown-Auswahl
    updateSelectedGroupsDisplay();
    $('input[name="security_groups"]').change(updateSelectedGroupsDisplay);

    // Datei-Upload
    document.getElementById('script_file').addEventListener('change', function (event) {
        const file = event.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = function (e) {
            const content = e.target.result;
            document.getElementById('hiddenScriptField').value = content;
            document.getElementById('scriptText').value = content;
        };
        reader.readAsText(file);
    });

    // Cloudinit Snippet Auswahl
    document.querySelectorAll(".script-option").forEach((checkbox) => {
        checkbox.addEventListener("change", updateScriptBasedOnSelection);
    });

    // Bootstrap Dropdown
    $('.dropdown-toggle').dropdown();

    // Modal ggf. anzeigen
    if (data.showModal) {
        $('#responseModal').modal('show');
    }
});

function openModal() {
    const acc = document.getElementById("account_attributes").value;
    const inst = document.getElementById("instantiation_attributes").value;
    document.getElementById("accountContent").innerText = acc;
    document.getElementById("instantiationContent").innerText = inst;
    document.getElementById('scriptModal').style.display = 'block';

    setTimeout(function () {
        const preElement = document.querySelector("#scriptModal pre");
        const infoBox = document.querySelector("#scriptModal .cloudinit-info");
        if (preElement && infoBox) {
            infoBox.style.height = preElement.offsetHeight + "px";
        }
    }, 0);
}

function closeModal() {
    document.getElementById('scriptModal').style.display = 'none';
}

function saveScript() {
    const script = document.getElementById('scriptText').value;
    document.getElementById('hiddenScriptField').value = script;
    closeModal();
}

function updateSelectedGroupsDisplay() {
    const selected = [];
    $('input[name="security_groups"]:checked').each(function () {
        selected.push($(this).val());
    });

    const display = $('#selectedGroupsDisplay');
    display.empty();

    if (selected.length === 0) {
        display.append('<span class="text-muted">No group selected</span>');
    } else {
        selected.forEach(function (group) {
            display.append('<span>' + group + '</span>');
        });
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

async function checkName(url, csrftoken) {
    const inputField = document.getElementById("name");
    const feedback = document.getElementById("name-feedback");
    const submitButton = document.getElementById("submit-button");

    const name = inputField.value;
    const validPattern = /^[a-zA-Z0-9_\- ]+$/;

    if (!validPattern.test(name)) {
        inputField.classList.remove("is-valid");
        inputField.classList.add("is-invalid");
        feedback.textContent = "Invalid input: Only letters, numbers, '-', '_' and spaces are allowed.";
        feedback.style.color = "red";
        submitButton.disabled = true;
        return;
    }

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({ name: name })
        });

        if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
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
            feedback.textContent = result.reason || "Name already taken";
            feedback.style.color = "red";
            submitButton.disabled = true;
        }
    } catch (err) {
        console.error("Validation error:", err);
    }
}

function updateScriptBasedOnSelection() {
    const textarea = document.getElementById("scriptText");
    const hiddenField = document.getElementById("hiddenScriptField");

    const selected = Array.from(document.querySelectorAll(".script-option"))
        .filter(cb => cb.checked)
        .map(cb => cb.dataset.key)
        .sort();

    const keyCombo = selected.join("+");
    let selectedKey = "";

    switch (keyCombo) {
        case "base_configuration":
            selectedKey = "base_configuration";
            break;
        case "ssh_script":
            selectedKey = "ssh_script";
            break;
        case "user_add":
            selectedKey = "user_add";
            break;
        case "base_configuration+ssh_script":
        case "base_configuration+ssh_script+user_add":
            selectedKey = "sshscript_base_configuration";
            break;
        case "base_configuration+user_add":
            selectedKey = "base_user";
            break;
        case "ssh_script+user_add":
            selectedKey = "ssh_script";
            break;
        default:
            selectedKey = "";
    }

    if (selectedKey && window.scriptSnippets && window.scriptSnippets[selectedKey]) {
        const decoded = window.scriptSnippets[selectedKey]
            .replace(/\\r\\n/g, '\n')
            .replace(/\\"/g, '"');
        textarea.value = decoded;
        hiddenField.value = decoded;
    } else {
        textarea.value = "";
        hiddenField.value = "";
    }
}
