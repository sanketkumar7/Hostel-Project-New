from django.urls import path
from . import views
urlpatterns=[
    path('sign-in',views.sign_in_view,name='sign_in_page'),
    path('set-hostel',views.set_hostel_view,name='set_hostel_page'),
    path('create-new-account',views.create_new_account_view,name='registration'),
    path('dashboard',views.homepage_view,name='homepage'),
    path('log-out',views.logout_view,name='logout_page'),
    path('view-block/<int:id>/<int:user_id>',views.block_details_view,name='view_block_page'),
    path('delete-block/<int:id>/<int:user_id>',views.delete_block_view,name='delete_block_page'),
    path('all-enrolled',views.all_enrolled_persons_view,name='all_enrolled_persons'),
    path('all-leaved',views.all_leaved_persons_view,name='all_leaved_persons'),
    path('delete-leaved/<int:id>',views.delete_leaved_person_view,name='delete_leaved_person'),
    path('in-out/',views.in_out_view,name='in_out'),
    path('in-out/<str:date>',views.in_out_view,name='in_out_date'),
    path('delete-in-out/<int:id>',views.delete_in_out_view,name='delete_in_out'),
    path('all-visitors',views.all_visitors_view,name='all_visitors'),
    path('all-visitors/<str:date>',views.all_visitors_view,name='all_visitors'),
    path('visitor-out-time/<int:id>',views.visitor_out_time_view,name='visitor_out_time'),
    path('all-revenue',views.all_revenue_view,name='all_revenue'),
    path('profile',views.member_profile_view,name='member_profile'),

    # ajax requests
    path('add-block',views.ajax_request_add_block_details_view,name='ajax_add_block_details'),
    path('add-person',views.ajax_request_add_person_to_bed_view,name='add_person_to_bed'),
    path('update-person',views.ajax_request_update_person_to_bed_view,name='update_person_to_bed'),
    path('deallocate-person',views.ajax_request_deallocate_person_from_bed_view,name='deallocate_person_from_bed'),
    path('retrieve-bed-details',views.ajax_request_retrive_bed_details_view,name='retrieve_bed_details'),
    path('update-block-name',views.ajax_request_update_block_name_view,name='update_block_name'),
    path('add-bed',views.ajax_request_add_bed_to_room_view,name='add_bed_to_room'),
    path('remove-bed',views.ajax_request_remove_bed_from_room_view,name='remove_bed_from_room'),
    path('retrieve-person-details',views.ajax_request_retrieve_person_details_view,name="in_modal_retrieve_details"),
    path('in-out-in-entry',views.ajax_request_add_in_entry_view,name="in_out_in_entry"),
    path('in-out-out-entry',views.ajax_request_add_out_entry_view,name='in_out_out_entry'),
    path('add-visitors',views.ajax_request_add_visitor_view,name='add_visitors_detail'),
    path('update-profile',views.ajax_request_update_profile_view,name='update_profile')

]