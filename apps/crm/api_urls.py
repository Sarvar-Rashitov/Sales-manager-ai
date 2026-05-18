from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register("leads", api_views.LeadViewSet, basename="lead")
router.register("contacts", api_views.ContactViewSet, basename="contact")
router.register("companies", api_views.CompanyViewSet, basename="company")
router.register("deals", api_views.DealViewSet, basename="deal")
router.register("tasks", api_views.TaskViewSet, basename="task")
router.register("activities", api_views.ActivityViewSet, basename="activity")

urlpatterns = router.urls
