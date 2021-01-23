// validate google recaptcha v3 token
grecaptcha.ready(function ()
{
  $('.recaptcha_form')
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

$(document).ready(function(){
$('.navbar-toggler').click(function(){
        $('#toggle_icon').toggleClass("fa-angle-up fa-angle-down");
    });

});