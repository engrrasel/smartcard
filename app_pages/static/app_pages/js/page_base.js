document.addEventListener("DOMContentLoaded", () => {

    const toggleBtn = document.getElementById("companyToggle");
    const dropdown = document.getElementById("companyDropdown");

    // Guard: এই পেজে company switcher না থাকলে
    if (!toggleBtn || !dropdown) return;

    // Toggle dropdown
    toggleBtn.addEventListener("click", (e) => {
        e.stopPropagation();               // 🔴 সবচেয়ে গুরুত্বপূর্ণ
        dropdown.classList.toggle("show");
    });

    // Click outside → close
    document.addEventListener("click", () => {
        dropdown.classList.remove("show");
    });
});
