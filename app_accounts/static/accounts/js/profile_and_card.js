document.addEventListener("DOMContentLoaded", () => {

    /* CARD CLICK → redirect */
    document.querySelectorAll(".pc-card").forEach(card => {
        const url = card.dataset.url;
        if (!url) return;

        card.addEventListener("click", () => {
            window.location.href = url;
        });
    });

    /* stop redirect for icons */
    document.querySelectorAll(".no-redirect, .no-redirect *").forEach(el => {
        el.addEventListener("click", e => e.stopPropagation());
    });

    /* PUBLIC TOGGLE */
    document.querySelectorAll(".public-toggle").forEach(toggle => {
        toggle.addEventListener("change", function () {

            const profileId = this.dataset.id;
            const newState = this.checked;

            fetch(`/toggle-public/${profileId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({ is_public: newState })
            })
            .then(r => r.json())
            .then(data => {
                if (data.status !== "success") {
                    this.checked = !newState;
                    alert("Failed to update visibility");
                }
            })
            .catch(() => {
                this.checked = !newState;
                alert("Network error");
            });
        });
    });

    /* COPY LINK */
    document.querySelectorAll(".copy-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            navigator.clipboard.writeText(btn.dataset.url);
            showCopied();
        });
    });

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
        `;
        document.body.appendChild(box);
        setTimeout(() => box.remove(), 1200);
    }

    /* TAB SWITCH */
    const mainBtn = document.getElementById("toggleMain");
    const childBtn = document.getElementById("toggleChild");
    const mainSection = document.getElementById("mainSection");
    const childSection = document.getElementById("childSection");

    mainBtn.addEventListener("click", () => {
        mainSection.style.display = "block";
        childSection.style.display = "none";
        mainBtn.classList.add("active");
        childBtn.classList.remove("active");
    });

    childBtn.addEventListener("click", () => {
        mainSection.style.display = "none";
        childSection.style.display = "block";
        childBtn.classList.add("active");
        mainBtn.classList.remove("active");
    });

    function getCookie(name) {
        let v = null;
        document.cookie.split(";").forEach(c => {
            c = c.trim();
            if (c.startsWith(name + "=")) {
                v = decodeURIComponent(c.slice(name.length + 1));
            }
        });
        return v;
    }

});
