#from django.db import models
from django.contrib.gis.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector
from django.contrib.postgres.aggregates import StringAgg

"""
class PostManager(models.Manager):
    def with_documents(self):
        vector = SearchVector('title', weight='A') + \
                 SearchVector('content', weight='C') + \
                 SearchVector('author__name', weight='B') + \
                 SearchVector(StringAgg('tags__name', delimiter=' '), weight='B')
        return self.get_queryset().annotate(document=vector)
"""

class Author(models.Model):
    name = models.CharField(max_length=50)


class Tag(models.Model):
    name = models.CharField(max_length=20)


class Post(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    tags = models.ManyToManyField(Tag)
    search_vector = SearchVectorField(null=True)

    class Meta:
        indexes = [
            GinIndex(fields=['search_vector'])
        ]

    #objects = PostManager()

    #def save(self, *args, **kwargs):
        #super().save(*args, **kwargs)
        #if 'update_fields' not in kwargs or 'search_vector' not in kwargs['update_fields']:
            #instance = self._meta.default_manager.with_documents().get(pk=self.pk)
            #instance.search_vector = instance.document
            #instance.save(update_fields=['search_vector'])




class Shop(models.Model):
    name = models.CharField(max_length=100)
    location = models.PointField()
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)

    