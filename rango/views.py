from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from rango.models import Category, Page

def index(request):
	# Construct a dictionary to pass to the template engine as its context
	# Note the key boldmessage is the same as {{ boldmessage }} in the template!
	# context_dict = {'boldmessage': 'I am bold font from the context'}
	# place the top 5 categories
	category_list = Category.objects.order_by('-likes')[:5]
	context_dict = {'categories': category_list}

	# Return a rendered response to send to the client
	# We make use of the shortcut function to make our lives easier
	# Note that the first parameter is the template we wish to use
	return render(request, 'rango/index.html', context_dict)
	# return HttpResponse("Rango says hey there world!<br/><a href='/rango/about'>About</a>")

def about(request):
	return HttpResponse("Rango says here is the about page<br/><a href='/rango'>Index</a>")


def category(request, category_name_slug):
	# context dictionary to pass to the template rendering engine
	context_dict = {}

	try:
		# if we cannot find the slug-name, get() raises DoesNotExist exception
		category = Category.objects.get(slug=category_name_slug)
		context_dict['category_name'] = category.name

		# retrieve all the pages
		pages = Page.objects.filter(category=category)
		# Adds results list to the template context 
		context_dict['pages'] = pages
		# also add category object from db to the context 
		context_dict['category'] = category
	except Category.DoesNotExist:
		# dont do anything
		pass

	return render(request, 'rango/category.html', context_dict)