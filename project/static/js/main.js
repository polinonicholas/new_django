// validate google recaptcha v3 token
grecaptcha.ready(function ()
{
  $('.primary_form')
    .submit(function (e)
    {
      var form = this;
      e.preventDefault()
      grecaptcha.execute('6LdN7QsaAAAAAPNy5Fr52O3zrV6JQ-d-j4Uookcf'
          , {
            action: 'register'
          })
        .then(function (token)
        {
          $('#recaptcha_v3')
            .val(token)
          form.submit()
        });
    })
});
const toggleButton = $("#password_toggle");
const togglePassword = $("input[name*='password']");

$(document).ready(function(){
$('.navbar-toggler').click(function(){
        $('#toggle_icon').toggleClass("fa-angle-up fa-angle-down");
    });

toggleButton.click(function(){
      if (togglePassword.attr("type") === "password"){
        toggleButton.html("HIDE PASSWORD");
        togglePassword.attr("type", "text")
      }
      else{
        toggleButton.html("SHOW PASSWORD");
        togglePassword.attr("type", "password")
      }
    });
});