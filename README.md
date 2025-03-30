# Trip_logbook_backend

/admin/ django.contrib.admin.sites.index        admin:index
/admin/<app_label>/     django.contrib.admin.sites.app_index    admin:app_list
/admin/<url>    django.contrib.admin.sites.catch_all_view
/admin/auth/group/      django.contrib.admin.options.changelist_view    admin:auth_group_changelist
/admin/auth/group/<path:object_id>/     django.views.generic.base.RedirectView
/admin/auth/group/<path:object_id>/change/      django.contrib.admin.options.change_view        admin:auth_group_change   
/admin/auth/group/<path:object_id>/delete/      django.contrib.admin.options.delete_view        admin:auth_group_delete   
/admin/auth/group/<path:object_id>/history/     django.contrib.admin.options.history_view       admin:auth_group_history  
/admin/auth/group/add/  django.contrib.admin.options.add_view   admin:auth_group_add
/admin/autocomplete/    django.contrib.admin.sites.autocomplete_view    admin:autocomplete
/admin/jsi18n/  django.contrib.admin.sites.i18n_javascript      admin:jsi18n
/admin/login/   django.contrib.admin.sites.login        admin:login
/admin/logout/  django.contrib.admin.sites.logout       admin:logout
/admin/password_change/ django.contrib.admin.sites.password_change      admin:password_change
/admin/password_change/done/    django.contrib.admin.sites.password_change_done admin:password_change_done
/admin/r/<int:content_type_id>/<path:object_id>/        django.contrib.contenttypes.views.shortcut      admin:view_on_site
/api/   rest_framework.routers.APIRootView      api-root
/api/<drf_format_suffix:format> rest_framework.routers.APIRootView      api-root
/api/auth/login/        api.views.DriverLoginView       driver-login
/api/auth/register/     api.views.DriverRegisterView    driver-register
/api/auth/token/refresh/        rest_framework_simplejwt.views.TokenRefreshView token-refresh
/api/compliance/        api.views.ComplianceCheckView   compliance-check
/api/drivers/   api.views.DriverListView        driver-list
/api/logs/      api.views.LogEntryViewSet       log-list
/api/logs/<pk>/ api.views.LogEntryViewSet       log-detail
/api/logs/<pk>\.<format>/       api.views.LogEntryViewSet       log-detail
/api/logs\.<format>/    api.views.LogEntryViewSet       log-list
/api/trips/     api.views.TripViewSet   trip-list
/api/trips/<pk>/        api.views.TripViewSet   trip-detail
/api/trips/<pk>/generate_logs/  api.views.TripViewSet   trip-generate-logs
/api/trips/<pk>/generate_logs\.<format>/        api.views.TripViewSet   trip-generate-logs
/api/trips/<pk>\.<format>/      api.views.TripViewSet   trip-detail
/api/trips\.<format>/   api.views.TripViewSet   trip-list
/api/trucks/    api.views.TruckViewSet  truck-list
/api/trucks/<pk>/       api.views.TruckViewSet  truck-detail
/api/trucks/<pk>\.<format>/     api.views.TruckViewSet  truck-detail
/api/trucks\.<format>/  api.views.TruckViewSet  truck-list