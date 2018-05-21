function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    var d = new Date().getTime();
    if (window.performance && typeof window.performance.now === "function") {
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
    return uuid;
}

var imageCodeId = ""
var preimageCodeId = ""

// 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
function generateImageCode() {
    // 生成图片的uuid
    imageCodeId = generateUUID()
    // 生成url
    var url = "/api/v1.0/image_code?cur_id=" + imageCodeId + '&pre_id=' + preimageCodeId
    $(".image-code>img").attr('src', url)
    preimageCodeId = imageCodeId

}

function sendSMSCode() {
    // 校验参数，保证输入框有数据填写
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }

    // TODO: 通过ajax方式向后端接口发送请求，让后端发送短信验证码
    var params = {
        "mobile": mobile,
        "image_code": imageCode,
        "image_code_id": imageCodeId
    }
    $.ajax({
        url: "/api/v1.0/sms_code",
        type: "post",
        data: JSON.stringify(params),
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        contentType: "application/json",
        success: function (resp) {
            if (resp.errno == "0") {
                //发送成功
                var iClick = 60

                var t = setInterval(function () {
                    //每一千毫秒刷新一次界面
                    if (iClick == 1) {
                        //倒计时结束
                        // 清除倒计时
                        clearInterval(t)
                        // 重新获取验证码有效
                        $(".phonecode-a").attr("onclick", "sendSMSCode();");
                        $(".phonecode-a").html("获取验证码")
                    } else {
                        iClick = iClick - 1
                        // 正在进行倒计时
                        // 设置倒计时的秒数
                        $(".phonecode-a").html(iClick + "S")

                    }

                }, 1000)

            } else {
                // 发送失败
                generateImageCode()
                // 把可点击时间添加回去
                $(".phonecode-a").attr("onclick", "sendSMSCode();");
                // 再次刷新下验证码
                alert(resp.errmsg)
            }

        }

    })


}

$(document).ready(function () {
    generateImageCode();  // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
    $("#mobile").focus(function () {
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function () {
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function () {
        $("#phone-code-err").hide();
    });
    $("#password").focus(function () {
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function () {
        $("#password2-err").hide();
    });

    //  注册的提交(判断参数是否为空)
    $(".form-register").submit(function (e) {
        e.preventDefault()
        //取出3个单位的值
        var mobile = $("#mobile").val()
        var phonecode = $("#phonecode").val()
        var password = $("#password").val()
        var password2 = $("#password2").val()
        if (!mobile) {
            $("#mobile-err span").html("请输入正确的手机号码");
            $("#mobile-err").show();
            return
        }
        if (!phonecode) {
            $("#phone-code-err span").html("请输入正确的短信验证号码");
            $("#phone-code-err").show();
            return
        }

        if (!password) {
            $("#password-err span").html("请输入密码");
            $("#password-err").show();
            return
        }
        if (password != password2) {
            $("#password2-err span").html("两次输入的密码不一致");
            $("#password2-err").show();
            return
        }
        var params = {
            "mobile": mobile,
            "phonecode": phonecode,
            "password": password
        }
        $.ajax({
            url: "/api/v1.0/users",
            type: "post",
            data: JSON.stringify(params),
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            contentType: "application/json",
            success: function (resp) {
                if (resp.erron == "0") {
                    location.href = "/"
                } else {
                    $("#password2-err span").html(resp.errmsg);
                    $("#password2-err").show();

                }

            }

        })


    })


})
