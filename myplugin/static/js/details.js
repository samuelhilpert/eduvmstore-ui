const dataDetails = window.templateContext || {};

document.addEventListener("DOMContentLoaded", function () {
    let accountAttributes = dataDetails.accountAttributes;
    let instantiationAttributes = dataDetails.instantiationAttributes;

    document.getElementById("structured-accounts").textContent =
        accountAttributes.length ? accountAttributes.map(acc => acc.name).join(": ") : "No account attributes available.";

    document.getElementById("structured-instantiation").textContent =
        instantiationAttributes.length ? instantiationAttributes.map(attr => attr.name).join(": ") : "No instantiation attributes available.";
});

let accountAttributes = dataDetails.accountAttributes;
let formattedAccounts = accountAttributes.map(acc => acc.name).join(":");
document.getElementById("formatted-accounts").textContent = formattedAccounts;
document.getElementById("structured-accounts").textContent = formattedAccounts;

let instantiationAttributes = dataDetails.instantiationAttributes;
let formattedInstatiation = instantiationAttributes.map(acc => acc.name).join(":");
document.getElementById("structured-instantiation").textContent = formattedInstatiation;
document.getElementById("instantiationContent").textContent = formattedInstatiation;