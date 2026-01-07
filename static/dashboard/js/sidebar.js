document.addEventListener("DOMContentLoaded", () => {

    const sidebar = document.getElementById("sidebar");
    const main = document.getElementById("main");
    const toggle = document.getElementById("toggleBtn");

    const isMobile = () => window.innerWidth <= 991;

    // Restore desktop state
    if (!isMobile() && localStorage.getItem("sidebarCollapsed") === "true") {
        sidebar.classList.add("collapsed");
        main.classList.add("collapsed");
    }

    toggle.addEventListener("click", (e) => {
        e.stopPropagation();

        if (isMobile()) {
            sidebar.classList.toggle("open");
        } else {
            sidebar.classList.toggle("collapsed");
            main.classList.toggle("collapsed");

            localStorage.setItem(
                "sidebarCollapsed",
                sidebar.classList.contains("collapsed")
            );
        }
    });

    // Mobile outside click close
    document.addEventListener("click", (e) => {
        if (
            isMobile() &&
            sidebar.classList.contains("open") &&
            !sidebar.contains(e.target) &&
            e.target !== toggle
        ) {
            sidebar.classList.remove("open");
        }
    });
});
