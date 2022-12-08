$(document).ready(function() {
  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        var csrftoken = Cookies.get('csrftoken');
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });

  $('.language_changer').bind('click', function(e){
    e.preventDefault();

    var lang = $( this ).attr('id');
    Cookies.set('django_language', lang, { expires: 7, path: '/' });

    var form = document.getElementById('formsetLang'+lang);
    $.ajax({
      url: $(form).attr('action'),
      method: "POST",
      data : $(form).serialize(),
      success : function (data){
        window.location='.';
      }
    });
    return false;
  });
});

