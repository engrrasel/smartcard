function clickTrack(btn){
    let data = {csrfmiddlewaretoken: window.CSRF_TOKEN, action:btn};

    navigator.geolocation?.getCurrentPosition(
        p=>{data.lat=p.coords.latitude;data.lon=p.coords.longitude; send(data)},
        ()=>send(data)
    );
}

function send(data){
    fetch(window.CLICK_URL,{
        method:"POST",
        headers:{"Content-Type":"application/x-www-form-urlencoded"},
        body:new URLSearchParams(data)
    });
}
