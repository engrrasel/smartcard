document.addEventListener("click", function (e) {

    // Copy link
    const copyBtn = e.target.closest(".copy-btn");
    if (copyBtn) {
        const url = copyBtn.dataset.url;
        navigator.clipboard.writeText(url);
        copyBtn.innerHTML = "✓";
        setTimeout(() => {
            copyBtn.innerHTML = '<i class="fa-solid fa-link"></i>';
        }, 1200);
    }

    // QR placeholder (modal hook)
    const qrBtn = e.target.closest(".qr-btn");
    if (qrBtn) {
        alert("QR URL:\n" + qrBtn.dataset.url);
    }

});
