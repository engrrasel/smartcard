/********************************************
 * ALL FIXED - Delete + Notes Working
 ********************************************/

document.addEventListener("DOMContentLoaded", () => {

    /* ===================== 📒 NOTE OPEN ===================== */
    const modal = document.getElementById("noteModal");
    const newNote = document.getElementById("newNote");
    const saveBtn = document.getElementById("saveNoteBtn");
    const lastNoteText = document.getElementById("lastNoteText");
    let activeID = null;

    // OPEN notes
    document.querySelectorAll(".contact-btn.note").forEach(btn=>{
        btn.addEventListener("click",(e)=>{
            e.stopPropagation();
            activeID = btn.dataset.id;
            modal.style.display = "flex";

            fetch(`/contacts/get-last-note/${activeID}/`)
            .then(r=>r.json())
            .then(d=>{
                lastNoteText.innerHTML = d.exists
                    ? `<b>${d.text}</b><br><small>${d.time}</small>`
                    : "No previous notes found";
            });
        });
    });

    /* ===================== ✖ NOTE CLOSE (WORKING NOW) ===================== */
    document.getElementById("closeNoteBtn")?.addEventListener("click",()=>{
        modal.style.display = "none";
    });


    /* ===================== 💾 NOTE SAVE ===================== */
    saveBtn?.addEventListener("click",()=>{
        let text=newNote.value.trim();
        if(!text) return alert("Write something first!");

        fetch(`/contacts/save-note/${activeID}/`,{
            method:"POST",
            headers:{
                "X-CSRFToken":getCookie("csrftoken"),
                "Content-Type":"application/x-www-form-urlencoded"
            },
            body:`text=${encodeURIComponent(text)}`
        })
        .then(r=>r.json())
        .then(d=>{
            if(d.success){
                lastNoteText.innerHTML = `<b>${d.text}</b><br><small>${d.time}</small>`;
                modal.style.display="none";
            }
        });
    });



    /* ===================== ❌ DELETE CONTACT (FULL WORKING) ===================== */
    document.addEventListener("click", function(e){

        const btn = e.target.closest(".contact-btn.delete");
        if(!btn) return;

        let id = btn.dataset.id;

        Swal.fire({
            title:"Delete?",
            icon:"warning",
            showCancelButton:true,
            confirmButtonColor:"#d90429",
            confirmButtonText:"Delete"
        }).then(res=>{
            if(res.isConfirmed){

                fetch(`/contacts/delete/${id}/`,{
                    method:"POST",
                    headers:{ "X-CSRFToken":getCookie("csrftoken") }
                })
                .then(r=>r.json())
                .then(data=>{
                    if(data.success){
                        btn.closest(".contact-row").remove(); // NOW WORKS 🔥
                        Swal.fire("Removed","Contact deleted","success");
                    }
                })
            }
        });
    });

});


/* ===================== CSRF ===================== */
function getCookie(name){
    return document.cookie.split("; ").reduce((a,b)=>{
        let c=b.split("="); return c[0]==name?decodeURIComponent(c[1]):a;
    },"");
}
