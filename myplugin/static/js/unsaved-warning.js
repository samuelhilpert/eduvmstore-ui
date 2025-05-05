/**
 * This script adds functionality to warn users about unsaved changes in forms.
 *
 * Features:
 * - Tracks changes in form inputs and marks the form as "dirty" when changes occur.
 * - Displays a browser warning when the user attempts to close or refresh the page with unsaved changes.
 * - Displays a confirmation dialog when the user clicks on internal navigation links or buttons, allowing them to discard changes or continue editing.
 * - Suppresses the warning during form submission or when navigating using elements with the `no-warning` class.
 *
 * Key Behaviors:
 * - `isDirty` flag tracks whether any form has unsaved changes.
 * - `beforeunload` event warns users about unsaved changes when leaving the page.
 * - Internal navigation elements (links, buttons) trigger a confirmation dialog if changes are unsaved.
 * - Form submission disables the `isDirty` flag to prevent warnings during redirects.
 */

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

        form.addEventListener("submit", () => {
            isDirty = false;
        });
    });

    let internalNavigation = false;

    window.addEventListener("beforeunload", function (e) {
        if (!isDirty || internalNavigation) return;
        e.preventDefault();
        e.returnValue = "";
    });

    document.querySelectorAll("a:not(.no-warning), button:not(.no-warning):not([type=submit]), input[type=submit]:not(.no-warning)").forEach(el => {
        el.addEventListener("click", function (e) {
            if (!isDirty) return;

            internalNavigation = true;

            const leave = confirm("You have unsaved changes.\nDiscard and leave or Continue editing?");
            if (!leave) {
                e.preventDefault();
                internalNavigation = false;
            }
        });
    });
});