document.addEventListener("DOMContentLoaded", function () {
    let isDirty = false;
    const forms = document.querySelectorAll("form");

    // Track form changes
    forms.forEach(form => {
        form.addEventListener("input", () => {
            isDirty = true;
        });
        form.addEventListener("change", () => {
            isDirty = true;
        });

        // Prevent beforeunload during form submission
        form.addEventListener("submit", () => {
            isDirty = false;
        });
    });

    // Suppress `beforeunload` if internal navigation is detected
    let internalNavigation = false;

    // Browser close/refresh warning
    window.addEventListener("beforeunload", function (e) {
        if (!isDirty || internalNavigation) return;
        e.preventDefault();
        e.returnValue = ""; // Required for some browsers
    });

    // Internal navigation warning
    document.querySelectorAll("a:not(.no-warning), button:not(.no-warning):not([type=submit]), input[type=submit]:not(.no-warning)").forEach(el => {
        el.addEventListener("click", function (e) {
            if (!isDirty) return;

            // Mark as internal navigation to suppress `beforeunload`
            internalNavigation = true;

            const leave = confirm("You have unsaved changes.\nDiscard and leave or Continue editing?");
            if (!leave) {
                e.preventDefault();
                internalNavigation = false; // Reset if user cancels
            }
        });
    });
});