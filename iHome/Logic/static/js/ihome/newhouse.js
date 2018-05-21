function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');

    //  在页面加载完毕之后获取区域信息
    $.get("/api/v1.0/area", function (resp) {
        if (resp.error == "0") {
            //添加options条目
            // for (var i = 0; i < resp.data.length; i++) {
            //     var aid = resp.data[i].aid
            //     var aname = resp.data[i].aname
            //     // 添加逻辑
            //     $("#area-id").append('<option value="' + aid + '">' + aname + '</option>')
            // }

            var html = template("areas-tmpl", {"areas": resp.data})
            $("#area-id").html(html)

        } else {
            alert(resp.errmsg)
        }

    })

    // TODO: 处理房屋基本信息提交的表单数据
    $("#form-house-info").submit(function (e) {
        e.preventDefault()

        var params = {}
        $(this).serializeArray().map(function (x) {
            params[x.name] = x.value
        })
        var facilities = []

        $(":checkbox:checked[name = facility]").each(function (index, x) {
            facilities[index] = x.value
        })
        params["facility"] = facilities

        $.ajax({
            url: "/api/v1.0/houses",
            type: "post",
            data: JSON.stringify(params),
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (resp) {
                //实现基本信息的隐藏i
                $("#form-house-info").hide()
                //   上传图片的展示
                $("#form-house-image").show()

                $("#house-id").val(resp.data.house_id)


            }

        })

    })

    // TODO: 处理图片表单的数据
    $("#form-house-image").submit(function (e) {
        e.preventDefault()
        $(this).ajaxSubmit({
            url: "/api/v1.0/houses/image",
            type: "post",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            }, success: function (resp) {

                if (resp.errno == "0") {

                    $(".house-image-cons").append('<img src="' + resp.data.image_url + '">')

                } else {
                    alert(resp.errmsg)
                }

            }


        })


    })


})