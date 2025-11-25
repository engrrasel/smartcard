document.getElementById("toggleMain").onclick = () => {
    document.getElementById("mainSection").style.display = "block";
    document.getElementById("childSection").style.display = "none";
};

document.getElementById("toggleChild").onclick = () => {
    document.getElementById("mainSection").style.display = "none";
    document.getElementById("childSection").style.display = "block";
};

function toggleCopyMenu(id) {
    let menu = document.getElementById(id);
    document.querySelectorAll(".copy-menu").forEach(m => {
        if (m !== menu) m.style.display = "none";
    });
    menu.style.display = (menu.style.display === "block") ? "none" : "block";
}

function copyAndHide(text, id) {
    navigator.clipboard.writeText(text);
    document.getElementById(id).style.display = "none";
}

document.addEventListener("click", function (e) {
    document.querySelectorAll(".copy-menu").forEach(menu => {
        if (!menu.contains(e.target) && !e.target.closest(".icon-btn")) {
            menu.style.display = "none";
        }
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie) {
        document.cookie.split(';').forEach(cookie => {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = cookie.substring(name.length + 1);
            }
        });
    }
    return cookieValue;
}

document.querySelectorAll(".toggle-switch").forEach(toggle => {
    toggle.addEventListener("change", function () {
        fetch(`/toggle-public/${this.dataset.id}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
            }
        });
    });
});
