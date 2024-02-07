from django.contrib import admin
from blog.models import Post, Tag, Comment


class PostAdmin(admin.ModelAdmin):
    raw_id_fields = ['author', 'likes', 'tags']

class TagAdmin(admin.ModelAdmin):
    pass

class CommentAdmin(admin.ModelAdmin):
    list_display = ['text', 'published_at']
    autocomplete_fields = ['author', 'post',]


admin.site.register(Post)
admin.site.register(Tag)
admin.site.register(Comment)