// static/accounts/profile_card_responsive.js

document.addEventListener("DOMContentLoaded", function() {

    /* ========== SECTION TOGGLE ========== */
    const mainSection   = document.getElementById("mainSection");
    const childSection  = document.getElementById("childSection");
    const toggleMainBtn = document.getElementById("toggleMain");
    const toggleChildBtn= document.getElementById("toggleChild");

    if (toggleMainBtn && toggleChildBtn && mainSection && childSection) {

        toggleMainBtn.addEventListener("click", () => {
            mainSection.style.display = "block";
            childSection.style.display = "none";

            toggleMainBtn.classList.add("active");
            toggleChildBtn.classList.remove("active");
        });

        toggleChildBtn.addEventListener("click", () => {
            mainSection.style.display = "none";
            childSection.style.display = "block";

            toggleChildBtn.classList.add("active");
            toggleMainBtn.classList.remove("active");
        });
    }


    /* ========== COPY LINK BUTTONS ========== */
    document.querySelectorAll(".copy-btn").forEach(btn => {
        btn.addEventListener("click", function(e) {
            e.stopPropagation(); // card click block

            const url = this.dataset.url;
            if (!url) {
                alert("Link not found!");
                return;
            }

            // Modern API
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(url).then(() => {
                    showCopyToast();
                }).catch(err => {
                    console.error("Clipboard error:", err);
                    fallbackCopy(url);
                });
            } else {
                // Fallback for old browsers
                fallbackCopy(url);
            }
        });
    });

    function fallbackCopy(text) {
        const temp = document.createElement("textarea");
        temp.value = text;
        temp.style.position = "fixed";
        temp.style.left = "-9999px";
        document.body.appendChild(temp);
        temp.select();
        try {
            document.execCommand("copy");
            showCopyToast();
        } catch (err) {
            console.error("Fallback copy failed:", err);
            alert("Could not copy link");
        }
        document.body.removeChild(temp);
    }

    function showCopyToast() {
        const toast = document.createElement("div");
        toast.innerText = "🔗 Link copied!";
        toast.style.position = "fixed";
        toast.style.bottom = "25px";
        toast.style.right = "25px";
        toast.style.background = "#0d6efd";
        toast.style.color = "#fff";
        toast.style.padding = "8px 14px";
        toast.style.borderRadius = "6px";
        toast.style.fontSize = "14px";
        toast.style.fontWeight = "600";
        toast.style.boxShadow = "0 4px 10px rgba(0,0,0,.15)";
        toast.style.zIndex = "9999";

        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 1500);
    }


    /* ========== QR POPUP (যদি ব্যবহার করো) ========== */
    const qrModal    = document.getElementById("qrModal");
    const qrCloseBtn = document.getElementById("qrClose");
    const qrBox      = document.getElementById("qrContainer");
    const qrDownload = document.getElementById("qrDownloadPng");

    if (qrModal && qrCloseBtn && qrBox) {

        document.querySelectorAll(".qr-btn").forEach(btn => {
            btn.addEventListener("click", function(e) {
                e.stopPropagation();

                const url = this.dataset.url;
                if (!url) return;

                qrModal.style.display = "flex";
                qrBox.innerHTML = "";

                if (typeof QRCode !== "undefined") {
                    new QRCode(qrBox, {
                        text: url,
                        width: 220,
                        height: 220,
                        colorDark: "#000000",
                        colorLight: "#ffffff"
                    });
                } else {
                    qrBox.innerHTML = "<p>QRCode library missing!</p>";
                }
            });
        });

        qrCloseBtn.addEventListener("click", () => {
            qrModal.style.display = "none";
        });

        qrModal.addEventListener("click", (e) => {
            if (e.target === qrModal) {
                qrModal.style.display = "none";
            }
        });

        if (qrDownload) {
            qrDownload.addEventListener("click", () => {
                const canvas = qrBox.querySelector("canvas");
                if (!canvas) return;

                const link = document.createElement("a");
                link.download = "profile_qr.png";
                link.href = canvas.toDataURL();
                link.click();
            });
        }
    }

});
