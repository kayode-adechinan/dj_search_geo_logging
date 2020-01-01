"""
from core.models import Author, Tag, Post

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

@receiver(post_save, sender=Author)
def author_changed(sender, instance, **kwargs):
    for post in instance.posts.with_documents():
        post.search_vector = post.document
        post.save(update_fields=['search_vector'])


@receiver(m2m_changed, sender=Post.tags.through)
def post_tags_changed(sender, instance, action, **kwargs):
    if action in ('post_add', 'post_remove', 'post_clear'):
        instance.save()

"""