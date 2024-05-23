let answer_form = document.querySelector("#answer-form");
let check_btn = document.querySelector("#check-btn");
let quizz_id = parseInt(document.querySelector("#quizz-id").innerHTML);
let quizz_block = document.querySelector("#quizz-block");

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function post_answer(answer, quizz_id) {
    $.post("/check_answer/", {
        quizz_id: quizz_id,
        answer: answer
    }, function(data) {
        if (data["status"] == true) {
            let submit_btn = document.createElement("button");
            submit_btn.type = "submit";
            answer_form.appendChild(submit_btn);
            submit_btn.click();
            answer_form.removeChild(submit_btn);
        } else if (data["status"] == false) {
            quizz_block.classList.add("shake");
            quizz_block.classList.add("red-bottom");
            setInterval(remove_border_color, 400);
            setInterval(remove_shake, 4000);
        }

    })
}

function remove_border_color() {
    quizz_block.classList.remove("red-bottom");
}

function remove_shake() {
    quizz_block.classList.remove("shake");
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

check_btn.onclick = function() {
    let answer = document.querySelector("#answer").value;
    post_answer(answer, quizz_id);
}