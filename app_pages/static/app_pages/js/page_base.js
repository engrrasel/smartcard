document.addEventListener("click", async function (e) {

    /* ========= COPY LINK ========= */
    const copyBtn = e.target.closest(".copy-btn");
    if (copyBtn) {
        const url = copyBtn.dataset.url;
        navigator.clipboard.writeText(url);

        copyBtn.innerHTML = "✓";
        setTimeout(() => {
            copyBtn.innerHTML = '<i class="fa-solid fa-link"></i>';
        }, 1200);
        return;
    }

    /* ========= QR DIRECT DOWNLOAD ========= */
    const qrBtn = e.target.closest(".qr-btn");
    if (qrBtn) {
        const pageUrl = encodeURIComponent(qrBtn.dataset.url);

        const qrApi =
            `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${pageUrl}`;

        try {
            const response = await fetch(qrApi);
            const blob = await response.blob();

            const blobUrl = URL.createObjectURL(blob);

            const a = document.createElement("a");
            a.href = blobUrl;
            a.download = "company-qr.png";
            document.body.appendChild(a);
            a.click();

            document.body.removeChild(a);
            URL.revokeObjectURL(blobUrl);

        } catch (err) {
            alert("QR download failed");
            console.error(err);
        }
    }

});
