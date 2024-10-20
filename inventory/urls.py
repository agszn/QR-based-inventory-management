from unicodedata import name
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

app_name = 'inventory'

urlpatterns = [

    path('sensor_data/', views.sensor_data, name='sensor_data'),

    path('', views.item_list, name='item_list'),
    path('item/<int:pk>/', views.item_detail, name='item_detail'),
    path('item/create/', views.item_create, name='item_create'),
    path('item/<int:pk>/update/', views.item_update, name='item_update'),
    path('item/<int:pk>/delete/', views.item_delete, name='item_delete'),

    path('generate-qr/<int:item_id>/', views.generate_qr, name='generate_qr'),

    path('view_images/', views.view_images, name='view_images'),
    path('delete_image/<str:image_name>/', views.delete_image, name='delete_image'),
    path('hide_image/<str:image_name>/', views.hide_image, name='hide_image'),
    path('show_all_images/', views.show_all_images, name='show_all_images'),

    path('scan_qr_codes/', views.display_qr_content, name='scan_qr_codes'),
    path('receive_checked_values/', views.receive_checked_values, name='receive_checked_values'),

     # URL for listing all scanned items
    path('itemsscanned/', views.item_list, name='item-list'),
    # URL for viewing details of a single scanned item
    path('itemsscanned/<int:pk>/', views.item_detail, name='item-detail'),
    # URL for creating a new scanned item
    path('itemsscanned/create/', views.item_create, name='item-create'),
    # URL for updating details of an existing scanned item
    path('itemsscanned/<int:pk>/update/', views.item_update, name='item-update'),
    # URL for confirming deletion of an existing scanned item
    path('itemsscanned/<int:pk>/delete/', views.item_delete, name='item-delete'),
    # URL for filtering scanned items (optional)
    path('itemsscanned/filter/', views.item_filter, name='item-filter'),

    path('analytics/', views.graph_view, name='analytics'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
