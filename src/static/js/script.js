// var target_output = document.getElementById("learn_output");
var update = new EventSource("/data");

function updateView(){
    var number_live_neighbours = document.getElementById("number_live_neighbours");
    var host = document.getElementById("host");
    var port = document.getElementById("port");
    var id = document.getElementById("id");
    var transmitting = document.getElementById("transmitting");
    var neighbours = document.getElementById("neighbours");
    var neighbour_state = document.getElementById("neighbour_state");
    
    data = JSON.parse(sessionStorage.getItem("data"));
    console.log(data);
    number_live_neighbours.innerHTML  = Object.keys(data.neighbours).length;
    host.innerHTML = data.host;
    port.innerHTML = data.port;
    id.innerHTML = data.id;
    transmitting.innerHTML = data.transmit;
    neighbours.innerHTML = Object.keys(data.neighbours);
    neighbour_state.innerHTML = Object.keys(data.neighbour_state);

}

function toggleTransmit(){
    return fetch('/transmit', {
        method: 'PUT'
    }).then(response => {
        console.log(response.status);
    })
}

update.onmessage = function (e) {
    if (e.data == "close") {
        update.close();
    } else {
        let json = JSON.stringify(JSON.parse(e.data), null, 2);
        // target_output.innerHTML = json
        sessionStorage.setItem("data", json);
        updateView();
    }
};


