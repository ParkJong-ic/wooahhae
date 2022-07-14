$(document).ready(function () {
    post_list()
})

function post_list() {
    $.ajax({
        type: "GET",
        url: "/posting",
        data: {},
        success: function (response) {
            console.log(response)
        }
    });
}

// 로그인
function sign_in() {
    let email = $("#input-email").val()
    let password = $("#input-password").val()

    if (email == "") {
        $("#help-email-login").text("아이디를 입력해주세요.")
        $("#input-email").focus()
        return;
    } else {
        $("#help-email-login").text("")
    }

    if (password == "") {
        $("#help-password-login").text("비밀번호를 입력해주세요.")
        $("#input-password").focus()
        return;
    } else {
        $("#help-password-login").text("")
    }
    $.ajax({
        type: "POST",
        url: "/sign_in",
        data: {
            email_give: email,
            password_give: password
        },
        success: function (response) {
            if (response['result'] == 'success') {
                $.cookie('mytoken', response['token'], {path: '/'});
                window.location.replace("/main")
            } else {
                alert(response['msg'])
            }
        }
    });
}

function sign_up() {
    let email = $("#input-email").val()
    let password = $("#input-password").val()
    let password2 = $("#input-password2").val()
    let name = $("#input-name").val()
    let nickname = $("#input-nickname").val()
    let tel = $("#input-tel").val()
    let address = $("#input-address").val()

    console.log(email, password, password2)


    if ($("#help-email").hasClass("is-danger")) {
        alert("이메일을 다시 확인해주세요.")
        return;
    } else if (!$("#help-email").hasClass("is-success")) {
        alert("이메일 중복확인을 해주세요.")
        return;
    }

    if (password == "") {
        $("#help-password").text("비밀번호를 입력해주세요.").removeClass("is-safe").addClass("is-danger")
        $("#input-password").focus()
        return;
    } else if (!is_password(password)) {
        $("#help-password").text("비밀번호의 형식을 확인해주세요. 영문과 숫자 필수 포함, 특수문자(!@#$%^&*) 사용가능 8-20자").removeClass("is-safe").addClass("is-danger")
        $("#input-password").focus()
        return
    } else {
        $("#help-password").text("사용할 수 있는 비밀번호입니다.").removeClass("is-danger").addClass("is-success")
    }
    if (password2 == "") {
        $("#help-password2").text("비밀번호를 입력해주세요.").removeClass("is-safe").addClass("is-danger")
        $("#input-password2").focus()
        return;
    } else if (password2 != password) {
        $("#help-password2").text("비밀번호가 일치하지 않습니다.").removeClass("is-safe").addClass("is-danger")
        $("#input-password2").focus()
        return;
    } else {
        $("#help-password2").text("비밀번호가 일치합니다.").removeClass("is-danger").addClass("is-success")
    }
    $.ajax({
        type: "POST",
        url: "/sign_up/save",
        data: {
            email_give: email,
            password_give: password,
            name_give: name,
            nickname_give: nickname,
            tel_give: tel,
            address_give: address
        },
        success: function (response) {
            alert("회원가입을 축하드립니다!")
            window.location.replace("/login")
        }
    });

}

function toggle_sign_up() {
    $("#sign-up-box").toggleClass("is-hidden")
    $("#div-sign-in-or-up").toggleClass("is-hidden")
    $("#btn-check-dup").toggleClass("is-hidden")
    $("#help-email").toggleClass("is-hidden")
    $("#help-password").toggleClass("is-hidden")
    $("#help-password2").toggleClass("is-hidden")
}

function is_email(asValue) {
    var regExp = /^[0-9a-zA-Z]([-_\.]?[0-9a-zA-Z])*@[0-9a-zA-Z]([-_\.]?[0-9a-zA-Z])*\.[a-zA-Z]{2,3}$/i;
    return regExp.test(asValue);
}

function is_password(asValue) {
    var regExp = /^(?=.*\d)(?=.*[a-zA-Z])[0-9a-zA-Z!@#$%^&*]{8,20}$/;
    return regExp.test(asValue);
}

function check_dup() {
    let email = $("#input-email").val()
    console.log(email)
    if (email == "") {
        $("#help-email").text("이메일을 입력해주세요.").removeClass("is-safe").addClass("is-danger")
        $("#input-email").focus()
        return;
    }
    if (!is_email(email)) {
        $("#help-email").text("이메일 형식에 맞게 입력해주세요").removeClass("is-safe").addClass("is-danger")
        $("#input-email").focus()
        return;
    }
    $("#help-email").addClass("is-loading")
    $.ajax({
        type: "POST",
        url: "/sign_up/check_dup",
        data: {
            email_give: email
        },
        success: function (response) {

            if (response["exists"]) {
                $("#help-email").text("이미 존재하는 이메일입니다.").removeClass("is-safe").addClass("is-danger")
                $("#input-email").focus()
            } else {
                $("#help-email").text("사용할 수 있는 이메일입니다.").removeClass("is-danger").addClass("is-success")
            }
            $("#help-email").removeClass("is-loading")

        }
    });
}


//로그아웃
function sign_out() {
    $.removeCookie('mytoken', {path: '/'});
    alert('로그아웃!')
    window.location.href = "/login"
}

function detail() {
    window.location.href = "/detail"
}

function main() {
    window.location.href = "/main"
}

// 등록하기
function save_order() {
    let content = $('#content').val()
    let time = $('#time').val()
    let file = $('#file')[0].files[0]
    let writer = $('#writer').val()
    let address = $('#address').val()
    let form_data = new FormData();
    let anonymous = ""

    if ($('#anonymous').is(':checked') == true) {
        anonymous = "on"
    } else {
        anonymous = "off"
    }

    form_data.append("file_give", file)
    form_data.append("content_give", content)
    form_data.append("anonymous_give", anonymous)
    form_data.append("writer_give", writer)
    form_data.append("address_give", address)
    form_data.append("time_give", time)

    $.ajax({
        type: "POST",
        url: "/posting",
        data: form_data,
        cache: false,
        contentType: false,
        processData: false,
        success: function (response) {
            alert(response["msg"])
            window.location.reload()
        }
    });

}

$(function () {
    $("#file").on('change', function () {
        readURL(this);
    });
});

function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            $('#preImage').attr('src', e.target.result);
        }
        reader.readAsDataURL(input.files[0]);
    }
}

// function main(){
//     window.location.href="{{ url_for('main') }}"
// }


// function show_comment() {
//             let num = $('#comment-num').val()
//             $('#order-box').empty()
//             $.ajax({
//                 type: 'GET',
//                 url: '/detail',
//                 data: {},
//                 success: function (response) {
//                     let comments = response['comments']
//                     for (let i = 0; i < comments.length; i++) {
//                         let comment = comments[i]
//
//                         if (comment['num'] == num) {
//                             let temp_html = `<li class="ub-content">
//                                                 <p class="usertxt ub-word">${comment['comment']}</p>
//                                               </li>`
//                             $('#order-box').append(temp_html)
//                         }
//
//                     }
//                 }
//             });
