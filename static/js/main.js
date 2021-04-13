window.STAGING = 'A1'; //описание состояния заполнения формы
let el_id = 0;
let message =  ['Неправильный IP-адресс',
        'Обратите внимание, возможно указан неправильный IP-адрес, либо он не является внутреннем.',
        'Обратите внимание, возможно указан неправильный IP-адрес, либо он не является внешним.',
        'Это зарезервированный IP-адрес, использовать его нежелательно.',
        'Произошла ошибка при выполнении операции.',
        'Операция выполнена.',
        'Поле IP адресс - нужно заполнить правильными данными',
        'Обратите внимание, необходимо указать по крайней мере один протокол и порт (для транспортного уровня и выше), пример: udp:53, tcp:3306, icmp итд.',
        'Вы действительно хотите удалить?',
        'Неизвестная ошибка'
    ];

const protocols = ['TCP', 'UDP', 'ICMP', 'IGMP', 'IGMPv3', 'RIP', 'RIP2', 'VRRP', 'BGP4', 'NETFLOW'];

function hasNumber(myString) {
  return /\d/.test(myString);
}
function resolvDomain(domain = '', el = null){
        if (domain == '')
            return ''
         let ipform = $(el).closest('td')[0];
             ipform = $(ipform).next();
             ipform = $(ipform).find("input[class*='ip']")[0];
             if (ipform) $(ipform).attr("disable", true);


        $.post("/iptable/domainresolv/", {
                                        domain:  domain,
                                        csrfmiddlewaretoken: '{{ csrf_token }}',
                }

            ).done(function(data){
                try{
                    let status = JSON.parse(JSON.stringify(data));
                    if (status.hasOwnProperty('status'))
                    {
                        status = status['status'];
                    }
                    if (status instanceof Array)
                        {
                            status = status[0];
                        }
                    if (status != 'undefined' && status!= '')
                    {
                             if (status && el)
                                {
                                    if (ipform)
                                    {
                                        $(ipform).val(status);
                                        if (ipform) $(ipform).attr("disable", false);
                                    }
                                    console.log(status);
                                }

                        return status
                    }


                }catch (e) {
                    if (ipform) $(ipform).attr("disable", false);
                    return '';
                }

            }).fail(function(data){
                if (ipform) $(ipform).attr("disable", false);
               return '';
            });

}
function extractUuid(myString)
{
    try
    {
        return myString.match(/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}/)[0];
    }
    catch (e) {
        return '';
    }

}
function deletebyuuid(data=toString(), el = null)
{
    $.post('/acl/remove/', {data}).done(function(data){
                try{
                    let status = JSON.parse(JSON.stringify(data));

                    if (status.hasOwnProperty('status') )
                    {
                        ShowNotify(idx=2, text=status['status']);
                        if (el != null)
                        {
                            try{
                                $(el).remove();
                            } catch (e) {
                                
                            }
                            
                        }
                        return true;
                    } else
                    {
                        ShowNotify(idx=0, text=status['error']);
                    }

                } catch (e) {
                    console.error(status);
                }
            }).fail(function(){
                ShowNotify(idx=0, text='Произошла ошибка при удалении элементов');
            });
    return false;
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
function ShowNotify(idx = 0, text='Error')
{
    if($("#notifyMessage").length < 1)
    {
        if (idx == 0) //Error
        {
            $("body").append("<div id='notifyMessage' class='alert alert-danger shadow rounded' style='text-align:center;vertical-align:middle;width:400px;position:absolute;top:60px;right:30px;margin:20px;display:none;border:1px solid #fd1414;opacity: 0.8;box-shadow: 0 0 10px;z-index:2000;'><i class='fas fa-radiation mr-3'></i>" + text + "</i></div>");
        }
        else if (idx == 1) //Warning
        {
           $("body").append("<div id='notifyMessage' class='alert alert-warning shadow rounded' style='text-align:center;vertical-align:middle;width:400px;position:absolute;top:60px;right:30px;margin:20px;display:none;border:1px solid rgba(198,108,26,0.99);opacity: 0.8;box-shadow: 0 0 10px;z-index:2000;'><i class='fas fa-warning mr-3'></i>" +text + "</i></div>");
        }

        else //Success
        {
             $("body").append("<div id='notifyMessage' class='alert alert-success shadow rounded' style='text-align:center;vertical-align:middle;width:400px;position:absolute;top:60px;right:30px;margin:20px;display:none;border:1px solid rgba(31,151,15,0.99);opacity: 0.8;box-shadow: 0 0 10px;z-index:2000;'><i class='fas fa-anchor mr-3'></i>" +text + "</i></div>");
        }

    }
    else
    {
        $("#notifyMessage").html(text);
    }
    $("#notifyMessage").show('slow');

    let timerId = setTimeout('$("#notifyMessage").hide("slow").remove()',10000);

    $("#notifyMessage").on("click.hide", function(){
        $("#notifyMessage").remove();
        clearTimeout(timerId);
    });

}

$(document).ready(function(){
    $("#notifyMessage").click(function(){
       $(this).hide();
    });

    $(".btn-remove").click(function() {
        if (!confirm(message[8])) return false;
        if (window.location.href.indexOf('history') == -1) {
             let data = extractUuid(window.location.href);
             if (data != '' && data != null)
             {
                  deletebyuuid(data);
                  window.location.href = '/';
             }
              else{
                alert(message[9]);
             }

        }
        else
        {
               $('.table-history input:checkbox:checked').each(function () {
               let data = $(this).attr('data');
               let el = $(this).closest('tr')[0];
               if (data) {
                   if (deletebyuuid(data, el)) {

                   }
               }
               else {
                   alert(message[9]);
               }

    });
        }



        });


    $('.table-history input:checkbox').click(function(){
         ($(this).prop('checked')) ? $(".btn-danger").attr('disabled', false) : $(".btn-danger").attr('disabled', true);

    });
    $(".input__ip__internal").change(function(el){
        if (ValidateIPaddress(this.value) == true) {
            $.getJSON("/acl/checkip/" + this.value + '/',).done(function (data) {
                try
                {
                   let status = JSON.parse(JSON.stringify(data));
                   if (status.ip != true || status.type != 2)
                   {
                            [3, 4, 5].includes(status.type) ? ShowNotify(1, message[3]) : ShowNotify(1, message[1]);
                   }
                }
                catch(e) {  console.error(e);
                };


            })
        }
        $("#notifyMessage").hide("slow")
    });

        $(".input__ip__external").change(function(el){
        if (ValidateIPaddress(this.value) == true) {
            $.getJSON("/acl/checkip/" + this.value + '/',).done(function (data) {
                try
                {
                   let status = JSON.parse(JSON.stringify(data));
                   if (status.ip != true || status.type != 1)
                   {
                           [3, 4, 5].includes(status.type) ? ShowNotify(1,message[3]) : ShowNotify(1,message[2]);
                   }
                }
                catch(e) {  console.error(e);
                };


            })
        }
        $("#notifyMessage").hide("slow")
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

$("input[name*='domain']").change(function(){
      if ($(this).is(":empty")){
          if ($(this).val() == 'any')
              return 0;
          else
            return resolvDomain($(this).val(), $(this));
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
