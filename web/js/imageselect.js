imgOpt = document.querySelector("select#img")

fetch('/images').then(
    function(r){
        return r.json();
    }
).then(
    function(r){
        for(let i of r) {
            let opt_elem = document.createElement("option");
            opt_elem.value = i
            opt_elem.innerHTML = i
            imgOpt.appendChild(opt_elem)
        }
    }
)
function img_change(){
    document.querySelector("img").src = "data/images/" + imgOpt.value
}

imgOpt.addEventListener('change', img_change)