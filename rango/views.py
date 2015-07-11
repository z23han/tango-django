from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm

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
		context_dict['category_name_slug'] = category_name_slug
	except Category.DoesNotExist:
		# dont do anything
		pass

	return render(request, 'rango/category.html', context_dict)


def add_category(request):
	# A HTTP POST?
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		# been provided with a valid form yet?
		if form.is_valid():
			# save the new category to the db
			cat = form.save(commit=True)
			print cat, cat.slug
			# call the index() view
			return index(request)
		else:
			print form.errors
	else:
		# If it's not a POST, display the form to enter details
		form  = CategoryForm()
	# Bad form , no form supplied
	return render(request, 'rango/add_category.html', {'form': form})


def add_page(request, category_name_slug):
	# get the category by try/catch approach
	try:
		cat = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		cat = None

	if request.method == 'POST':
		form = PageForm(request.POST)

		if form.is_valid():
			if cat:
				page = form.save(commit=True)
				page.category = cat
				page.views = 0
				page.save()
				return category(request, category_name_slug)
		else:
			print form.errors
	else:
		form = PageForm()

	context_dict = {'form': form, 'category': cat}
	return render(request, '/rango/add_page.html', context_dict)