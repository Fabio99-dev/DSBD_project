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

const startingLatitude = form["startingLatitude"]
const startingLongitude = form["startingLongitude"]
const endingLatitude = form["endingLatitude"]
const endingLongitude = form["endingLongitude"]

//Variabili globali
let latitude_departure = 0
let longitude_departure = 0
let latitude_arrival = 0
let longitude_arrival = 0

//Event listeners

departTime.addEventListener("input", showRoute);

/*
estimatedArrivalTime.addEventListener("focusout", showRoute);
estimatedArrivalTime.addEventListener("focusout", test);*/

//Implementazione delle funzioni

const body = document.querySelector("body")
body.onload = () =>{


    const origin = departureAddress.value+" "+ departureCAP.value +" " + departureCity.value;
    const destination = arrivalAddress.value+" "+arrivalCAP.value + " " + arrivalCity.value; 
    map.src = "https://www.google.com/maps/embed/v1/directions?key=AIzaSyBonANlvTZDMhpcdoxhJSUHzZusR_BSf64&origin=" + encodeURIComponent(origin)+"&destination=" + encodeURIComponent(destination)
    //Request the coordinates of the place through bing maps api
    const departure_coordinates_endpoint = "http://dev.virtualearth.net/REST/v1/Locations?&locality="+ encodeURIComponent(departureCity.value) +"&addressLine=" + encodeURIComponent(departureAddress.value) + "&postalCode="+ departureCAP.value+"&maxResults=1&key=" + BING_API_KEY
    fetch(departure_coordinates_endpoint).then(onResponse).then(getDepartureCoordinates)

    const arrival_coordinates_endpoint = "http://dev.virtualearth.net/REST/v1/Locations?&locality="+ encodeURIComponent(arrivalCity.value) +"&addressLine=" + encodeURIComponent(arrivalAddress.value) + "&postalCode="+ arrivalCAP.value+"&maxResults=1&key=" + BING_API_KEY
    fetch(arrival_coordinates_endpoint).then(onResponse).then(getArrivalCoordinates)

    //Find the route
    
    if(latitude_departure !=0 &&longitude_departure != 0 && latitude_arrival != 0 && longitude_arrival != 0){
    const route_endpoint = "http://dev.virtualearth.net/REST/V1/Routes?wp.0="+latitude_departure+","+longitude_departure+"&wp.1=" + latitude_arrival + "," +longitude_arrival +"&dateTime="+ departTime.value + "&key=" + BING_API_KEY 
    fetch(route_endpoint).then(onResponse).then(onRoute);

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
    startingLatitude.value = latitude_departure
    startingLongitude.value = longitude_departure
    console.log(startingLatitude.value)
    console.log(startingLongitude.value)

}

function getArrivalCoordinates(json){


    latitude_arrival = json.resourceSets[0].resources[0].geocodePoints[0].coordinates[0]
    longitude_arrival = json.resourceSets[0].resources[0].geocodePoints[0].coordinates[1]
    endingLatitude.value = latitude_arrival
    endingLongitude.value = longitude_arrival  
    console.log(endingLatitude.value)
    console.log(endingLongitude.value)

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



function onResponse(response){

    return response.json();
}

function onJson(json){

    console.log(json)
}
