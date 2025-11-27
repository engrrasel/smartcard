document.addEventListener("DOMContentLoaded", () => {

    /*============ 🔍 LIVE SEARCH ============*/
    const searchBox=document.getElementById("searchBox");
    if(searchBox){
        searchBox.addEventListener("input",()=>{
            const q=searchBox.value.toLowerCase();
            document.querySelectorAll(".contact-row").forEach(row=>{
                row.style.display=row.dataset.name.includes(q)?"":"none";
            });
        });
    }


    /*============ 📝 NOTE SYSTEM ============*/
    const modal=document.getElementById("noteModal");
    const newNote=document.getElementById("newNote");
    const saveBtn=document.getElementById("saveNoteBtn");
    const lastNoteText=document.getElementById("lastNoteText");
    let activeID=null;


    // ⭐ OPEN NOTE MODAL + GET LAST NOTE
    document.querySelectorAll(".contact-btn.note").forEach(btn=>{
        btn.addEventListener("click",(e)=>{
            e.stopPropagation();               // prevent dashboard redirect ❗
            activeID=btn.dataset.id;
            modal.style.display="flex";
            newNote.value="";

            // Fetch last note instantly
            fetch(`/contacts/get-last-note/${activeID}/`)
            .then(r=>r.json())
            .then(d=>{
                lastNoteText.innerHTML = d.exists
                    ? `<b>${d.text}</b><br><small>${d.time}</small>`
                    : "No previous notes found";
            });

        });
    });


    // ⭐ SAVE NOTE → POPUP + AUTO CLOSE
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
                    willClose:()=>closeNote()    // modal auto close 🔥
                });

                lastNoteText.innerHTML = `<b>${d.text}</b><br><small>${d.time}</small>`;
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
                        if(d.success){
                            btn.closest(".contact-row").remove();
                        }
                    });
                }
            });

        };
    });

});



/*============ MODAL + CSRF ============*/
function closeNote(){ document.getElementById("noteModal").style.display="none"; }

function getCookie(name){
    return document.cookie.split("; ").reduce((a,b)=>{
        let c=b.split("=");return c[0]==name?decodeURIComponent(c[1]):a;
    },"");
}
