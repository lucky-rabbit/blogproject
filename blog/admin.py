#coding:utf-8

from django.contrib import admin
from .models import Post, Category, Tag

#定制后台显示效果并注册
class PostAdmin(admin.ModelAdmin):
	list_display = ['tittle', 'created_time', 'modified_time', 'category', 'author' ]
		
admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Tag)
