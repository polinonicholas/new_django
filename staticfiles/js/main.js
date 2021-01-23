const navButton = $('.navbar-toggler');
const navIcon = $('#toggle_icon');
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
navButton.click(function(){
        navIcon.toggleClass("fa-angle-up fa-angle-down");
    });

});
