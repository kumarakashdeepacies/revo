$('#addrecord').click(function () {
	$('#list_view_tab_content').removeClass('show');
	$('#list_view_tab_content').removeClass('active');
	$('#list_view-tab').removeClass('active');
	$('#list_view_tab').attr('aria-selected', 'false');
	$('#create_view_tab_content').addClass('show');
	$('#create_view_tab_content').addClass('active');
	$('#create_view-tab').addClass('active');
	$('#create_view_tab').attr('aria-selected', 'true');
	$('#list_view_tab_content').attr('href', '#create_view_tab_content');
});
