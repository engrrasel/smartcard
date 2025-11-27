function filterContacts() {
    let q = document.getElementById('contactSearch').value.toLowerCase();
    let cards = document.getElementsByClassName('contact-item');

    for (let i = 0; i < cards.length; i++) {
        let text = cards[i].innerText.toLowerCase();
        cards[i].style.display = text.includes(q) ? "" : "none";
    }
}


function deleteContact(id){
    Swal.fire({
        title: "Are you sure?",
        text: "This will remove the contact permanently.",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#6c757d",
        confirmButtonText: "Delete"
    }).then((result) => {
        if (result.isConfirmed) {

            fetch(`/contacts/delete/${id}/`)
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    document.getElementById(`contact-${id}`).remove();
                    Swal.fire("Deleted!", "Contact removed.", "success");
                }
            });
        }
    });
}
