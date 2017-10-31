#coding:utf-8

from django import forms
from .models import Comments

#Django 的表单类必须继承自 forms.Form 类或者 forms.ModelForm 类
#表单对应有一个数据库模型（评论表单对应着评论模型），最好使用 ModelForm 类
#model = Comment 表明这个表单对应的数据库模型是 Comments 类
class CommentsForm(forms.ModelForm):
	class Meta:
		model = Comments
		fields = ['name', 'email', 'url', 'text']