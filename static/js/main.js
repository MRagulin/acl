window.STAGING = 'A1'; //описание состояния заполнения формы

function GetCurrentDate()
{
    //Old SQL style
     var now = new Date();
     var day = ("0" + now.getDate()).slice(-2);
     var month = ("0" + (now.getMonth() + 1)).slice(-2);
     return  now.getFullYear()+"-"+(month)+"-"+(day) ;


    //return new Date().toLocaleDateString();
}
$(document).ready(function(){

    $("#checkbox__real__term").on("click", function(){
        if (this.checked)
        {
            $("#contact__input__term").attr('disabled', true);
        } else
        {
            $("#contact__input__term").attr('disabled', false);
        }

    });
  // $(".btn-create-activity").on("click", function (event){
  //   event.preventDefault();
  //   if (typeof window.STAGING !== 'undefined')
  //   {
  //     alert('Next');
  //     // $('.main').load('/', function (){
  //     //
  //     // });
  //   }
  //   });

});
