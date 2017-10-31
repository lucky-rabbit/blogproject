# coding: utf-8

from django.db import models
from django.contrib.auth.models import User
from django.utils.six import python_2_unicode_compatible
from django.urls import reverse
import markdown
from django.utils.html import strip_tags

#兼容py2解析成中文
@python_2_unicode_compatible
class Category(models.Model):
	name = models.CharField(max_length=100)
	
	def __str__(self):
		return self.name
		
@python_2_unicode_compatible
class Tag(models.Model):
	name = models.CharField(max_length=100)

	def __str__(self):
		return self.name

@python_2_unicode_compatible
class Post(models.Model):
	tittle = models.CharField(max_length=70)
	body = models.TextField()
	#文章创建时间
	created_time = models.DateTimeField()
	#文章最后修改时间
	modified_time = models.DateTimeField()
	#摘要。可以没有，但CharField必须存入数据，blank=true允许空值
	excerpt = models.CharField(max_length=200, blank=True)

	#指定一篇文章只有一个分类，一个分类可以有多篇文章。一（Category）对多（Post），外键设在多方（Post）
	category = models.ForeignKey(Category)

	#一篇文章有多个标签，一个标签有多篇文章，多对多用ManyToManyField。同时指定文章可以没有标签。
	tags = models.ManyToManyField(Tag, blank=True)
	
	#django.contrib.auth是django内置应用，用于处理网站用户注册、登陆等流程
	#User是django.contrib.auth.models导入的已写好的用户模型
	#指定一篇文章只有一个作者，一个作者可以有多篇文章。一（User）对多（Post）,外键设在多方（Post）
	author = models.ForeignKey(User)

	#PositiveIntegerField参数记录阅读量
	views = models.PositiveIntegerField(default=0)

	def __str__(self):
		return self.tittle

	def get_absolute_url(self):
		#'blog:detail'意为 blog 应用下的 name=detail 的视图函数，reverse 函数会去解析对应的 URL		
		#detail对应的规则就是post/（?P<pk>[0-9]+）/，这个正则被Pk替换
		#所以，如果Post的id或pk是77的话，get_absolute_url返回值就是 /post/77/
		#这样Post就生产了自己的URL。在模板index中有应用
		return reverse('blog:detail', kwargs={'pk': self.pk})

	#博客的流量不会很大，偶尔多人同时访问造成的数据误差忽略不计。+1这个工作量最好由Post自身完成
	#update_fields 参数来告诉 Django 只更新数据库中 views 字段的值
	def increase_views(self):
		self.views +=1
		self.save(update_fields=['views'])

	def save(self, *args, **kwargs):
		#没有摘要就实例Markdown类，渲染body文章内容
		if not self.excerpt:
			md = markdown.Markdown(extentions=[
					'markdown.extentions.extra',
					 'markdown.extentions.codehilite',
				])
			#将Markdown文本转为HTML文本，并去掉HTML文本里的HTML标签
			self.excerpt = strip_tags(md.convert(self.body))[:54]

		#调用父类的save方法将数据保存到数据库中
		super(Post, self).save(*args, **kwargs)

	#Django允许在models.Model的子类里定义一个 Meta 的内部类，通过指定一些属性来规定这个类该有的一些特性
	class Meta:
		ordering = ['-created_time']