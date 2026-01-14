from django.urls import path, include
from rest_framework.routers import DefaultRouter

from tenant.views.SlaXView import SLAViewSet, HolidayViewSet, SLAConfigurationViewSet, BusinessHoursViewSet

router = DefaultRouter()
router.register(r'policies', SLAViewSet)
router.register(r'holidays', HolidayViewSet)
router.register(r'business-hours', BusinessHoursViewSet)
router.register(r'config', SLAConfigurationViewSet, basename='sla-config')


urlpatterns = [
    path('', include(router.urls)),
]
