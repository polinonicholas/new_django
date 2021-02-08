$(document).ready(function()
{
  form.on('input',".changed", function()
  {
    globalThis.focusing=this.id;
    validate_register();
  });
  username.change(function()
  {
    if(!username.hasClass("changed"))
    {
      username.addClass("changed");
      globalThis.focusing=this.id;
      validate_register();
    }
  })
  email.change(function()
  {
    if(!email.hasClass("changed"))
    {
      email.addClass("changed")
      globalThis.focusing=this.id;
      validate_register();
    }
  })
  password.on("input", function()
  {
    if(!password.hasClass("changed"))
    {
      password.addClass("changed")
      globalThis.focusing=this.id;
      validate_register();
    }
  })
});
function validate_register()
{$.ajax(
  {
    url: '/ajax/validate_registration/',
    data:
    {
      'username': username.val(),
      'email': email.val()
      ,'password': password.val(),
    },
    dataType: 'json',
    success: function (data)
    {
      if (data.username_pass && data.email_pass && data.password_pass)
      {
        submitButton.prop('disabled', false);
        $(form).find(".register_field").addClass("field_valid").removeClass("field_invalid");
        $(form).find(".errorlist").children("div.error").slideUp("fast");
        $(form).find(".validate_symbol").css({"display": "inline-block"})
        return;
      }
      else
      {
        submitButton.prop('disabled', true);
        if (focusing===email.attr("id"))  
        {
          if(data.email_pass)
          {
            email.addClass("field_valid").removeClass("field_invalid");
            emailError.slideUp("fast");
            emailPostError.slideUp("fast");
            emailSymbol.css({"display": "inline-block"});
          }
          else
          {
            if(data.email_null)
            {
              email.removeClass("field_invalid");
              emailError.slideUp("fast");
              emailPostError.slideUp("fast");
              return;
            }
            email.focus();
            check_email(data);

          }
          if(password.val().length > 0)
          {
            check_password(data)
          }
        }
        else if(focusing===username.attr("id"))
        {
          if(data.username_pass)
          {
            username.addClass("field_valid").removeClass("field_invalid");
            usernameError.slideUp("fast");
            usernamePostError.slideUp("fast");
            usernameSymbol.css({"display": "inline-block"});
          }
          else
          {
            if(data.username_null)
            {
             username.removeClass("field_invalid");
             usernameError.slideUp("fast");
             usernamePostError.slideUp("fast");
             return;
              
            }
            username.focus();
            check_username(data);
          }
          
          if(password.val().length > 0)
          {
            check_password(data);
          }
        }
        else if (focusing===password.attr("id"))
        {
          if(data.password_pass)
          {
            
            password.addClass("field_valid").removeClass("field_invalid");
            passwordError.slideUp("slow");
            passwordPostError.slideUp("slow");
            passwordSymbol.css({"display": "inline-block"});
          }
          else
          {
            if(data.password_null)
            {
              password.removeClass("field_invalid");
              passwordError.slideUp("fast");
              passwordPostError.slideUp("fast");
              return;

            }
            password.focus();
            check_password(data);
          }
        }
      }
    }
  });
}