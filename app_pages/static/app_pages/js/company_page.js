document.addEventListener("DOMContentLoaded", () => {

    const modal = document.getElementById("qrModal");
    const modalImg = document.getElementById("qrModalImage");
    const closeBtn = document.querySelector(".qr-close");
    const downloadBtn = document.getElementById("qrDownloadBtn");

    let currentQrUrl = "";

    // QR button click
    document.querySelectorAll(".qr-btn").forEach(btn => {
        btn.addEventListener("click", () => {

            const pageUrl = btn.dataset.url;
            currentQrUrl = pageUrl;

            const qrApi =
                `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(pageUrl)}`;

            modalImg.src = qrApi;
            modal.style.display = "flex";
        });
    });

    // Close modal
    closeBtn.addEventListener("click", () => {
        modal.style.display = "none";
    });

    // ✅ IMPORTANT: remove previous listener before adding
    downloadBtn.onclick = () => {
        if (!currentQrUrl) return;

        const link = document.createElement("a");
        link.href =
            `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(currentQrUrl)}`;
        link.download = "company-qr.png";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };
});
