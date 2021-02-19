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
let el_id = 0;

function hasNumber(myString) {
  return /\d/.test(myString);
}

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

    //.val('').attr('placeholder', '').attr('name', input_name)
    $(".table-ip-internal").delegate('.btn-action-add','click', function() {

    let tr    = $(this).closest('tr')[0];
    let new_name = $('.table-ip-internal tr:first-child').find('.form-control');
    let idx_input = 0;
    //let input_name = $(tr).attr('name') +'_'+ Math.random().toString(36).substr(2, 5)
    $(tr).clone().insertAfter(tr).find('.form-control').each(function() {
        //let name1 = $(tr).find('input:text')[el_id].name;
        try
        {   console.log(new_name[idx_input].name);
            $(this).val('').attr('placeholder', '').attr('name',  new_name[idx_input].name+'_'+el_id.toString());
            idx_input++;
            el_id++;
        }catch (e){
            console.log(e);
        }

    });


    });


    $(".table-ip-internal").delegate('.btn-action-rm','click', function() {
    let all_tr = $(".table-ip-internal tr");
    if ($(all_tr).length > 2) {
        try
        {
            let mom  = $(this).closest('tr').find('.form-control')[0];
            if (!hasNumber($(mom).attr('name'))) //.parentElement.parentElement.nodeName == 'TBODY'
            {
                return false;
            }
        } catch (e)
        {
            console.log('Parent el not find, row remove.');
        }

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
