var popoverClicks = 0;
var mouseDown, currentTarget;

$(document).ready(function()
{
  $(".navbar-toggler").click(function()
  {
  	$('#toggle_icon').toggleClass("fa-angle-up fa-angle-down");
  });

  $(".nav_popover").on(
  {
  	"mousedown mouseup":function(e)
  	{
  		mouseDown = e.type === "mousedown";
	},
	"focus":function(e)
	{
		if(mouseDown)
		{
			return;
		}
		else
		{
			popover_display();
		}
	},
	"click":function(e)
	{
		popover_display();
	}

  })

  $(".popover__wrapper").focusout(function(e)
  {
  	if(!$(e.relatedTarget).parents(".popover__wrapper").length > 0)
  	{
  		$("div.popover__content ").css({"display":"none"});
  		popoverClicks = 0;
  	}
  })
})

function popover_display()
{
	popoverClicks++;
	if(popoverClicks % 2 === 1)
	{
		$("div.popover__content ").css({"display":"block"});
	}
	else
	{
		$("div.popover__content").css({"display":"none"});
	}

}
