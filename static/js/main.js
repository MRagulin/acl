window.STAGING = 'A1'; //описание состояния заполнения формы
let TableRow = `<tr><td class=''><input type='text'class='form-control' 
placeholder='172.16.45.75' id='input__ip' autofocus minlength='7' maxlength='15' size='15' 
pattern='^((\\d{1,2}|1\\d\\d|2[0-4]\\d|25[0-5])\\.){3}(\\d{1,2}|1\\d\\d|2[0-4]\\d|25[0-5])$'>
<span class='validity'></span></td><td class=''>
<input type='text' class='form-control' placeholder='/16' id='input__mask'style='max-width: 110px;' pattern='^((\\d{1,2}'>
<span class='validity'></span></td><td><textarea class='form-control' placeholder='Внутренняя сеть АС' rows='1' id='input_descr' pattern='.{3,}'>
</textarea><span class='validity'></span></td><td><button class='btn btn-danger btn-sm btn-action btn-action-rm ml-3' type='button'>-</button>
<button class='btn btn-success btn-sm btn-action btn-action-add ml-1' type='button'>+</button></td>
</tr>`;

function GetCurrentDate()
{
    //Old SQL style
     var now = new Date();
     var day = ("0" + now.getDate()).slice(-2);
     var month = ("0" + (now.getMonth() + 1)).slice(-2);
     return  now.getFullYear()+"-"+(month)+"-"+(day) ;
    //return new Date().toLocaleDateString();
}



function AddRowTable()
{
       //$(".btn-action-add").click(function(){
       $(".table-ip-internal > tbody:last-child").append(TableRow);
       //$(document).on('click','.btn-action-add',AddRowTable());
 // });
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

    $(".table-ip-internal").delegate('.btn-action-add','click', function() {
    let tr    = $(this).closest('tr')[0];
    $(tr).clone().insertAfter(tr).find('.form-control').val('').attr('placeholder', '');
    });


    $(".table-ip-internal").delegate('.btn-action-rm','click', function() {
    let tr = $(".table-ip-internal tr");
    if ($(tr).length > 2) {
        tr = $(this).closest('tr')[0];
        $(tr).remove();
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
