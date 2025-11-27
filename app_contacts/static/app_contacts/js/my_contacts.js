document.addEventListener("DOMContentLoaded", () => {

    /* ============================
       🔍 Live Search
    ============================ */
    const searchBox = document.getElementById("searchBox");
    searchBox?.addEventListener("input", () => {
        const q = searchBox.value.toLowerCase();
        document.querySelectorAll(".contact-row").forEach(row => {
            row.style.display = row.dataset.name.includes(q) ? "" : "none";
        });
    });


    /* ============================
       📝 NOTE OPEN MODAL
    ============================ */
    const noteModal = document.getElementById("noteModal");
    let selectedContactID = null;

    document.querySelectorAll(".contact-btn.note").forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            selectedContactID = btn.dataset.id;
            noteModal.style.display = "flex";   // Modal Show
        });
    });


    /* ============================
       📝 NOTE SAVE (AJAX + NO RELOAD)
    ============================ */
    document.getElementById("saveNoteBtn").onclick = () => {
        const text = document.getElementById("newNote").value;
        if(!text.trim()) return Swal.fire("Write something first ⚠");

        fetch(`/contacts/note/save/${selectedContactID}/`,{
            method:"POST",
            headers:{
                "X-CSRFToken": getCookie("csrftoken"),
                "Content-Type":"application/x-www-form-urlencoded"
            },
            body:`text=${encodeURIComponent(text)}`
        })
        .then(r=>r.json())
        .then(data=>{
            if(data.success){
                document.getElementById("lastNoteText").innerText = data.text;
                closeNote();   // Modal Close
                Swal.fire("Saved! 🔥","Note stored successfully","success");
            }
        });
    };


    /* ============================
       ❌ DELETE CONTACT (AJAX)
    ============================ */
    document.querySelectorAll(".contact-btn.delete").forEach(btn=>{
        btn.addEventListener("click", (e)=>{
            e.stopPropagation();
            const id = btn.dataset.id;

            Swal.fire({
                title: "Delete Contact?",
                text: "This action cannot be undone!",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#d90429",
                confirmButtonText: "Delete"
            }).then(result=>{
                if(result.isConfirmed){

                    fetch(`/contacts/delete/${id}/`,{
                        method:"DELETE",
                        headers:{ "X-CSRFToken": getCookie("csrftoken") }
                    })
                    .then(r=>r.json())
                    .then(data=>{
                        if(data.success){
                            let card = btn.closest(".contact-row");
                            card.style.opacity="0";
                            setTimeout(()=>card.remove(),300);
                        }
                    });

                }
            });
        });
    });


    /* ============================
       📞 CALL + ✉ EMAIL ACTION
    ============================ */
    document.querySelectorAll(".contact-btn.call").forEach(btn=>{
        btn.onclick = (e)=>{ e.stopPropagation(); window.location=`tel:${btn.dataset.phone}` }
    });
    document.querySelectorAll(".contact-btn.email").forEach(btn=>{
        btn.onclick = (e)=>{ e.stopPropagation(); window.location=`mailto:${btn.dataset.email}` }
    });


});


/* ============================
   MODAL CLOSE FUNCTION
============================ */
function closeNote(){
    document.getElementById("noteModal").style.display="none";
    document.getElementById("newNote").value="";
}

/* ============================
   CSRF TOKEN GETTER
============================ */
function getCookie(name){
    return document.cookie.split("; ").reduce((a,b)=>{
        const c=b.split("="); return c[0]==name?c[1]:a;
    },"");
}
