$(document).ready(function()
{
  password.change(function()
  {
    if(!password.hasClass("changed"))
    {
      password.addClass("changed");
      globalThis.focusing=this.id;
      validatePassword();
    }
	})
  form.on('input',".changed",function()
  {
    globalThis.focusing=this.id;
    validatePassword();
  })

  randomPassword.click(function()
    {
      globalThis.focusing=this.id;
      password.val(generatePassword(16));
      validatePassword();
    })
});

function validatePassword()
{$.ajax(
  {
    url: '/ajax/validate_registration/',
    data:
    {
      'password': password.val(),
    },
    dataType: 'json',
    success: function (data)
    {
      if (data.password_pass)
      {
        submitButton.prop('disabled', false);
        password.removeClass("field_invalid");
        passwordError.slideUp("fast");
        passwordPostError.slideUp("fast");
      }
      else
      {
        submitButton.prop('disabled', true);
        password.focus();
        check_password(data);
      }
    }
  });
}









