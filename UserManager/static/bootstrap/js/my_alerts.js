const body = document.querySelector("body")
const user_id = document.querySelector("#user_id")

body.onload = () => {

    fetch("/getData/" + encodeURIComponent(user_id.value)).then(onResponse).then(onData)
    console.log("sto facendo la richiesta")

}

function onResponse(response){

    return response.json();
}

function onData(json){

    console.log("Ritorno della richiesta")
    console.log(json)
    const container = document.querySelector("#myAlerts")
    let row = document.createElement("div")
    row.classList.add("row")
    row.classList.add("margin-top")
    let i =0
    for(i= 0; i < json.length; i++){

        
        const card_container = document.createElement("div")
        card_container.id = json[i].subscription_id
        card_container.classList.add("col-md-4")

        const card = document.createElement("div")
        card.classList.add("card")

        const card_body = document.createElement("div")
        card_body.classList.add("card-body")

        const title = document.createElement("h4")
        title.classList.add("card-title")
        title.classList.add("text-align-center")
        title.textContent = "Alert numero: " + json[i].subscription_id
        card_body.appendChild(title)

        const departure_title = document.createElement("h6")
        departure_title.textContent = "Dati di partenza"
        departure_title.classList.add("text-muted")
        departure_title.classList.add("text-align-center")
        departure_title.classList.add("card-subtitle")
        card_body.appendChild(departure_title)

        const departure_data = document.createElement("p")
        departure_data.textContent = json[i].departureCity + ", " + json[i].departureCAP + ", " + json[i].departureAddress
        departure_data.classList.add("text-align-center")
        card_body.appendChild(departure_data)

        const arrival_title = document.createElement("h6")
        arrival_title.textContent = "Dati di arrivo"
        arrival_title.classList.add("text-muted")
        arrival_title.classList.add("text-align-center")
        arrival_title.classList.add("card-subtitle")
        card_body.appendChild(arrival_title)

        const arrival_data = document.createElement("p")
        arrival_data.textContent = json[i].arrivalCity + ", " + json[i].arrivalCAP + ", " + json[i].arrivalAddress
        arrival_data.classList.add("text-align-center")
        card_body.appendChild(arrival_data)

        const departure_time_title = document.createElement("h6")
        departure_time_title.textContent = "Orario di partenza"
        departure_time_title.classList.add("text-muted")
        departure_time_title.classList.add("text-align-center")
        departure_time_title.classList.add("card-subtitle")
        card_body.appendChild(departure_time_title)

        const departure_time_data = document.createElement("p")
        departure_time_data.textContent = json[i].departTime
        departure_time_data.classList.add("text-align-center")
        card_body.appendChild(departure_time_data)

        const notify_threshold_title = document.createElement("h6")
        notify_threshold_title.textContent = "Soglia di notifica"
        notify_threshold_title.classList.add("text-muted")
        notify_threshold_title.classList.add("text-align-center")
        notify_threshold_title.classList.add("card-subtitle")
        card_body.appendChild(notify_threshold_title)

        const notify_threshold = document.createElement("p")
        notify_threshold.textContent = json[i].notifyThreshold
        notify_threshold.classList.add("text-align-center")
        card_body.appendChild(notify_threshold)

        const advances_title = document.createElement("h6")
        advances_title.textContent = "Notifica gli anticipi"
        advances_title.classList.add("text-muted")
        advances_title.classList.add("text-align-center")
        advances_title.classList.add("card-subtitle")
        card_body.appendChild(advances_title)

        const advances_data = document.createElement("p")
        if(json.advances === true){
            advances_data.textContent = "Sì"
        }else{
            advances_data.textContent = "No"
        }
        advances_data.classList.add("text-align-center")
        card_body.appendChild(advances_data)

        const buttonDiv = document.createElement("div")
        buttonDiv.classList.add("buttons")

        const deleteButton = document.createElement("button")
        deleteButton.classList.add("btn")
        deleteButton.classList.add("btn-danger")

        const deleteLink = document.createElement("a")
        deleteLink.href = "http://my.traffic.com:8080/deleteAlert/"+encodeURIComponent(json[i].subscription_id)

        const deleteIcon = document.createElement("img")
        deleteIcon.src = "http://127.0.0.1:3001/static/img/trash-fill.png"

        deleteLink.appendChild(deleteIcon)
        deleteButton.appendChild(deleteLink)

        buttonDiv.appendChild(deleteButton)

        const editButton = document.createElement("button")
        editButton.classList.add("btn")
        editButton.classList.add("btn-warning")

        const editLink = document.createElement("a")
        deleteLink.href = "http://127.0.0.1:3001/editAlert/"+encodeURIComponent(json[i].subscription_id)

        const editIcon = document.createElement("img")
        editIcon.src = "http://127.0.0.1:3001/static/img/pencil-fill.png"

        editLink.appendChild(editIcon)
        editButton.appendChild(editLink)

        buttonDiv.appendChild(editButton)

        card_body.appendChild(buttonDiv)

        card.appendChild(card_body)
        card_container.appendChild(card)
        row.appendChild(card_container)
        console.log(row.childElementCount)

        if(row.childElementCount == 3){ 
            container.appendChild(row)
            row = document.createElement("div")
            row.classList.add("row")
            row.classList.add("margin-top")

        }

    }
    if(row.childElementCount != 3){
        container.appendChild(row)
    }

}
