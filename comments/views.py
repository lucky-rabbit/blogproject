#coding:utf-8

from django.shortcuts import render, get_object_or_404, redirect
from blog.models import Post
from .models import Comments
from .forms import CommentsForm

def post_comment(request, post_pk):
	post = get_object_or_404(Post, pk=post_pk)

	 # 只有当用户的请求为 post 时才需要处理表单数据
	if request.method == 'POST':
		# 用户提交的数据存在 request.POST 中，这是一个类字典对象
		# 用这些数据构造了 CommentForm 的实例，这样 Django 的表单就生成了
		form = CommentsForm(request.POST)

		#调用 form.is_valid() 方法，Django 自动检查表单的数据是否符合格式要求
		if form.is_valid():
			# commit=False 仅仅利用表单的数据生成 Comments 模型类的实例，但不保存评论数据到数据库
			comments = form.save(commit=False)

			# 将评论和被评论的文章关联起来
			comments.post = post

			# 最终将评论数据保存进数据库，调用模型实例的 save 方法
			comments.save()

			#当 redirect 函数接收一个模型的实例时，它会调用这个模型实例的 get_absolute_url 方法
			# 然后重定向到 get_absolute_url 方法返回的 URL
			return redirect(post)

		# 检查到数据不合法，重新渲染详情页，并渲染表单的错误
		# 因此我们传文章（Post）、评论列表、表单form给 detail.html
		else:
			#从一（post）查询多（comments）通过‘一.多_set.all()’方法
			comments_list = post.comments_set.all()
			context = {'post': post,
						'form': form,
						'comments_list': comments_list
					}
			return render(request, 'blog/detail.html', context)
	# 不是 post 请求，说明用户没有提交数据，重定向到文章详情页
	return redirect(post)