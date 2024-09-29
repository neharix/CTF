let table = document.querySelector("#table-body");
let challenge_pk = JSON.parse(document.querySelector("#challenge-pk").textContent);

function success(data) {
    table.innerHTML = "";
    data.forEach(row => {
        let table_row = document.createElement("tr");
        let cell_id = document.createElement("td");
        cell_id.innerHTML = row.id;
        let cell_name = document.createElement("td");
        cell_name.innerHTML = row.name;
        let cell_score = document.createElement("td");
        cell_score.innerHTML = row.score;

        table_row.appendChild(cell_id);
        table_row.appendChild(cell_name);
        table_row.appendChild(cell_score);
        table.append(table_row);
    });
}
function update() {
    $.ajax({
        url: "/api/v1/get-current-data/" + challenge_pk + "/",
        type: 'GET',
        dataType: 'json',
        success: success,
    });
}

const updater = setInterval(update, 3000);

update();