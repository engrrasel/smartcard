console.log("📦 dynamic_formset.js loaded and running!");

function setupDynamicFormset(sectionId, addBtnId, formClass, removeBtnClass, prefix) {
    const container = document.getElementById(sectionId);
    const addBtn = document.getElementById(addBtnId);

    if (!container || !addBtn) return;

    addBtn.addEventListener("click", function () {
        const totalFormsInput = container.querySelector(`input[name="${prefix}-TOTAL_FORMS"]`);
        let totalForms = parseInt(totalFormsInput.value);
        const emptyForm = container.querySelector(`.${formClass}:last-child`);
        const newForm = emptyForm.cloneNode(true);

        // Clear previous input values
        newForm.querySelectorAll("input").forEach(input => input.value = "");

        // Replace form index numbers
        newForm.innerHTML = newForm.innerHTML.replace(
            new RegExp(`${prefix}-(\\d+)-`, "g"),
            `${prefix}-${totalForms}-`
        );

        totalFormsInput.value = totalForms + 1;
        container.appendChild(newForm);
    });

    container.addEventListener("click", function (e) {
        if (e.target.closest(`.${removeBtnClass}`)) {
            const forms = container.querySelectorAll(`.${formClass}`);
            if (forms.length > 1) e.target.closest(`.${formClass}`).remove();
        }
    });
}

// Initialize after DOM loaded
document.addEventListener("DOMContentLoaded", function () {
    setupDynamicFormset("phones-formset", "add-phone", "phone-form", "remove-phone", "phones");
    setupDynamicFormset("emails-formset", "add-email", "email-form", "remove-email", "emails");
    setupDynamicFormset("socials-formset", "add-social", "social-form", "remove-social", "socials");
});
