document.addEventListener("DOMContentLoaded", () => {

    const modal = document.getElementById("qrModal");
    const modalImg = document.getElementById("qrModalImage");
    const closeBtn = document.querySelector(".qr-close");
    const downloadBtn = document.getElementById("qrDownloadBtn");

    // 👉 Guard: যদি এই পেজে modal না থাকে
    if (!modal || !modalImg || !closeBtn || !downloadBtn) {
        return;
    }

    let currentQrUrl = null;

    /* =========================
       QR BUTTON CLICK
    ========================= */
    document.querySelectorAll(".qr-btn").forEach(btn => {
        btn.addEventListener("click", () => {

            const pageUrl = btn.dataset.url;
            if (!pageUrl) return;

            currentQrUrl = pageUrl;

            const qrApi =
                `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(pageUrl)}`;

            modalImg.src = qrApi;
            modal.style.display = "flex";
        });
    });

    /* =========================
       CLOSE MODAL
    ========================= */
    closeBtn.addEventListener("click", () => {
        modal.style.display = "none";
        modalImg.src = "";
        currentQrUrl = null;
    });

    /* =========================
       DOWNLOAD BUTTON
    ========================= */
    downloadBtn.onclick = () => {
        if (!currentQrUrl) return;

        const qrApi =
            `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(currentQrUrl)}`;

        const link = document.createElement("a");
        link.href = qrApi;
        link.download = "company-qr.png";

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

});
