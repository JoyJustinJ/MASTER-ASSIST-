/**
 * ER4U AI Bill Upload — Login API JavaScript
 * Source: https://er4uepplus.in/er4u/aibillupload/login_js/login-api.js
 * Extracted verbatim
 */

async function loginLaravelAppThenContinue() {
    const data = {
        username: $("input[name='txtUserName']").val(),
        password: $("input[name='txtPassword']").val()
    };

    try {
        const response = await fetch('newapp/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'same-origin',
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            console.log("App Login Success");
            continueAfterLogin(result.user);
        } else {
            console.log("App Login Failed");
        }

    } catch (error) {
        console.error("Error during login:", error);
    }
}

function continueAfterLogin(user) {
}

let timerOn = true;

function userLogin(){
    $(".btn-er4u-login").find("i").removeClass("fa-sign-in").addClass("fa-cog fa-spin");

    loginLaravelAppThenContinue();

    setTimeout(() => {
        $.ajax({
            url: "login1.php",
            method: "POST",
            data:new FormData($("#form")[0]),
            contentType:false,
            processData:false,
            success: function(response) {
                $(".btn-er4u-login").find("i").removeClass("fa-cog fa-spin").addClass("fa-sign-in");

                try{
                    response = $.parseJSON(response);
                    if(response.status == "200"){
                        Swal.fire({
                            title: response.message,
                            icon: "success",
                            draggable: true
                        });
                        if(localStorage.getItem("get_pay_mode_1")!=null){
                            localStorage.removeItem("get_pay_mode_1");
                        }
                        if(localStorage.getItem("country_state")!=null){
                            localStorage.removeItem("country_state");
                        }
                        if(localStorage.getItem("state_district")!=null){
                            localStorage.removeItem("state_district");
                        }
                        window.location.href = "welcome.php";
                    }else if(response.status == "203"){
                        $.ajax({
                            url: "api-loginotp.php",
                            method: "GET",
                            data:{"Token":response.Token},
                            success: function(response_os) {
                                try{
                                    response_otp = $.parseJSON(response_os);
                                    if(response_otp.status == "200"){
                                        Swal.fire({
                                            title: response_otp.message,
                                            icon: "success",
                                            draggable: true
                                        });
                                        $("#tokenid").val(response_otp.token);
                                        $("#replace_mobno").html(response_otp.mobile);

                                        $(".popup").fadeIn(500);
                                        timer(120);
                                    }else{
                                        Swal.fire({
                                            icon: "error",
                                            text: response_otp.message,
                                        });
                                    }
                                }catch(err2){
                                    console.log(err2);
                                    alert(response_os);
                                }
                            }
                        });

                    }else if(response.status == "209"){

                        Swal.fire({
                            icon: "error",
                            text: response.message,
                            showDenyButton: false,
                            showCancelButton: true,
                            confirmButtonText: "Logout from all device",
                        }).then((result) => {
                            if (result.isConfirmed) {
                                $.ajax({
                                    url: "logout_from_all_device.php",
                                    method: "GET",
                                    data:{"Token":response.Token,"status":"Ajax"},
                                    success: function(response_os) {
                                        try{
                                            response_otp = $.parseJSON(response_os);
                                            if(response_otp.status == "200"){
                                                Swal.fire("Successfully Logout From All Devices! Login Again.", "", "success");
                                            }
                                        }catch(err2){
                                            console.log(err2);
                                            alert(response_os);
                                        }
                                    }
                                });
                            }
                        });
                    }
                    else{
                        Swal.fire({
                            icon: "error",
                            text: response.message,
                        });
                    }
                }catch(err2){
                    console.log(err2);
                    alert(response);
                }
            }
        });
    }, 1500);
}

function timer(remaining) {
    var m = Math.floor(remaining / 60);
    var s = remaining % 60;

    m = m < 10 ? '0' + m : m;
    s = s < 10 ? '0' + s : s;
    document.getElementById('timer').innerHTML = m + ':' + s;
    remaining -= 1;

    if(remaining >= 0 && timerOn) {
        setTimeout(function() {
            timer(remaining);
        }, 1000);
        return;
    }
    if(!timerOn) {
        return;
    }
    document.getElementById('timer').innerHTML = "<a href='javascript: void(0)' class='resend_otp'>Resend OTP</a>";
}

$(document).ready(function() {
    $("#form").submit(function(e) {
        e.preventDefault();
        userLogin();
    });
    $(document).on("click", ".resend_otp", async function(){
        $.ajax({
            url: "api-loginotp.php",
            type: "POST",
            data:{"Token":$("#tokenid").val(),"status": "resend"},
            success: function(data){
                try{
                    response_os = $.parseJSON(data);
                    if(response_os.status == "200"){
                        Swal.fire({
                            title: response_os.message,
                            icon: "success",
                            draggable: true
                            });
                    }else{
                        Swal.fire({
                            icon: "error",
                            text: response_os.message,
                            });
                    }
                }catch(err2){
                    console.log(err2);
                    alert(response_os);
                }
            }
        })
        timer(120);
    });
});
