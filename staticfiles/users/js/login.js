$(document).ready(function()
{    
  email.change(function()
  {
    if(!email.hasClass("change"))
    {
      email.addClass("changed")
      globalThis.focusing=this.id;
      validate_login();
    }
  })
  form.on('input',".changed",function()
  {
    globalThis.focusing=this.id;
    validate_login();
  })
  password.on("input", function()
  {
    if(!password.hasClass("changed"))
    {
      password.addClass("changed");
      globalThis.focusing=this.id;
      validate_login();
    }
  })
});
function validate_login ()
{
  $.ajax(
  {
    url: '/ajax/validate_login/', 
    data:
    {
      'email': email.val(),
      'password': password.val(),
    },
    dataType: 'json', 
    success: function(data)
    {
      if (data.email_pass && data.password_pass)
      {   
        submitButton.prop('disabled', false);
        return;
      }
      else
      {
        submitButton.prop('disabled', true);
        return;
      }
    }
  });
}