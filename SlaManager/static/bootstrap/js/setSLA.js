const form = document.querySelector("#custom_interval");

const start_time = form["start_time"];
const end_time = form["end_time"];

form.addEventListener("submit", sendData);

function validateForm(start_time,end_time) {
    var startTimeDate = new Date(start_time.value);
    var endTimeDate = new Date(end_time.value);    
    
    var currentDate = new Date();

    if (startTimeDate > endTimeDate || startTimeDate > currentDate || endTimeDate >= currentDate) {
        return false;
    }else{
        return true;
    }

}

function sendData(event){

    event.preventDefault();

    if(validateForm(start_time,end_time) == false){
        alert("La data di inizio deve essere precedente alla data di fine e la data di fine non può essere maggiore della data attuale!");
        return;
    }

    let map = {
        data_inizio: start_time.value, 
        data_fine: end_time.value
    }    

    fetch("/customSearch", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(map),
    }).then(onResponse).then(onData);

}

function onResponse(response){

    return response.json();
}

function onData(json){

    const resultsDiv = document.getElementById("resultsDiv");

    // Elimina iterativamente tutti i nodi figli
    while (resultsDiv.firstChild) {
        resultsDiv.removeChild(resultsDiv.firstChild);
    }

    for (var i = 0; i < json.length; i++) {
        
        console.log(json[i]);
        
        const li = document.createElement("li");
        li.textContent = "Violazioni di " +  json[i]["nome"] + " : " + json[i]["violazioni"];
        
        resultsDiv.appendChild(li);
        
    }

}