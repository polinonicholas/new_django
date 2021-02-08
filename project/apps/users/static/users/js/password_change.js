const current_password = $("#current_password");
const currentPasswordError = current_password.parents(".field_div").siblings(".errorlist").children("div.error").eq(0);
const currentPasswordPostError = current_password.parents(".field_div").siblings(".errorlist").children("div.error").slice(1);
const currentPasswordErrorText = currentPasswordError.children("span");
const currentPasswordSymbol = current_password.siblings("span.validate_symbol");
$(document).ready(function()
{
  form.on('input',".changed", function()
  {
    globalThis.focusing=this.id
    validate_change();
  });
  current_password.on("change", function()
  {
    if(!current_password.hasClass("changed"))
    {
      current_password.addClass("changed")
      globalThis.focusing=this.id;
      validate_change();
    }
  })
  password.on("input", function()
  {
    if(!password.hasClass("changed"))
    {
      password.addClass("changed");
      globalThis.focusing=this.id;
      validate_change();
    }
  })
});
function validate_change()
{$.ajax(
  {
    url: '/ajax/validate_pw_change/',
    data:
    {
      'password': password.val(),
      'current_password': current_password.val(), 
    },
    dataType: 'json',
    success: function (data)
    {
      if(data.current_password_pass && data.password_pass)
      {
        submitButton.prop('disabled', false);
        $(form).find("input").removeClass("field_invalid");
        $(form).find(".errorlist").children("div.error").slideUp("fast");
        return;
      }
      else
      {
        submitButton.prop('disabled', true);
        if (focusing===current_password.attr("id"))
        {
          if(data.current_password_pass)
          {
            current_password.removeClass("field_invalid");
            currentPasswordError.slideUp("fast");
            currentPasswordPostError.slideUp("fast");          
          }
          else
          {
            if(data.current_password_null)
            {
              current_password.removeClass("field_invalid");
              currentPasswordError.slideUp("fast");
              currentPasswordPostError.slideUp("fast");
              return;
            }
            current_password.focus();
            check_current_password(data);
          }   
        }
        else if (focusing===password.attr("id"))
        {
          if(data.password_pass)
          {
            password.removeClass("field_invalid");
            passwordError.slideUp("slow");
            passwordPostError.slideUp("slow");
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


function check_current_password(data)
{
  if(data.current_password_null)
  {
    return;
  }
  else if(!data.password_correct)
  {
    current_password_error(data.wrong_password)
  }
}

function current_password_error(message)
{
  current_password.addClass("field_invalid").removeClass("field_valid");
  currentPasswordErrorText.html(message);
  currentPasswordError.slideDown('fast');
  currentPasswordPostError.slideUp("fast");
  currentPasswordSymbol.css({"display": "none"});
  current_password.focus();
  return;
}