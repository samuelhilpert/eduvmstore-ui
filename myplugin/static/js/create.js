$(document).ready(function() {
    $('[data-toggle="tooltip"]').tooltip();

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


function openModal() {
    let accountStructure = document.getElementById("account_attributes").value;
    let instantiationStructure = document.getElementById("instantiation_attributes").value;
    document.getElementById("accountContent").innerText = accountStructure;
    document.getElementById("instantiationContent").innerText = instantiationStructure;
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
    var scriptText = document.getElementById('scriptText').value;
    document.getElementById('hiddenScriptField').value = scriptText;
    closeModal();
}

function updateSelectedGroups() {
    const selectedGroups = [];
    const checkboxes = document.querySelectorAll('.dropdown-menu input[type="checkbox"]:checked');
    checkboxes.forEach(function(checkbox) {
        selectedGroups.push(checkbox.value);
    });

    if (selectedGroups.length === 0) {
        selectedGroups.push('default');
    }

    const selectedGroupsDisplay = document.querySelector('.selected-group');
    selectedGroupsDisplay.textContent = selectedGroups.join(", ");
}

document.querySelectorAll('.dropdown-menu input[type="checkbox"]').forEach(function(checkbox) {
    checkbox.addEventListener('change', updateSelectedGroups);
});

document.addEventListener('DOMContentLoaded', updateSelectedGroups);

document.addEventListener("DOMContentLoaded", function () {
    const textarea = document.getElementById("scriptText");
    const hiddenField = document.getElementById("hiddenScriptField");

    function updateScriptBasedOnSelection() {
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
                selectedKey = "sshscript_base_configuration";
                break;
            case "ssh_script+user_add":
                selectedKey = "ssh_script";
                break;
            case "base_configuration+user_add":
                selectedKey = "base_user";
                break;
            case "base_configuration+ssh_script+user_add":
                selectedKey = "sshscript_base_configuration";
                break;
            default:
                selectedKey = "";
        }

        if (selectedKey && scriptSnippets[selectedKey]) {
            const decoded = scriptSnippets[selectedKey]
                .replace(/\\r\\n/g, '\n')
                .replace(/\\"/g, '"');
            textarea.value = decoded;
            hiddenField.value = decoded;
        } else {
            textarea.value = "";
            hiddenField.value = "";
        }
    }

    document.querySelectorAll(".script-option").forEach((checkbox) => {
        checkbox.addEventListener("change", updateScriptBasedOnSelection);
    });

    var scriptText = textarea.value;
    hiddenField.value = scriptText;
    document.querySelectorAll("input[type='text']").forEach(function(input) {
        input.value = input.value.replace(",", ".");
    });
});

function updateSelectedGroupsDisplay() {
    const selected = [];
    $('input[name="security_groups"]:checked').each(function() {
        selected.push($(this).val());
    });

    const display = $('#selectedGroupsDisplay');
    display.empty();

    if (selected.length === 0) {
        display.append('<span class="text-muted">No group selected</span>');
    } else {
        selected.forEach(function(group) {
            display.append('<span>' + group + '</span>');
        });
    }
}
updateSelectedGroupsDisplay();

$('input[name="security_groups"]').change(function() {
    updateSelectedGroupsDisplay();
});

$(document).ready(function() {
    $('.dropdown-toggle').dropdown();
});

const dataCreate = window.templateContext || {};

if (dataCreate.accountAttributes) {
    const formattedAccountAttributes = dataCreate.accountAttributes.map(acc => acc.name).join(":");
    document.getElementById("account_attributes").value = formattedAccountAttributes;
}

if (dataCreate.instantiationAttributes) {
    const formattedInstantiationAttributes = dataCreate.instantiationAttributes.map(acc => acc.name).join(":");
    document.getElementById("instantiation_attributes").value = formattedInstantiationAttributes;
}