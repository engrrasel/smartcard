document.addEventListener("DOMContentLoaded", () => {

    /*============ 📝 NOTE SYSTEM ============*/
    const modal=document.getElementById("noteModal");
    const newNote=document.getElementById("newNote");
    const saveBtn=document.getElementById("saveNoteBtn");
    const lastNoteText=document.getElementById("lastNoteText");
    let activeID=null;

    // ⭐ OPEN NOTE MODAL + LOAD LAST NOTE
    document.querySelectorAll(".contact-btn.note").forEach(btn=>{
        btn.addEventListener("click",(e)=>{
            e.stopPropagation();
            activeID=btn.dataset.id;
            modal.style.display="flex";
            newNote.value="";

            fetch(`/contacts/get-last-note/${activeID}/`)
            .then(r=>r.json())
            .then(d=>{
                lastNoteText.innerHTML = d.exists
                    ? `<b>${d.text}</b><br><small>${d.time}</small>`
                    : "No previous notes found";
            });
        });
    });

    // ⭐ SAVE NOTE + CLOSE POPUP
    saveBtn.addEventListener("click",()=>{
        let text=newNote.value.trim();
        if(!text) return Swal.fire("⚠ Write something first!");

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
                Swal.fire({
                    icon:"success",
                    title:"Note Saved!",
                    timer:900,
                    showConfirmButton:false,
                    willClose:()=>closeNote()
                });
                lastNoteText.innerHTML=`<b>${d.text}</b><br><small>${d.time}</small>`;
            }
        });
    });



    /*============ 📞 CALL BUTTON ============*/
    document.querySelectorAll(".contact-btn.call").forEach(btn=>{
        btn.onclick=e=>{
            e.stopPropagation();
            window.location=`tel:${btn.dataset.phone}`;
        };
    });

    /*============ ✉ EMAIL BUTTON ============*/
    document.querySelectorAll(".contact-btn.email").forEach(btn=>{
        btn.onclick=e=>{
            e.stopPropagation();
            window.location=`mailto:${btn.dataset.email}`;
        };
    });


    /*============ ❌ DELETE CONTACT ============*/
    document.querySelectorAll(".contact-btn.delete").forEach(btn=>{
        btn.onclick=e=>{
            e.stopPropagation();

            Swal.fire({
                title:"Delete Contact?",
                icon:"warning",
                showCancelButton:true,
                confirmButtonColor:"#d90429",
                confirmButtonText:"Delete"
            }).then(res=>{
                if(res.isConfirmed){
                    fetch(`/contacts/delete/${btn.dataset.id}/`,{
                        method:"DELETE",
                        headers:{ "X-CSRFToken":getCookie("csrftoken") }
                    })
                    .then(r=>r.json())
                    .then(d=>{
                        if(d.success) btn.closest(".contact-row").remove();
                    });
                }
            });
        };
    });


    // ===================== 🔍 ADVANCED LIVE SEARCH =====================
    const search=document.getElementById("searchBox");

    search?.addEventListener("input",()=>{
        let q=search.value.toLowerCase().trim();

        document.querySelectorAll(".contact-row").forEach(item=>{

            let name  = item.dataset.name ?? "";
            let email = item.dataset.email ?? "";
            let phone = item.dataset.phone ?? "";
            let addr  = item.dataset.address ?? "";
            let org   = item.dataset.org ?? "";

            let match = name.includes(q) || email.includes(q) || phone.includes(q)
                     || addr.includes(q) || org.includes(q);

            item.style.display = match ? "" : "none";
        });
    });

});


/*============ UTILITIES ============*/
function closeNote(){ document.getElementById("noteModal").style.display="none"; }
function getCookie(name){
    return document.cookie.split("; ").reduce((a,b)=>{
        let c=b.split("=");return c[0]==name?decodeURIComponent(c[1]):a;
    },"");
}
