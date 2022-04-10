from django.contrib import admin
from django.urls import path, include
from books import views
from django.views.generic import RedirectView

urlpatterns = [
    # path('', views.index,name='index'),
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/library/', permanent=True)),
    path('auth/', include('social_django.urls', namespace='social')),
    path('library/', include('books.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
