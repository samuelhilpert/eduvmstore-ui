function openModal() {
    document.getElementById('scriptModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('scriptModal').style.display = 'none';
}

function copyToClipboard(elementId) {
    const codeElement = document.getElementById(elementId);
    const tempInput = document.createElement("textarea");
    tempInput.value = codeElement.textContent;
    document.body.appendChild(tempInput);
    tempInput.select();
    try {
        document.execCommand("copy");
    } catch (err) {
        console.error("Copy failed:", err);
    }
    document.body.removeChild(tempInput);
}

document.addEventListener("DOMContentLoaded", () => {
    const tocLinks = document.querySelectorAll(".toc a");
    tocLinks.forEach(link => {
        link.addEventListener("click", (event) => {
            const targetId = link.getAttribute("href").replace("#!", "");
            window.location.hash = targetId;
            event.preventDefault();
        });
    });
});