document.addEventListener("DOMContentLoaded", function () {
    checkName();
    var scriptText = document.getElementById('scriptText').value;
    document.getElementById('hiddenScriptField').value = scriptText;
    document.querySelectorAll("input[type='text']").forEach(function(input) {
        input.value = input.value.replace(",", ".");
    });
});

let accountAttributes = window.appTemplateData.accountAttributes || [];
let formattedAccounts = accountAttributes.map(acc => acc.name).join(":");
document.getElementById("account_attributes").value = formattedAccounts;

let instantiationAttributes = window.appTemplateData.instantiationAttributes || [];
let formattedInstantiation = instantiationAttributes.map(acc => acc.name).join(":");
document.getElementById("instantiation_attributes").value = formattedInstantiation;

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
}

function closeModal() {
    document.getElementById('scriptModal').style.display = 'none';
}

function saveScript() {
    // Get the script text from the textarea
    var scriptText = document.getElementById('scriptText').value;
    // Store it in the hidden input field
    document.getElementById('hiddenScriptField').value = scriptText;
    // Close the modal
    closeModal();
}



// Close the modal if the user clicks anywhere outside of it
window.onclick = function(event) {
    var modal = document.getElementById('scriptModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}
// Automatically show the modal if modal_message is set
{% if modal_message %}
$(document).ready(function() {
    $('#responseModal').modal('show');
});
{% endif %}

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

    const validPattern = /^[a-zA-Z0-9_\- ]+$/;

    if (!validPattern.test(name)) {
        inputField.classList.remove("is-valid");
        inputField.classList.add("is-invalid");
        feedback.textContent = "`Invalid input: Only letters (a-z, A-Z), numbers (0-9)," +
            " underscores (_), hyphens (-), and spaces are allowed.`";
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
            feedback.textContent = result.reason || "Name already taken";
            feedback.style.color = "red";
            submitButton.disabled = true;
        }
    } catch (error) {
        console.error("Fehler bei der Validierung:", error);
    }
}

function toggleSshScript(checkbox) {
    const sshScript = `
runcmd:
  - |
    # Create directory for private keys
    mkdir -p /home/ubuntu/user_keys
    chmod 700 /home/ubuntu/user_keys
    chown ubuntu:ubuntu /home/ubuntu/user_keys

    while IFS=: read -r username password; do
      # Create users
      if ! id "$username" &>/dev/null; then
        useradd -m -s /bin/bash "$username"
        echo "$username:$password" | chpasswd
      fi

      # Create SSH directory and key
      sudo -u "$username" mkdir -p /home/"$username"/.ssh
      chmod 700 /home/"$username"/.ssh

      # Generate SSH key
      sudo -u "$username" ssh-keygen -t rsa -b 2048 -f /home/"$username"/.ssh/id_rsa -N ""

      # Set Public Key as authorized_key
      cat /home/"$username"/.ssh/id_rsa.pub >> /home/"$username"/.ssh/authorized_keys
      chmod 600 /home/"$username"/.ssh/authorized_keys
      chown -R "$username:$username" /home/"$username"/.ssh

      # Secure private keys for the admin & Ubuntu user
      cp /home/"$username"/.ssh/id_rsa /home/ubuntu/user_keys/"$username"_id_rsa
      chmod 600 /home/ubuntu/user_keys/"$username"_id_rsa
      chown ubuntu:ubuntu /home/ubuntu/user_keys/"$username"_id_rsa
    done < /etc/users.txt

    # SSH configuration: Disable password login
    sed -i 's/^#\\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
    sed -i 's/^#\\?PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
    systemctl restart ssh`;

    if (checkbox.checked) {
        document.getElementById('scriptText').value = sshScript.trim();
        document.getElementById('hiddenScriptField').value = sshScript.trim();
    } else {
        document.getElementById('scriptText').value = '';
        document.getElementById('hiddenScriptField').value = '';
    }
}
