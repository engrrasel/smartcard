document.addEventListener("DOMContentLoaded", ()=>{

    const counter = document.getElementById("reqCount");


    /*==================== ACCEPT ====================*/
    document.querySelectorAll(".btn-accept").forEach(btn=>{
        btn.onclick = ()=>{

            fetch(`/contacts/accept/${btn.dataset.id}/`)
            .then(res=>res.json())
            .then(data=>{
                if(data.success){

                    let box = document.getElementById("req-"+data.id);
                    box.style.opacity = "0";

                    setTimeout(()=> box.remove(), 300); // UI instantly update

                    updateCount();  // 🔥 Count reduce instantly

                    Swal.fire({
                        icon:"success",
                        title:"Request Accepted",
                        timer:900,
                        showConfirmButton:false
                    });
                }
            });
        };
    });



    /*==================== REJECT ====================*/
    document.querySelectorAll(".btn-reject").forEach(btn=>{
        btn.onclick = ()=>{

            fetch(`/contacts/reject/${btn.dataset.id}/`)
            .then(res=>res.json())
            .then(data=>{
                if(data.success){

                    let box = document.getElementById("req-"+data.id);
                    box.style.opacity = "0";

                    setTimeout(()=> box.remove(), 300);

                    updateCount();  // 🔥 Live badge update

                    Swal.fire({
                        icon:"info",
                        title:"Request Removed",
                        timer:900,
                        showConfirmButton:false
                    });
                }
            });
        };
    });



    /*==================== 🔍 LIVE SEARCH ====================*/
    const searchInput = document.getElementById("searchReq");

    searchInput?.addEventListener("input",()=>{

        const q = searchInput.value.toLowerCase().trim();

        document.querySelectorAll(".req-item").forEach(item=>{
            item.style.display = item.dataset.name.includes(q) ? "" : "none";
        });

        updateCount(); // 🔥 Search করলে count dynamic update
    });



    /*==================== COUNT UPDATE ====================*/
    function updateCount(){
        if(counter){
            const visible = document.querySelectorAll(".req-item:not([style*='display: none'])");
            counter.innerText = visible.length;
        }
    }

});
