document.addEventListener("DOMContentLoaded", () => {

    /* ============================
       🔍 SEARCH CONTACT
    ============================ */
    const searchBox = document.getElementById("searchBox");
    if(searchBox){
        searchBox.addEventListener("input",()=>{
            let q = searchBox.value.toLowerCase();
            document.querySelectorAll(".contact-row").forEach(row=>{
                row.style.display = row.dataset.name.includes(q) ? "" : "none";
            });
        });
    }

    /* ============================
       📝 NOTE MODAL
    ============================ */
    const modal = document.getElementById("noteModal");
    const newNote = document.getElementById("newNote");
    const saveBtn = document.getElementById("saveNoteBtn");
    const lastNoteText = document.getElementById("lastNoteText");
    let activeID = null;


    // ⭐ OPEN MODAL + LOAD LAST NOTE
    document.querySelectorAll(".contact-btn.note").forEach(btn=>{
        btn.addEventListener("click",()=>{
            activeID = btn.dataset.id;
            modal.style.display="flex";
            newNote.value="";

            // 🔥 Load last note instantly
            fetch(`/contacts/get-last-note/${activeID}/`)
            .then(r=>r.json())
            .then(data=>{
                lastNoteText.innerHTML = data.exists 
                    ? `<b>${data.text}</b><br><small>${data.time}</small>`
                    : "No previous note found";
            });
        });
    });


    // 💾 SAVE NOTE
    saveBtn.addEventListener("click", ()=>{
        let text = newNote.value.trim();
        if(!text) return Swal.fire("⚠ Write something first!");

        fetch(`/contacts/save-note/${activeID}/`,{
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

                // 🔥 SHOW SUCCESS MESSAGE
                Swal.fire({
                    icon:"success",
                    title:"Saved!",
                    timer:1400,
                    showConfirmButton:false
                });

                // 🌟 Update last note instantly in modal
                lastNoteText.innerHTML = `<b>${data.text}</b><br><small>${data.time}</small>`;

                closeNote(); // Popup auto close
            }
        });
    });

    // Close Modal
    window.closeNote = ()=> modal.style.display="none";


});


/* ============================
   🔐 CSRF
============================ */
function getCookie(name){
    return document.cookie.split("; ").reduce((a,b)=>{
        let c=b.split("="); return c[0]==name?decodeURIComponent(c[1]):a;
    },"");
}
