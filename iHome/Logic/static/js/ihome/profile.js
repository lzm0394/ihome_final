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
    //  在页面加载完毕向后端查询用户的信息
    $.get("/api/v1.0/user", function (resp) {
        console.log(resp)
        if (resp.errno == "0") {
            // 设置头像
            $("#user-avatar").attr("src", resp.data.avartar_url)
            // 设置名字
            $("#user-name").val(resp.data.name)

        } else if (resp.errno == "4101") {
            location.href = "/"

        } else {
            alert(resp.errmsg)

        }


    })

    //管理上传用户头像表单的行为
    $("#form-avatar").submit(function (e) {
        e.preventDefault()

        $(this).ajaxSubmit({
            url: "/api/v1.0/user/avatar",
            type: "post",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {

                if (resp.errno == "0") {

                    $("#user-avatar").attr("src", resp.data)
                } else if (resp.errno == "4101") {
                    location.href = "/"

                } else {

                    alert(resp.errmsg)

                }

            }

        })

    })


    // TODO: 管理用户名修改的逻辑
    $("#form-name").submit(function (e) {
        e.preventDefault()
        var name = $("#user-name").val()
        if (!name) {
            $(".error-msg").show()
            return
        }
        $(".error-msg").hide()


        params = {"name": name}

        $.ajax({
            url: "/api/v1.0/user/name",
            type: "post",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            contentType: "application/json",
            data: JSON.stringify(params),
            success: function (resp) {

                if (resp.errno == "0") {

                    showSuccessMsg()
                } else if (resp.errno == "4101") {
                    location.href = "/"

                } else {

                    alert(resp.errmsg)

                }

            }

        })

    })


})

