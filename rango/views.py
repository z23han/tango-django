from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query
from django.shortcuts import redirect


def index(request):	
	# request.session.set_test_cookie()
	# Construct a dictionary to pass to the template engine as its context
	# Note the key boldmessage is the same as {{ boldmessage }} in the template!
	# context_dict = {'boldmessage': 'I am bold font from the context'}
	# place the top 5 categories
	# category_list = Category.objects.order_by('-likes')[:5]
	# context_dict = {'categories': category_list}

	# Return a rendered response to send to the client
	# We make use of the shortcut function to make our lives easier
	# Note that the first parameter is the template we wish to use
	# return render(request, 'rango/index.html', context_dict)
	# return HttpResponse("Rango says hey there world!<br/><a href='/rango/about'>About</a>")
	
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]
	context_dict = {'categories': category_list, 'pages': page_list}

	# Get the number of visits, if exists, the value returned is casted to integer
	# visits = int(request.COOKIES.get('visits', '1'))
	visits = request.session.get('visits')

	if not visits:
		visits = 1
	reset_last_visit_time = False

	last_visit = request.session.get('last_visit')
	if last_visit:
		last_visit_time = datetime.strptime(last_visit[:-7], '%Y-%m-%d %H:%M:%S')

		if (datetime.now() - last_visit_time).seconds > 5:
			visits += 1
			reset_last_visit_time = True
	else:
		reset_last_visit_time = True

	# visits can be used for html <p>{{ visits }}</p> for further checking 
	if reset_last_visit_time:
		request.session['last_visit'] = str(datetime.now())
		request.session['visits'] = visits
	context_dict['visits'] = visits

	response = render(request, 'rango/index.html', context_dict)

	return response
'''
	reset_last_visit_time = False
	response = render(request, 'rango/index.html', context_dict)
	# does the cookie last_visit exist? 
	if 'last_visit' in request.COOKIES:
		# yes, it does, and get the cookie's value
		last_visit = request.COOKIES['last_visit']
		# cast the value to python date/time object
		last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

		if (datetime.now() - last_visit_time).seconds > 5:
			visits += 1
			# flag that the cookie last visit needs to be updated
			reset_last_visit_time = True
	else:
		# Cookie last_visit doesn't exist, flag that it should be set
		reset_last_visit_time = True
		context_dict['visits'] = visits

		# obtain response object early so we can add cookie information
		response = render(request, 'rango/index.html', context_dict)

	if reset_last_visit_time:
		response.set_cookie('last_visit', datetime.now())
		response.set_cookie('visits', visits)

	# return response back to the user, updating the cookies 
	return response
'''

def about(request):
	return render(request, 'rango/about.html', {})
	# return HttpResponse("Rango says here is the about page<br/><a href='/rango'>Index</a>")


def category(request, category_name_slug):
	# context dictionary to pass to the template rendering engine
	context_dict = {}
	context_dict['result_list'] = None
	context_dict['query'] = None
	if request.method == 'POST':
		query = request.POST['query'].strip()
		if query:
			# Run the Bing function to get the result list
			result_list = run_query(query)
			context_dict['result_list'] = result_list
			context_dict['query'] = query

	try:
		# if we cannot find the slug-name, get() raises DoesNotExist exception
		category = Category.objects.get(slug=category_name_slug)
		context_dict['category_name'] = category.name

		# retrieve all the pages
		pages = Page.objects.filter(category=category).order_by('-views')
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


def register(request):
	# boolean for telling the template whether registration is successful
	if request.session.test_cookie_worked():
		print ">>>> TEST COOKIE WORKED!"
		request.session.delete_test_cookie()
	register = False

	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			user.set_password(user.password)
			user.save()

			profile = profile_form.save(commit=False)
			profile.user = user

			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			profile.save()
			register = True

		else:
			print user_form.errors, profile_form.errors
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render(request, 'rango/register.html', 
		{'user_form': user_form, 'profile_form': profile_form, 'register': register})


def user_login(request):

	# test if it is a HTTP POST
	if request.method == 'POST':
		# gather user information and password provided
		# request.POST[var] might raise exception
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username=username, password=password)

		# if we have a user object, the details are correct
		if user:
			# is account active? It could have been disabled. 
			if user.is_active:
				# if account is valid and active
				login(request, user)
				return HttpResponseRedirect('/rango/')
			else:
				return HttpResponse("Your rango account is disabled.")
		else:
			# bad login details
			print "Invalid login details: {0}, {1}".format(username, password)
			return HttpResponse("Invalid login details supplied.")
	# if the request is not a HTTP post
	else:
		return render(request, 'rango/login.html', {})

@login_required
def restricted(request):
	return HttpResponse("Since you're logged in, you can see this text!")


# login_required() decorator to ensure onlu those logged in can access view
@login_required
def user_logout(request):
	# since we know the user is logged in, we can just log out
	logout(request)
	return HttpResponseRedirect('/rango/')


def search(request):
	result_list = []

	if request.method == 'POST':
		query = request.POST['query'].strip()

		if query:
			# Run Bing function to get the result list
			result_list = run_query(query)

	return render(request, 'rango/search.html', {'result_list': result_list})


def track_url(request):
	page_id = None
	url = '/rango/'
	if request.method == 'GET':
		if 'page_id' in request.GET:
			page_id = request.GET['page_id']
			try:
				page = Page.objects.get(id=page_id)
				page.views = page.views + 1
				page.save()
				url = page.url
			except:
				pass

	return redirect(url)


@login_required
def like_category(request):

	cat_id = None
	if request.method == 'GET':
		cat_id = request.GET['category_id']

	likes = 0
	if cat_id:
		cat = Category.objects.get(id=int(cat_id))
		cat.likes = likes
		cat.save()
	return HttpResponse(likes)

# helper function to get the cat_list with starts_with and max_results limits
def get_category_list(max_results=0, starts_with=''):
	cat_list = []
	if starts_with:
		cat_list = Category.objects.filter(name__istartswith=starts_with)

	if max_results > 0:
		if len(cat_list) > max_results:
			cat_list = cat_list[:max_results]

	return cat_list


def suggest_category(request):
	cat_list = []
	starts_with = ''
	if request.method == 'GET':
		starts_with = request.GET['suggestion']

	cat_list = get_category_list(8, starts_with)

	return render(request, 'rango/category_list.html', {'cat_list': cat_list})

