/* eslint-disable semi */
/* eslint-disable comma-dangle */
$("[name='name_alert_parent_alert_tag_select']").on(
  'select2:select',
  function () {
    const alertTagSelected = $(this).val();
    const alertParentCard = $('#alert_view_tab_content').find(
      '.alert_parent_card'
    );
    alertParentCard.find('[data-alert_tag]').each(function () {
      if (String(alertTagSelected) === '') {
        $(this).show();
        return;
      }
      if (String($(this).attr('data-alert_tag')) !== String(alertTagSelected)) {
        $(this).hide();
      } else {
        $(this).show();
      }
    });
  }
);
