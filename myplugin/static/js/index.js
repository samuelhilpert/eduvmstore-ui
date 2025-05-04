document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll(".favorite-form").forEach(form => {
        form.addEventListener("submit", function () {
            let star = this.querySelector(".favorite-btn i");
            star.classList.add("temporary-favorite");

            setTimeout(() => {
                star.classList.remove("temporary-favorite");
            }, 1000);

        });
    });
});