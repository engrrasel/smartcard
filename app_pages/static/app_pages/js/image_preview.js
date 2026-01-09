document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("id_logo");
    const previewImage = document.getElementById("previewImage");

    if (!fileInput || !previewImage) return;

    fileInput.addEventListener("change", function () {
        const file = this.files[0];
        if (file && file.type.startsWith("image/")) {
            previewImage.src = URL.createObjectURL(file);
        }
    });
});
