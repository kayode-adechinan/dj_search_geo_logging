from django_filters import rest_framework as filters
from django.db.models import Q
from core.models import Shop
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point, fromstr
from django.contrib.gis.measure import D
from django.db.models import F
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

#https://docs.djangoproject.com/en/3.0/ref/contrib/gis/db-api/
#http://blog.lotech.org/postgres-full-text-search-with-django.html
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)



class PostFilter(filters.FilterSet):
     search = filters.CharFilter(method="go_search")

     def go_search(self, queryset, name, value):
          query = SearchQuery(value)
          logger.warning('warning info')
          return queryset.annotate(rank=SearchRank(F('search_vector'), query))\
                    .filter(search_vector=query).order_by('-rank')



class ShopFilter(filters.FilterSet):
    near_to= filters.CharFilter(method='get_nearest')

    def get_nearest(self, queryset, name, value):
       #tag_list = value.split(',')
       longitude = -80.191788
       latitude = 25.761681
       user_location = Point(longitude, latitude, srid=4326)

       #queryset = Shop.objects.annotate(distance=Distance('location',user_location)).order_by('distance')

       #location = fromstr("POINT(%s %s)" % (long, lat))
       #return models.Task.objects.filter(end__gt=datetime.datetime.now(), is_taken=False).filter(point__distance_lte=(location, D(m=dist)))


       queryset = queryset.filter(location__distance_lte=(user_location, D(km=7))) # D(mi=20)

       #location = fromstr("POINT(%s %s)" % (long, lat))
            #return models.Task.objects.filter(end__gt=datetime.datetime.now(), is_taken=False).filter(point__distance_lte=(location, D(m=dist)))


     


       return queryset;



