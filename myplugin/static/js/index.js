document.addEventListener("DOMContentLoaded", function () {
    let items = document.querySelectorAll(".template-row");
    let itemsPerPage = 10;
    let currentItems = 0;

    function showNextItems() {
        for (let i = currentItems; i < currentItems + itemsPerPage && i < items.length; i++) {
            items[i].style.display = "table-row";
        }
        currentItems += itemsPerPage;
    }

    showNextItems();

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