document.addEventListener("DOMContentLoaded", function () {
    let isDirty = false;
    const forms = document.querySelectorAll("form");
    forms.forEach(form => {
        form.addEventListener("input", () => {
            isDirty = true;
        });
        form.addEventListener("change", () => {
            isDirty = true;
        });
    });

    // browser close/refresh
    window.addEventListener("beforeunload", function (e) {
        if (!isDirty) return;
        e.preventDefault();
        e.returnValue = "";
    });

    // internal navigation
    document.querySelectorAll("a, button[type=button], input[type=submit]").forEach(el => {
        el.addEventListener("click", function (e) {
            if (!isDirty) return;
            const leave = confirm("You have unsaved changes.\nDiscard and leave or Continue editing?");
            if (!leave) e.preventDefault();
        });
    });
});