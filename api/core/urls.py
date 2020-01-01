from django.urls import path

from core import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('shops', views.ShopViewSet)
router.register('author', views.AuthorViewSet)
router.register('posts', views.PostViewSet)
router.register('tags', views.TagViewSet)

urlpatterns = router.urls