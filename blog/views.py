# coding:utf-8

from django.shortcuts import render, get_object_or_404
from .models import Post, Category, Tag
import markdown
from comments.forms import CommentsForm
from django.views.generic import ListView, DetailView
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension
from django.db.models import Q

#基于类视图的ListView是从数据库中获取某个模型列表数据的
class IndexView(ListView):
	#要获取的模型是 Post
	model = Post
	#指定获取的模型列表数据(Post)保存的变量名,这个变量会被传递给模板
	context_object_name = 'post_list'
	#指定这个视图渲染的模板
	template_name = 'blog/index.html'
	# 指定 paginate_by 属性后开启分页功能，其值代表每一页包含多少篇文章
	paginate_by = 5

	#在类视图中,通过 get_context_data方法以字典方式给模板传递变量
	def get_context_data(self, **kwargs):
		#先拿到父类生成的传递给模板的字典
		context = super(IndexView, self).get_context_data(**kwargs)
		#父类生成的字典中已有paginator、page_obj、is_paginated三个模板变量
		#paginator 是 Paginator 的一个实例，page_obj 是 Page 的一个实例
		paginator = context.get('paginator')
		page = context.get('page_obj')
		is_paginated = context.get('is_paginated')
		#重写pagination_data方法获得显示分页导航条需要的数据，返回一个字典
		pagination_data = self.pagination_data(paginator, page, is_paginated)
		#将这些数据更新到context中
		context.update(pagination_data)
		#返回context，让父类ListView使用这个更新后字典中的模板变量去渲染模板
		return context

	def pagination_data(self, paginator, page, is_paginated):
		if not is_paginated:
			return {}
		#当前页码左、右边连续的页码号，初始值为空
		left = []
		right = []

		# 第一页后、最后页前是否需要显示省略号
		left_has_more = False
		right_has_more = False

		#始终显示首末页。只有当前页紧邻第一页或最后页时，才不需要显示
		first = False
		last = False

		#获得当前页码号
		page_number = page.number
		#获得分页后的总页数
		total_pages = paginator.num_pages
		#获得整个分页页码列表，比如分了四页 [1, 2, 3, 4]
		page_range = paginator.page_range

		#请求首页时
		if page_number ==1:
			#分页页码列表如是 [1, 2, 3, 4]，+2获取的就是right = [2, 3]
			right = list(page_range)[page_number:page_number+2]
			# 此时如果最右边的页码号与最后一页的页码号不连续，即
			if right[-1] < total_pages - 1:
				#就需要显示省略号
				right_has_more = True
			#如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
			#就需要显示最后一页的页码号
			if right[-1] < total_pages:
				last = True

		#请求末页时
		elif page_number == total_pages:
			left = list(page_range)[(page_number -3) if (page_number - 3) >0 else 0:page_number - 1]
			if left[0] >2:
				left_has_more = True
			if left[0] >1:
				first = True

		else:
			left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
			right = list(page_range)[page_number:page_number + 2]
			#是否需要显示末页和之前的省略号
			if right[-1] < total_pages - 1:
				right_has_more = True
			if right[-1] < total_pages:
				last = True
			#是否需要显示首页和之后的省略号
			if left[0] > 2:
				left_has_more = True
			if left[0] > 1:
				first = True

		data = {
			'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
		}

		return data


#DetailView表示从数据库获取模型的一条记录数据
class PostDetailView(DetailView):
	model = Post
	template_name = 'blog/detail.html'
	context_object_name = 'post'

	#只有先调用父类get方法后,才有self.object属性,值为Post模型实例,即被访问的文章post
	def get(self, request, *args, **kwargs):
		response = super(PostDetailView, self).get(request, *args, **kwargs)
		self.object.increase_views()
		#必须返回一个 HttpResponse 对象
		return response

	#覆写 get_object的目的是因为需要对 post 的 body 值进行渲染
	def get_object(self, queryset=None):
		post = super(PostDetailView, self).get_object(queryset=None)
		md = markdown.Markdown(extensions=[
									'markdown.extensions.extra',
									'markdown.extensions.codehilite',
		#美化目录的锚点URL，不使用markdown.extensions.toc，而用TocExtension 的实例
		#slugify 参数可以接受一个函数作为参数，这个函数将被用于处理标题的锚点值
		#django.utils.text 中的 slugify 方法，该方法可以很好地处理中文
									TocExtension(slugify=slugify),
							])
		
		#一旦调用该方法后，实例 md 就会多出一个 toc 属性,值就是内容的目录							])
		post.body = md.convert(post.body)
		# 由于Python 是动态语言,所以把 md.toc 的值赋给 post.toc 属性
		post.toc = md.toc
		return post

	#覆写get_context_data的目的是因为除了将post传递给模板外（已由DetailView完成），
	#还要把评论表单、post 下的评论列表传递给模板
	#这个方法返回值是一个字典
	def get_context_data(self, **kwargs):
		context = super(PostDetailView, self).get_context_data(**kwargs)
		form = CommentsForm()
		comments_list = self.object.comments_set.all()
		context.update({'form':form,
				'comments_list':comments_list
				})
		return context

'''def detail():
	#作用是当传入的 pk对应的 Post在数据库存在时返回post; 如果不存在，返回404
	post = get_object_or_404(Post, pk=pk)

	#阅读量+1
	post.increase_views()

	#导入markdown这样我们在模板中展示 {{ post.body }} 就是渲染过后的 HTML 文本
	#传递的额外参数 extensions是对 Markdown 语法的拓展
	#extra 本身包含很多拓展、 codehilite 是语法高亮拓展、toc 允许我们自动生成目录
	post.body = markdown.markdown(post.body,
								 extensions=[
									'markdown.extensions.extra',
									'markdown.extensions.codehilite',
									'markdown.extensions.toc',
									])
	form = CommentsForm()
	comments_list = post.comments_set.all()
	context = {'post': post,
				'form':form,
				'comments_list':comments_list
			}
	return render(request, 'blog/detail.html', context)'''

#created_time 是 Python 的 date 对象。这里作为函数的参数列表，所以 Django 要求写成两个下划线，即 created_time__year
class ArchivesView(ListView):
	model = Post
	template_name = 'blog/index.html'
	context_object_name = 'post_list'

	def get_queryset(self):
		year = self.kwargs.get('year')
		month = self.kwargs.get('month')
		return super(ArchivesView, self).get_queryset().filter(created_time__year=year,
															   created_time__month=month
															   )

class CategoryView(ListView):
	model = Post
	template_name = 'blog/index.html'
	context_object_name = 'post_list'

	def get_queryset(self):
		#在类视图中，从URL捕获的命名组参数值保存在实例的kwargs属性（字典）里
		#非命名组参数值保存在实例的 args 属性（列表）里
		cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
		return super (CategoryView, self).get_queryset().filter(category=cate)

class TagView(ListView):
	model = Post
	template_name = 'blog/index.html'
	context_object_name = 'post_list'

	def get_queryset(self):
		tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
		return super(TagView, self).get_queryset().filter(tags=tag)

#简单全文搜索,查找含有搜索关键词的文章
def search(request):
	q = request.GET.get('q')
	error_msg = ''

	if not q:
		error_msg = '请输入关键字'
		context = {'error_msg':error_msg}
		return render(request, 'blog/index.html', context)

	post_list = Post.objects.filter(Q(tittle__icontains=q) | Q(body__icontains=q))
	context = {'error_msg':error_msg, 'post_list':post_list}
	return render(request, 'blog/index.html', context)