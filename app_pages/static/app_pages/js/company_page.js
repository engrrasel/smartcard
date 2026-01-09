document.addEventListener("DOMContentLoaded", () => {

    /* =========================
       ELEMENTS
    ========================= */
    const modal = document.getElementById("qrModal");
    const modalImg = document.getElementById("qrModalImage");
    const closeBtn = document.querySelector(".qr-close");
    const downloadBtn = document.getElementById("qrDownloadBtn");

    let currentQrUrl = null;

    /* =========================
       QR BUTTON CLICK
    ========================= */
    document.querySelectorAll(".qr-btn").forEach(btn => {
        btn.addEventListener("click", () => {

            const url = btn.dataset.url;
            if (!url) return;

            currentQrUrl = url;

            const qrApi =
                `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(url)}`;

            /* 👉 AUTO DOWNLOAD */
            autoDownload(qrApi);

            /* 👉 SHOW MODAL */
            if (modal && modalImg) {
                modalImg.src = qrApi;
                modal.style.display = "flex";
            }
        });
    });

    /* =========================
       CLOSE MODAL
    ========================= */
    if (closeBtn && modal) {
        closeBtn.addEventListener("click", () => {
            modal.style.display = "none";
            modalImg.src = "";
            currentQrUrl = null;
        });
    }

    /* =========================
       DOWNLOAD AGAIN BUTTON
    ========================= */
    if (downloadBtn) {
        downloadBtn.addEventListener("click", () => {
            if (!currentQrUrl) return;

            const qrApi =
                `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(currentQrUrl)}`;

            autoDownload(qrApi);
        });
    }

    /* =========================
       COPY BUTTON
    ========================= */
    document.querySelectorAll(".copy-btn").forEach(btn => {
        btn.addEventListener("click", () => {

            const url = btn.dataset.url;
            if (!url) return;

            const icon = btn.querySelector("i");
            const originalClass = icon.className;

            const success = () => {
                btn.classList.add("copied");
                icon.className = "fa-solid fa-check";

                setTimeout(() => {
                    btn.classList.remove("copied");
                    icon.className = originalClass;
                }, 1200);
            };

            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(url)
                    .then(success)
                    .catch(() => fallbackCopy(url, success));
            } else {
                fallbackCopy(url, success);
            }
        });
    });

    /* =========================
       HELPERS
    ========================= */
async function autoDownload(qrUrl) {
    try {
        const response = await fetch(qrUrl);
        const blob = await response.blob();

        const blobUrl = window.URL.createObjectURL(blob);

        const link = document.createElement("a");
        link.href = blobUrl;
        link.download = `company-qr-${Date.now()}.png`;

        document.body.appendChild(link);
        link.click();

        document.body.removeChild(link);
        window.URL.revokeObjectURL(blobUrl);

    } catch (err) {
        console.error("QR download failed", err);
        alert("QR download failed. Please try again.");
    }
}


    function fallbackCopy(text, callback) {
        const input = document.createElement("input");
        input.value = text;
        document.body.appendChild(input);
        input.select();
        document.execCommand("copy");
        document.body.removeChild(input);
        callback();
    }

});
