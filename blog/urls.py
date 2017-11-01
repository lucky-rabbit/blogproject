#coding:utf-8

from django.conf.urls import url
from . import views
from blog.feeds import AllPostsRssFeed

指定命名空间,告诉Django这个模块属于blog应用
app_name = 'blog'
urlpatterns = [
	#基于类视图的as_view() 方法将类转换成函数
	url(r'^$', views.IndexView.as_view(), name='index'),
	#(?P<pk>[0-9]+)匹配数字并保存为{pk:99}的字典
	url(r'^post/(?P<pk>[0-9]+)/$', views.PostDetailView.as_view(), name='detail'),
	url(r'^archives/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$', views.ArchivesView.as_view(), name='archives'),
	url(r'^category/(?P<pk>[0-9]+)/$', views.CategoryView.as_view(), name='category'),
	url(r'^tag/(?P<pk>[0-9]+)/$', views.TagView.as_view(), name='tag'),
	url(r'^all/rss/$', AllPostsRssFeed(), name='rss'),
	#url(r'^search/$', views.search, name='search'),
]
