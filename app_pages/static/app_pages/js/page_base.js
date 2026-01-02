document.addEventListener("DOMContentLoaded", function () {

    const toggle = document.getElementById("companyToggle");
    const dropdown = document.getElementById("companyDropdown");
    const deactivateBtn = document.getElementById("deactivateCompanyBtn");

    if (!toggle || !dropdown) return;

    // Toggle dropdown
    toggle.addEventListener("click", function (e) {
        e.stopPropagation();
        const open = dropdown.classList.toggle("show");
        toggle.setAttribute("aria-expanded", open);
    });

    // Outside click close
    document.addEventListener("click", function () {
        dropdown.classList.remove("show");
        toggle.setAttribute("aria-expanded", "false");
    });

    dropdown.addEventListener("click", e => e.stopPropagation());

    // Deactivate confirm
    if (deactivateBtn) {
        deactivateBtn.addEventListener("click", function () {
            if (!confirm("Deactivate this page? It will be hidden but not deleted.")) return;
            window.location.href = deactivateBtn.dataset.url;
        });
    }

});
