function copyToClipboard(elementId) {
    const codeElement = document.getElementById(elementId);
    const tempInput = document.createElement("textarea");
    tempInput.value = codeElement.textContent;
    document.body.appendChild(tempInput);
    tempInput.select();
    try {
        document.execCommand("copy");
    } catch (err) {
        console.log("Copy failed:", err);
    }
    document.body.removeChild(tempInput);

}