#coding:utf-8

from ..models import Post, Category, Tag
from django import template
from django.db.models.aggregates import Count

register = template.Library()

#最新文章模板标签
#注册并使用模板标签。Django 1.9 后才支持 simple_tag 模板标签
@register.simple_tag
def get_recent_posts(num=5):
	return Post.objects.all()[:num]

#归档文章模板标签
#dates方法返回一个列表, order='DESC' 降序排列,即离当前越近的时间越排前面
@register.simple_tag
def archives():
	return Post.objects.dates('created_time', 'month', order='DESC')

#分类模板标签
@register.simple_tag
def get_categories():
	#只要是两个model类通过ForeignKey或者ManyToMany关联起来，就可以使用annotate方法统计数量
	#引入 count 函数计算分类下的文章数,参数为需要计数的模型的名称
	return Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)

@register.simple_tag
def get_tags():
	return Tag.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)