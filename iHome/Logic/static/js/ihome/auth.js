function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function () {
        setTimeout(function () {
            $('.popup_con').fadeOut('fast', function () {
            });
        }, 1000)
    });
}


function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    // TODO: 查询用户的实名认证信息

    $.get("/api/v1.0/user/auth", function (resp) {
        if (resp.errno == "0") {
            if (resp.data.real_name && resp.data.id_card) {
                //设置值
                $("#real-name").val(resp.data.real_name)
                $("#id-card").val(resp.data.id_card)

                // 让对话框不可用
                $("#real-name").attr("disabled", true)
                $("#id-card").attr("disabled", true)

                $(".btn-success").hide()
            }

        } else if (resp.errno == "4101") {
            location.href = "/"
        } else {
            alert(resp.errmsg)
        }

    })


    // TODO: 管理实名信息表单的提交行为

    $("#form-auth").submit(function (e) {
        e.preventDefault()
        //获取实名认证的信息
        var real_name = $("#real-name").val()
        var id_card = $("#id-card").val()
        if (!(real_name & id_card)) {
            $(".error-msg").show()
            return
        }
        $(".error-msg").hide()

        params = {
            "real_name": real_name,
            "id_card": id_card
        }

        $.ajax({
            url: "/api/v1.0/user/auth",
            type: "post",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            contentType: "application/json",
            data: JSON.stringify(params),
            success: function (resp) {
                if (resp.errno == "0") {
                    $("#real-name").attr("disabled", true)
                    $("#id-card").attr("disabled", true)

                    $(".btn-success").hide()


                } else if (resp.errno == "4101") {
                    location.href = "/"
                } else {
                    alert(resp.errmsg)
                }


            }


        })


    })


})