// =========================
// DARK MODE
// =========================

const themeToggle = document.getElementById("themeToggle");

if (themeToggle) {

    // Load saved mode
    if (localStorage.getItem("darkMode") === "true") {
        document.body.classList.add("dark-mode");
    }

    themeToggle.addEventListener("click", () => {

        document.body.classList.toggle("dark-mode");

        localStorage.setItem(
            "darkMode",
            document.body.classList.contains("dark-mode")
        );

    });

}


// =========================
// SIDEBAR TOGGLE
// =========================

const sidebarToggle = document.getElementById("sidebarToggle");
const sidebar = document.querySelector(".sidebar");
const mainContent = document.querySelector(".main-content");

if (sidebarToggle && sidebar && mainContent) {

    sidebarToggle.addEventListener("click", () => {

        sidebar.classList.toggle("closed");
        mainContent.classList.toggle("expanded");

    });

}


// =========================
// PRODUCT / GROOMING FILTER
// =========================

const recordType = document.getElementById("recordType");
const productSelect = document.getElementById("productSelect");

if (recordType && productSelect) {

    const options = productSelect.querySelectorAll("option");

    recordType.addEventListener("change", function () {

        const selected = this.value;

        options.forEach(option => {

            if (option.value === "") {
                option.hidden = false;
                return;
            }

            const category = option.dataset.category;

            // SHOW ONLY GROOMING
            if (selected === "grooming") {

                option.hidden = category !== "grooming";

            }

            // SHOW ONLY PRODUCTS
            else if (selected === "product") {

                option.hidden = category === "grooming";

            }

            // SHOW ALL
            else {

                option.hidden = false;

            }

        });

        productSelect.value = "";

    });

}
