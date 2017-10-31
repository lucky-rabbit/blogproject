#coding:utf-8

from haystack import indexes
from .models import Post

#对某个app下的数据进行全文检索，就要在其下建一个search_indexes.py文件
#然后创建一个XXIndex类（XX为含有被检索数据的模型），并且继承SearchIndex和Indexable
class PostIndex(indexes.SearchIndex, indexes.Indexable):
	#设置了document=True的字段名一般约定为text,表示将使用此字段的内容作为索引进行检索
	#use_template=True允许使用数据模板去建立索引的文件，就是索引里面需要存放一些什么东西
	text = indexes.CharField(document=True, use_template=True)

	def get_model(self):
		return Post

	def indexe_querset(self):
		return self.get_model().objects.all()
