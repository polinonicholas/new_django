$(document).ready(function()
{
  email.change(function()
  {
    if(!email.hasClass("changed"))
    {
      email.addClass("changed")
      globalThis.focusing=this.id;
      validate_reset();
    }
  })
  
  form.on('input',".changed",function()
  {
    globalThis.focusing=this.id;
    validate_reset();
  }) 
});

function validate_reset()
{
  $.ajax(
  {
    url: '/ajax/validate_registration/',
    data:
    {
      'email': email.val(),
    },
    dataType: 'json',
    success: function(data)
    {
      if(data.email_pass)
      {
        submitButton.prop('disabled', false);
        email.removeClass("field_invalid");
        emailError.slideUp("fast");
        emailPostError.slideUp("fast");
      }
      else
      {
        email.focus();
        submitButton.prop('disabled', true);
        check_email(data);
      }
    }
  });
}