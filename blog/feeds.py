#coding:utf-8

from django.contrib.syndication.views import Feed
from .models import Post
import sys

'''添加XML格式的的RSS订阅功能'''

reload(sys)
sys.setdefaultencoding('utf8')

class AllPostsRssFeed(Feed):
	tittle = 'Django博客演示项目'
	#通过聚合阅读器跳转到网站的地址
	link = "/"	
	description = 'Django博客演示项目测试文章'

	#需要显示的内容条目
	def items(self):
		return Post.objects.all()

	#聚合器中显示的内容条目的标题
	def item_title(self, item):
		return '[%s] %s' %(item.category, item.tittle)

	def item_description(self, item):
		return item.body
