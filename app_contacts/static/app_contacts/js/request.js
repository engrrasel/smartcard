document.addEventListener("DOMContentLoaded", ()=>{

    const counter = document.getElementById("reqCount");

    /* ========== ACCEPT REQUEST ========== */
    document.querySelectorAll(".btn-accept").forEach(btn=>{
        btn.onclick = ()=>{

            fetch(`/contacts/accept/${btn.dataset.id}/`)
            .then(res=>res.json())
            .then(data=>{
                if(data.success){

                    let box = document.getElementById("req-"+data.id);
                    box.style.opacity="0";
                    setTimeout(()=> box.remove(),300);  // 🔥 Reload ছাড়াই remove

                    updateCount();

                    Swal.fire({ icon:"success", title:"Accepted", timer:800, showConfirmButton:false });
                }
            });
        }
    });


    /* ========== REJECT REQUEST ========== */
    document.querySelectorAll(".btn-reject").forEach(btn=>{
        btn.onclick = ()=>{

            fetch(`/contacts/reject/${btn.dataset.id}/`)
            .then(res=>res.json())
            .then(data=>{
                if(data.success){

                    let box = document.getElementById("req-"+data.id);
                    box.style.opacity="0";
                    setTimeout(()=> box.remove(),300);  // 🔥 Instantly UI update

                    updateCount();

                    Swal.fire({ icon:"info", title:"Removed", timer:800, showConfirmButton:false });
                }
            });
        }
    });


    /* ========== COUNT UPDATE ========== */
    function updateCount(){
        if(counter){
            counter.innerText = document.querySelectorAll(".req-card").length;
        }
    }

});
