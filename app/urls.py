from django.urls import path
from .views import detect_body_points, overlay_saree, upload_image


urlpatterns = [
    path('', upload_image, name='upload'),
    path('', detect_body_points, name='detect_body_points'),
    path('', overlay_saree, name='overlay_saree'),
]