const form  = $("#recaptcha_form");
const formError = $("#non_field_error");
const submitButton = $(".submit_register");

const username = $("#id_username");
const usernameError = $("#id_username").parents(".field_div").siblings(".error_div").children("div.error");
const usernameSymbol = $("#id_username").siblings("span.validate_symbol");

const email = $("#id_email");
const emailError = $("#id_email").parents(".field_div").siblings(".error_div").children("div.error");
const emailSymbol = $("#id_email").siblings("span.validate_symbol");

const password1 = $("#id_password1");
const password1Error = $("#id_password1").parents(".field_div").siblings(".error_div").children("div.error");
const password1Symbol = $("#id_password1").siblings("span.validate_symbol");

$(document)
  .ready(function ()
  {
    check_recaptcha_fail();
    // prevent no script element space
    $("#noscript")
        .css(
        {
          "display": "none"
        });
    // refresh page if accessed through browser history
    if(performance.navigation.type == 2)
    {
        location.reload(true)
    };
    // add error to username field on initial focus
    if(!username.hasClass("field_valid")){
        username.addClass("field_invalid").removeClass("field_valid");
        usernameError.html("Letters, digits, and underscores only, please.").css({"display":"block"});
        }

// if any fields change, ajax call
$(".register_field")
  .keyup(function ()
  {
    $.ajax(
    {
      url: '/ajax/validate_registration/'
      , data:
      {
        'username': username.val()
        , 'email': email.val()
        , 'password1': password1.val()
      , }
      , dataType: 'json'
      , success: function (data)
      {
        console.log(data);
        // if all fields are valid, disable submit button, add classes to PW
        if (data.username_pass && data.email_pass && data
          .password_pass && password1.val().length > 7)
        {
          submitButton
            .prop('disabled', false);
            // hide "please complete form text"
            $("#complete_request").html('By signing up, you agree to our <a href="#">terms of service</a> and <a href="#">privacy policy</a>.');
            password1Error.css({"display": "none"});
            password1.addClass("field_valid").removeClass("field_invalid");
            toggleButton.css({"display":"inline-block"});
            password1Symbol.css({"display": "inline-block"});
            username.prop("disabled", false);
            email.prop("disabled", false);
            password1.prop("disabled", false);
            // unneccesary?
            emailError.css({"display": "none"});
            usernameError.css({"display": "none"});
            usernameSymbol.css({"display": "inline-block"});
            emailSymbol.css({"display": "inline-block"});
            username.addClass("field_valid").removeClass("field_invalid");
            email.addClass("field_valid").removeClass("field_invalid");
            return;
        }
        // if any fields invalid, disable submit button
        else{submitButton
            .prop('disabled', true);}
        // must improve logic
        if (!data.username_pass || data.username_pass){
          check_username(data);
        }
        else{
          email.prop("disabled", true);
          password1.prop("disabled", true);
        }
        // if username valid, unlock email input, else disable
        if (data.username_pass){
          check_email(data);
        }
        else{
          email.prop("disabled", true);
          password1.prop("disabled", true);
        }
        // if username and email valid, unlock password input, else disable
        if (data.username_pass && data.email_pass) {
          check_password1(data);          
        }
        else{
          password1.prop("disabled", true);
        }
      }
    });
  });
});
function check_username(data){
  // if the username field is valid
  if(data.username_pass){
    username.addClass("field_valid").removeClass("field_invalid");
    usernameError.css({"display": "none"});
    usernameSymbol.css({"display": "inline-block"});
    email.prop("disabled", false);
    if(!data.email_pass){
      // email.focus();
      return;
    }
    else if(!data.password_pass){
      // password1.prop("disabled", false).focus();
      password1.prop("disabled", false);
      return;
    }
  }
  // if the username field has errors
  else {
    if(!data.username_valid){
      username.addClass("field_invalid").removeClass("field_valid");
      usernameError.html(data.username_invalid).css({"display":"block"});
      usernameSymbol.css({"display": "none"});
      username.focus();
      return;
    }
    else if (data.username_taken){
      username.addClass("field_invalid").removeClass("field_valid");
      usernameError.html(data.username_error).css({"display":"block"});
      usernameSymbol.css({"display": "none"});
      username.focus();
      return;
    }
    else if (data.username_profane){
      username.addClass("field_invalid").removeClass("field_valid");
      usernameError.html(data.username_has_profanity).css({"display":"block"});
      usernameSymbol.css({"display": "none"});
      username.focus();
      return;
    }
  }
}

function check_email(data){
  // if the email field is valid
  if (data.email_pass){
    
    email.addClass("field_valid").removeClass("field_invalid");
    emailError.css({"display": "none"});
    emailSymbol.css({"display": "inline-block"});
    password1.prop("disabled", false);

    if (!data.username_pass){
      username.prop("disabled", false);
      // username.prop("disabled", false).focus();
      return;

    }
    else if (!data.password_pass){
      // password1.focus();
      return;
    }
  }
  // if email field has errors
  else{
    if(!data.email_valid){
      email.addClass("field_invalid").removeClass("field_valid");;
      emailError.html(data.email_invalid).css({"display":"block"});
      emailSymbol.css({"display": "none"});
      // email.focus();
      return;
    }
    else if(data.email_taken){
      email.addClass("field_invalid").removeClass("field_valid");
      emailError.html(data.email_error).css({"display":"block"});
      emailSymbol.css({"display": "none"});
      email.focus();
      return;
    }
  }
}
function check_password1(data){
  // if password field is valid
  if(data.password_pass){
    password1Symbol.css({"display": "inline-block"});
    password1.addClass("field_valid").removeClass("field_invalid");
    toggleButton.css({"display":"inline-block"});
    password1Error.css({"display": "none"});

    if(!data.username_pass){
      // username.prop("disabled", false).focus();
      username.prop("disabled", false);
      return;
    }
    else if(!data.email_pass){
      // email.prop("disabled", false).focus();
      email.prop("disabled", false);
      return;
    }
  }
  // if the password field has an error
  else{
    if (password1.val().length < 8 ){
      password1.addClass("field_invalid").removeClass("field_valid");
      toggleButton.css({"display":"none"});
      password1Error.html(data.password_length_error).css({"display":"block"});
      password1Symbol.css({"display": "none"});
      // password1.focus();
      return;
    }
    else if (data.password_no_alpha){
      password1.addClass("field_invalid").removeClass("field_valid");
      toggleButton.css({"display":"none"});
      password1Error.html(data.password_digit_error).css({"display":"block"});
      password1Symbol.css({"display": "none"});
      password1.focus();
      return;
    }
    else if(data.password_too_similar){
      password1.addClass("field_invalid").removeClass("field_valid");
      toggleButton.css({"display":"none"});
      password1Error.html(data.password_error).css({"display":"block"});
      password1Symbol.css({"display": "none"});
      password1.focus();
      return;
    }
    else if (data.password_too_common){
      password1.addClass("field_invalid").removeClass("field_valid");
      toggleButton.css({"display":"none"});
      password1Error.html(data.password_common).css({"display":"block"});
      password1Symbol.css({"display": "none"});
      password1.focus();
      return;
    }
  }
}

function check_recaptcha_fail(){
  if($("div.error:contains(You did not pass Google's reCAPTCHA v3)").length > 0)
    {
      $("#recaptcha_v2").attr("data-sitekey","6LfDxNsZAAAAAFokK2IQeigtINMiV9D1RtK54ozM");
      $("#recaptcha_v2").css({"display": "inline"});
      username.prop('disabled', false).addClass("field_valid");
      usernameSymbol.css({"display": "inline-block"});
      email.prop('disabled', false).addClass("field_valid");
      emailSymbol.css({"display": "inline-block"});
      password1.prop('disabled', false).focus();
      password1.addClass("field_invalid");
      password1Error.html("Re-enter a strong password, please.").css({"display":"block"});
    }
}