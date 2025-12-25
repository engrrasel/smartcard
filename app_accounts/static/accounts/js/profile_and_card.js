document.addEventListener("DOMContentLoaded", () => {

    /* ================= CARD CLICK → redirect ================= */
    document.querySelectorAll(".pc-card").forEach(card => {
        const url = card.dataset.url;
        if (!url) return;

        card.addEventListener("click", () => {
            window.location.href = url;
        });
    });

    /* ================= STOP REDIRECT FOR ICONS & TOGGLES ================= */
    document.querySelectorAll(".no-redirect, .no-redirect *").forEach(el => {
        el.addEventListener("click", e => e.stopPropagation());
    });

    /* ================= COPY LINK ================= */
    document.querySelectorAll(".copy-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();

            const text = btn.dataset.url;

            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(text)
                    .then(showCopied)
                    .catch(() => fallbackCopy(text));
            } else {
                fallbackCopy(text);
            }
        });
    });

    function fallbackCopy(text) {
        const temp = document.createElement("textarea");
        temp.value = text;
        temp.style.position = "fixed";
        temp.style.opacity = "0";
        document.body.appendChild(temp);
        temp.select();
        document.execCommand("copy");
        document.body.removeChild(temp);
        showCopied();
    }

    function showCopied() {
        const box = document.createElement("div");
        box.innerText = "Link Copied!";
        box.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #111;
            color: white;
            padding: 10px 16px;
            border-radius: 8px;
            z-index: 9999;
            font-size: 14px;
        `;
        document.body.appendChild(box);
        setTimeout(() => box.remove(), 1200);
    }

    /* ================= TAB SWITCH ================= */
    const mainBtn = document.getElementById("toggleMain");
    const childBtn = document.getElementById("toggleChild");
    const mainSection = document.getElementById("mainSection");
    const childSection = document.getElementById("childSection");

    function showMain(save = true){
        mainSection.style.display = "block";
        childSection.style.display = "none";
        mainBtn.classList.add("active");
        childBtn.classList.remove("active");
        if (save) localStorage.setItem("pc_active_section", "main");
    }

    function showChild(save = true){
        mainSection.style.display = "none";
        childSection.style.display = "block";
        childBtn.classList.add("active");
        mainBtn.classList.remove("active");
        if (save) localStorage.setItem("pc_active_section", "child");
    }

    mainBtn.addEventListener("click", () => showMain(true));
    childBtn.addEventListener("click", () => showChild(true));

    /* ================= INITIAL LOAD ================= */
    const savedTab = localStorage.getItem("pc_active_section");
    if (savedTab === "child") {
        showChild(false);
    } else {
        showMain(false);
    }

    /* ================= PUBLIC PROFILE TOGGLE (FIXED) ================= */
    document.querySelectorAll(".public-toggle").forEach(toggle => {
        toggle.addEventListener("click", e => {
            e.stopPropagation(); // 🔥 card redirect বন্ধ
        });

        toggle.addEventListener("change", () => {

            const profileId = toggle.dataset.id;
            const isPublic = toggle.checked;

            fetch(`/profile/toggle-public/${profileId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify({ is_public: isPublic })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status !== "success") {
                    toggle.checked = !isPublic;
                    alert("Failed to update public status");
                }
            })
            .catch(() => {
                toggle.checked = !isPublic;
                alert("Network error");
            });
        });
    });

});


/* ================= CSRF helper ================= */
function getCSRFToken() {
    return document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="))
        ?.split("=")[1];
}
