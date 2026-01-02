document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("id_logo");
    const preview = document.getElementById("logoPreview");

    if (!input || !preview) return;

    input.addEventListener("change", function () {
        const file = this.files[0];
        if (file && file.type.startsWith("image/")) {
            preview.src = URL.createObjectURL(file);
        }
    });
});
