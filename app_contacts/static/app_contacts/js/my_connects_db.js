document.addEventListener("DOMContentLoaded", () => {

    // NOTE TOGGLE — final working version for all buttons
    const notePanel = document.querySelector(".note-panel");
    const noteBtns = document.querySelectorAll(".note-toggle");

    noteBtns.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.stopPropagation();
            notePanel.classList.toggle("active");
            notePanel.classList.toggle("hidden");
        });
    });

    // TOUCH FIX (mobile)
    document.addEventListener("touchstart", function(){}, true);

    /* =============================
       YOUR EXISTING CODE (unchanged)
       ============================= */

    document.querySelectorAll(".call, .email").forEach(btn => {
        btn.addEventListener("click", () => {
            let id = btn.dataset.id;
            let action = btn.classList.contains("call") ? "call" : "email";

            fetch(`/contacts/track/${id}/${action}/`)
            .then(r=>r.json())
            .then(data=>{
                if(action==="call")  callCount.innerText = data.call;
                if(action==="email") emailCount.innerText = data.email;
            });
        });
    });

    const saveBtn = document.getElementById("saveNoteBtn");
    const newNote = document.getElementById("newNote");
    const noteList = document.getElementById("noteList");
    const noteCount = document.getElementById("noteCount");

    saveBtn.addEventListener("click", function () {

        let id = this.dataset.id;
        let text = newNote.value.trim();
        if(!text) return alert("Write something!");

        fetch(`/contacts/save-note/${id}/`,{
            method:"POST",
            headers:{
                "X-CSRFToken": getCookie("csrftoken"),
                "X-Requested-With":"XMLHttpRequest",
                "Content-Type":"application/x-www-form-urlencoded"
            },
            body:`text=${encodeURIComponent(text)}`
        })
        .then(r=>r.json())
        .then(d=>{
            if(d.success){
                noteList.insertAdjacentHTML("afterbegin",`
                    <div class="note-item glass-card">
                        <p>${d.text}</p>
                        <small>${d.time}</small>
                    </div>
                `);
                noteCount.innerText = d.count;
                newNote.value="";
            }else alert(d.message);
        });

    });

});

// CSRF Helper
function getCookie(name){
    return document.cookie.split("; ").reduce((a,b)=>{
        let c=b.split("="); 
        return c[0]==name ? decodeURIComponent(c[1]) : a;
    }, "");
}
