(function ($) {
  $(function() {
    function replaceQueryParam(param, newval, search) {
      var regex = new RegExp("([?;&])" + param + "[^&;]*[;&]?");
      var query = search.replace(regex, "$1").replace(/&$/, '');

      return (query.length > 2 ? query + "&" : "?") + (newval ? param + "=" + newval : '');
    }

  $('.js-language-selector').change(function(event) {
      event.stopPropagation();
      window.location.search = replaceQueryParam('language', $(this).val(), window.location.search);
    });
    $('.changelist-form-container div.language-selector').prependTo('.changelist-form-container #toolbar');
    $('form#changelist-search').css('float', 'right');
    $('#toolbar').css('min-height', $('#toolbar div.language-selector select').height());
    $('#toolbar.actions-visible').css('float', 'unset');

    $('.js-language-tabs').each(function (i, e) {
      var element = $(e);
      element.data('dirty', false);
      element.parent().find('form input').change(function () {
        element.data('dirty', true);
      });
      element.find('.language_button').click(function(e) {
        if (!element.data('dirty') || confirm(element.data('message'))) {
          // Preserve app_config selection
           window.location.search = replaceQueryParam('language', this.dataset.url, window.location.search);
        }
      });
    });
  });
})(django.jQuery);
