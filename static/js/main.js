window.STAGING = 'A1'; //описание состояния заполнения формы
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

function IsJsonString(str) {
  try {
    var json = JSON.parse(str);
    return (typeof json === 'object');
  } catch (e) {
    return false;
  }
}

function ValidateIPaddress(ipaddress) {
  if (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(ipaddress)) {
    return (true)
  }
  return (false)
}
function ShowNotify(idx)
{
    let message =  ['Неправильный IP-адресс','Обратите внимание, возможно указан неправильный IP-адрес, либо он не является внутреннем.', 'Обратите внимание, возможно указан неправильный IP-адрес, либо он не является внешним.'];
    if($("#successMessage").length < 1)
    {
        $("body").append("<div id='notifyMessage' class='alert alert-warning' style='text-align:center;vertical-align:middle;width:400px;position:absolute;top:190px;right:30px;margin:20px;display:none;border:1px solid #fd7e14;opacity: 0.8;'><i class='fas fa-radiation mr-3'></i>" + message[idx] + "</i></div>");
    }
    else
    {
        $("#successMessage").html(message[idx]);
    }
    $("#notifyMessage").show('slow');
    setTimeout('$("#notifyMessage").hide("slow")',10000);
}

$(document).ready(function(){

    $(".input__ip__internal").change(function(el){
        if (ValidateIPaddress(this.value) == true) {
            $.getJSON("/acl/checkip/" + this.value + '/',).done(function (data) {
                try
                {
                   let status = JSON.parse(JSON.stringify(data));
                   if (status.ip != true || status.type != 2)
                   {
                           ShowNotify(1) ;
                   }
                }
                catch(e) {  console.error(e);
                };


            })
        }
    });

        $(".input__ip__external").change(function(el){
        if (ValidateIPaddress(this.value) == true) {
            $.getJSON("/acl/checkip/" + this.value + '/',).done(function (data) {
                try
                {
                   let status = JSON.parse(JSON.stringify(data));
                   if (status.ip != true || status.type != 1)
                   {
                           ShowNotify(2) ;
                   }
                }
                catch(e) {  console.error(e);
                };


            })
        }
    });

    $("#upload_file_form").submit(function (event){
               event.preventDefault();
               let ActionUrl = event.currentTarget.action;
               $.ajax({
                 url:ActionUrl,
                 type:'post',
                 enctype: 'multipart/form-data',
                 data: new FormData($('#upload_file_form')[0]),
                 cache: false,
                 contentType: false,
                 processData: false,
                 beforeSend:function(){
                     $(".input--file--label").hide();
                     $("#upload_file_form").append("<div class='spinner-border text-danger' role='status'><span class='sr-only'>Loading...</span></div>");
                 } ,
                 success : function(result){
                   if (typeof result!= 'undefined' && result !== null && result.length > 0)
                   {
                      if (IsJsonString(result))
                      {
                          result = JSON.parse(result);
                          let MessageType = result.hasOwnProperty('ok') ? 'success' : 'warning';
                          $(".content > div>div:nth-child(1)").append("<div class='alert alert-"+MessageType + "'>" + Object.values(result)[0] +  "</div>");
                      }
                   }
                 } ,
                 error:function(data){
                     $(".content > div>div:nth-child(1)").append("<div class='alert alert-danger>При отправке файла произошла ошибка, напишите нам об этом.</div>");
                     },
                 complete:function(){
                     $(".spinner-border").hide();
                     $(".input--file--label").show();
                     $("#upload_file_form").each(function(){
                        this.reset();
                     });
                 } ,
                });
            });


    $("#input--file--upload").on('change', function (e){
        if( this.files && this.files.length > 0 )
        {
            $("#upload_file_form").submit();
        }
    });
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
    let new_name = $('.table-ip-internal tr:first-child').find('.form-control');
    let idx_input = 0;
    $(tr).clone().insertAfter(tr).find('.form-control').each(function() {
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

//Скрывать все элементы с классом alert после x времени
$(function(){
 function hide_alert(){
   $('.alert').fadeOut();
 };
 window.setInterval(hide_alert, 70000);
});


$(".btn-start").click(function(){
        if ($("#flexAgreementCheck:checked").length == 0)
        {
            $("label.form-check-label").css({"border-bottom":" 2px solid red"});
            return false;
        }
});

$("#flexAgreementCheck").click(function(){
        if ($("#flexAgreementCheck:checked").length > 0) {
            $(".btn-start").removeClass('not-active');

        } else
        {
            $(".btn-start").addClass('not-active');
        }
});


});
