from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, PropertyViewSet, BookingViewSet,
    PaymentViewSet, ReviewViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'properties', PropertyViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
