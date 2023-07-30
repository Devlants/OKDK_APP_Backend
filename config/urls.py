from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path("account/",include("account.urls")),
    path("coffee/",include("coffee.urls")),
    path("order/",include("order.urls")),
    path("payment/",include("payment.urls")),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
