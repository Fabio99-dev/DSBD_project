const BING_API_KEY = "At71cbvTs-4zsbhV7M07ZYd41Y4FGK3PHvVOxTVZMz75lxwc1M-IQyZHypkgscJ6"

const form = document.querySelector("#form")
const map = document.querySelector("#map")

const departureCity = form["departureCity"]
const departureCAP = form["departureCAP"]
const departureAddress = form["departureAddress"]

const arrivalCity = form["arrivalCity"]
const arrivalCAP = form["arrivalCAP"]
const arrivalAddress = form["arrivalAddress"]

const departTime = form["departTime"]
const estimatedArrivalTime = form["estimatedArrivalTime"]
const travelTime = form["travelTime"]



button = document.querySelector("#testButton");

//Variabili globali
let latitude_departure = 0
let longitude_departure = 0
let latitude_arrival = 0
let longitude_arrival = 0

//Event listeners
departureCity.addEventListener("focusout", changeMap)
departureCAP.addEventListener("focusout", changeMap)
departureAddress.addEventListener("focusout", changeMap)

arrivalCity.addEventListener("focusout", showRoute)
arrivalCAP.addEventListener("focusout", showRoute)
arrivalAddress.addEventListener("focusout", showRoute)

departTime.addEventListener("input", showRoute);
departTime.addEventListener("input", test);

/*
estimatedArrivalTime.addEventListener("focusout", showRoute);
estimatedArrivalTime.addEventListener("focusout", test);*/

function test(event){

    console.log("JS MERDA AUTISTICO")
}

//Implementazione delle funzioni

function changeMap(event){

    console.log("Event change map")
    /*https://www.google.com/maps/embed/v1/search?key=AIzaSyBonANlvTZDMhpcdoxhJSUHzZusR_BSf64&q=Piazza+della+repubblica+Catania */
    if(departureCity.value !== "" && departureCAP.value !== "" && departureAddress !== ""){

        console.log("Fatto")
        //Update the map
        const address = departureAddress.value+" "+departureCity.value;
        map.src = "https://www.google.com/maps/embed/v1/search?key=AIzaSyBonANlvTZDMhpcdoxhJSUHzZusR_BSf64&q=" + encodeURIComponent(address)
        //Request the coordinates of the place through bing maps api
        const endpoint = "http://dev.virtualearth.net/REST/v1/Locations?&locality="+ encodeURIComponent(departureCity.value) +"&postalCode="+ encodeURIComponent(departureCAP.value)+"&addressLine="+encodeURIComponent(departureAddress.value)+"&maxResults=1&key="+BING_API_KEY
        fetch(endpoint).then(onResponse).then(getDepartureCoordinates);
    }
  
}

function showRoute(event){

    console.log("Event show route")
    /*https://www.google.com/maps/embed/v1/search?key=AIzaSyBonANlvTZDMhpcdoxhJSUHzZusR_BSf64&q=Piazza+della+repubblica+Catania */
    if(arrivalCity.value !== "" && arrivalCAP.value !== "" && arrivalAddress !== ""){

        console.log("Done")
        //Update the map
        const origin = departureAddress.value+" "+ departureCAP.value +" " + departureCity.value;
        const destination = arrivalAddress.value+" "+arrivalCAP.value + " " + arrivalCity.value; 
        map.src = "https://www.google.com/maps/embed/v1/directions?key=AIzaSyBonANlvTZDMhpcdoxhJSUHzZusR_BSf64&origin=" + encodeURIComponent(origin)+"&destination=" + encodeURIComponent(destination)
        //Request the coordinates of the place through bing maps api

        ////http://dev.virtualearth.net/REST/v1/Locations?&locality=Raddusa&addressLine=Via%20Asilo%Nido%20&maxResults=5&key=At71cbvTs-4zsbhV7M07ZYd41Y4FGK3PHvVOxTVZMz75lxwc1M-IQyZHypkgscJ6

        /*const departure_coordinates_endpoint = "http://dev.virtualearth.net/REST/v1/Locations?&locality="+ encodeURIComponent(departureCity.value) +"&addressLine=" + encodeURIComponent(departureAddress.value) + "&postalCode="+ departureCAP.value+"&maxResults=1&key=" + BING_API_KEY
        fetch(departure_coordinates_endpoint).then(onResponse).then(getDepartureCoordinates)*/

        const arrival_coordinates_endpoint = "http://dev.virtualearth.net/REST/v1/Locations?&locality="+ encodeURIComponent(arrivalCity.value) +"&addressLine=" + encodeURIComponent(arrivalAddress.value) + "&postalCode="+ arrivalCAP.value+"&maxResults=1&key=" + BING_API_KEY
        fetch(arrival_coordinates_endpoint).then(onResponse).then(getArrivalCoordinates)

        //Find the route
        //http://dev.virtualearth.net/REST/V1/Routes?wp.0=37.779160067439079,-122.42004945874214&wp.1=32.715685218572617,-117.16172486543655&key=At71cbvTs-4zsbhV7M07ZYd41Y4FGK3PHvVOxTVZMz75lxwc1M-IQyZHypkgscJ6
        const route_endpoint = "http://dev.virtualearth.net/REST/V1/Routes?wp.0="+latitude_departure+","+longitude_departure+"&wp.1=" + latitude_arrival + "," +longitude_arrival +"&dateTime="+ departTime.value + "&key=" + BING_API_KEY 
        fetch(route_endpoint).then(onResponse).then(onRoute);
    }

}


function getDepartureCoordinates(json){


    latitude_departure = json.resourceSets[0].resources[0].geocodePoints[0].coordinates[0]
    longitude_departure = json.resourceSets[0].resources[0].geocodePoints[0].coordinates[1]
    

}

function getArrivalCoordinates(json){


    latitude_arrival = json.resourceSets[0].resources[0].geocodePoints[0].coordinates[0]
    longitude_arrival = json.resourceSets[0].resources[0].geocodePoints[0].coordinates[1]  

}

function onRoute(json){

    console.log(json)

    let val2 = json.resourceSets[0].resources[0].travelDuration;
    val2 = parseInt(val2)
    let val = json.resourceSets[0].resources[0].travelDurationTraffic;
    val = parseInt(val)
    estimatedArrivalTime.value = Math.trunc(val /60) + " minuti"
    travelTime.value = Math.trunc(val2/60) + " minuti"
}

/*Piano operativo.
1. Mettere degli event listener su partenza e destinazione. 
2. Quando viene settata la destinazione, cambiare la modalità da search a directions. 
3. L'evento su focusout rimane ed esegue la query a bingMaps, facendo però la conversione prima 
dei luoghi in coordinate.*/

function funzione(event){

    if(partenza.value !== '' && arrivo.value !== '' && oraPartenza.value !== ''){

    console.log("TEST");
    fetch("http://dev.virtualearth.net/REST/V1/Routes/Driving?o=json&wp.0="+ partenza.value + "&wp.1="+arrivo.value +"&avoid=minimizeTolls&dateTime="+ oraPartenza.value +"&key=At71cbvTs-4zsbhV7M07ZYd41Y4FGK3PHvVOxTVZMz75lxwc1M-IQyZHypkgscJ6").then(onResponse).then(onJson)
    
    }else{

        console.log("Ho ricevuto un evento")
    }
  
}

function onResponse(response){

    return response.json();
}

function onJson(json){

    console.log(json)
}



//http://dev.virtualearth.net/REST/v1/Locations?&locality=Catania&addressLine=Piazza%20%della%Repubblica&maxResults=5&key=At71cbvTs-4zsbhV7M07ZYd41Y4FGK3PHvVOxTVZMz75lxwc1M-IQyZHypkgscJ6
//http://dev.virtualearth.net/REST/v1/Locations?&locality=Raddusa&addressLine=Via%20Asilo%Nido%20&maxResults=5&key=At71cbvTs-4zsbhV7M07ZYd41Y4FGK3PHvVOxTVZMz75lxwc1M-IQyZHypkgscJ6