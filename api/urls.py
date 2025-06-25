from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('products/', views.ProductListCreateAPIView.as_view()),
    path('products/info', views.ProductInfoApiView.as_view()),
    path('products/<int:id>', views.ProductRetrieveUpdateDestroyAPIView.as_view()),
    path('account/', views.UserListCreateAPIView.as_view()),
    # path('orders/', views.OrderListAPIView.as_view()),
    # path('user-orders/', views.UserOrderListAPIView.as_view()),
]

router = DefaultRouter()
router.register('orders', views.OrderViewSet)
urlpatterns += router.urls