const form = $(".primary_form");
const formError = $("#non_field_error");
const formLegend = $(".form_legend");
const submitButton = $("#submit_primary");
const errors = $(".errorlist")
const isErrors = errors.text().trim().length > 0
const username = $("#username");
const email = $("#email");
const password = $("#password");
const passwordToggle = $(".password_toggle");
const randomPassword = $("#random_password");
const usernameError = username.parents(".field_div").siblings(".errorlist").children("div.error").eq(0);
const emailError = email.parents(".field_div").siblings(".errorlist").children("div.error").eq(0);
const passwordError = password.parents(".field_div").siblings(".errorlist").children("div.error").eq(0);
const usernamePostError = username.parents(".field_div").siblings(".errorlist").children("div.error").slice(1);
const emailPostError = email.parents(".field_div").siblings(".errorlist").children("div.error").slice(1);
const passwordPostError = password.parents(".field_div").siblings(".errorlist").children("div.error").slice(1);
const emailErrorText = emailError.children("span")
const usernameErrorText = usernameError.children("span")
const passwordErrorText = passwordError.children("span")
const usernameSymbol = username.siblings("span.validate_symbol");
const emailSymbol = email.siblings("span.validate_symbol");
const passwordSymbol = password.siblings("span.validate_symbol");

$(document).ready(function()
{
  if(isErrors)
  {
    check_post_errors();
  }
  passwordToggle.on('click', function()
    {
      toggle_password($(this).siblings("input"));
    });
  randomPassword.click(function()
  {
    // globalThis.focusing=this.id;
    password.val(generatePassword(16)).trigger("input");   
  })
})

function check_username(data)
{
  if(data.username_null)
  {
    return;
  }
  else if(data.username_error)
  {
    username_error(data.username_error);
  }
}
  
function check_email(data)
{

  if(data.email_null)
  {
    return;
  }
	else if(data.email_error)
  {
    email_error(data.email_error);
  }
}
  
function check_password(data)
{
  if(data.password_null)
  {
    return;
  }
  else if(data.password_error)
  {
    password_error(data.password_error);
  }
}

function generatePassword(length)
{
  var charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012345678\
9!@#$%^&*(()_+}]{[~",
  value = "";
  for(var i = 0, n = charset.length; i < length; ++i)
  {
    value += charset.charAt(Math.floor(Math.random() * n));
  };
    return value;
}

function check_post_errors()
{
  var fieldErrors = $(document.querySelectorAll(".form-group .form-group .errorlist")).filter(function()
  {
    return $(this).text().trim().length > 0;
  })
  var multiErrors = fieldErrors.filter(function(){
    return $(this).children().length > 1
  })

  if(formError.children(errors).length > 0)
  {
    formLegend.css({"margin-bottom":0});
    if($("div.error:contains(reCAPTCHA)").length > 0)
    {
      $("#recaptcha_v2").attr("data-sitekey","6LfDxNsZAAAAAFokK2IQeigtINMiV9D1RtK54ozM");
  		$("#recaptcha_v2").css({"display": "inline"});
    }
  }

  if(fieldErrors.length > 0)
  {
  	fieldErrors.siblings(".field_div").children("input").addClass("field_invalid");
    var firstError = fieldErrors.first();
    firstError.siblings(".field_div").children("input").select();
    if(multiErrors.length > 0)
    {
      multiErrors.children(".error:not(:last-child)").css({"border-radius":"0"})
    }
  }
}

function username_error(message)
{
	username.addClass("field_invalid").removeClass("field_valid");
	usernameErrorText.html(message);
	usernameError.slideDown('fast');
	usernamePostError.slideUp("fast");
	usernameSymbol.css({"display": "none"});
	return;
}

function password_error(message)
{
  password.addClass("field_invalid").removeClass("field_valid");
	passwordErrorText.html(message);
	passwordError.slideDown('fast');
	passwordPostError.slideUp("fast");
	passwordSymbol.css({"display": "none"});
	return;
}

function email_error(message)
{
  email.addClass("field_invalid").removeClass("field_valid");
  emailErrorText.html(message);
  emailError.slideDown('fast');
  emailPostError.slideUp('fast');
  emailSymbol.css({"display": "none"});
  return;
}

function toggle_password(field)
{
  (field.siblings(".password_toggle").toggleClass("fa-eye fa-eye-slash"));
  if (field.attr("type") === "password")
  {
    field.attr("type", "text")
  }
  else
  {
    field.attr("type", "password")
  }
}

// validate google recaptcha v3 token
grecaptcha.ready(function ()
{
	$('.primary_form').submit(function(e)
	{
		var form = this;
		e.preventDefault();
		grecaptcha.execute('6LdN7QsaAAAAAPNy5Fr52O3zrV6JQ-d-j4Uookcf', {action: 'register'})
		.then(function(token)
		{
			$('#recaptcha_v3').val(token);
			form.submit()
		});
	})
});