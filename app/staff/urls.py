from django.urls import path, include
from rest_framework.routers import DefaultRouter

from staff import views


router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('department', views.DepartmentViewSet)
router.register('employee', views.EmployeeViewSet)

app_name = 'staff'

urlpatterns = [
    path('', include(router.urls))
]
