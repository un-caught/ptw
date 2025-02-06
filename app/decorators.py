from django.http import HttpResponse
from django.shortcuts import redirect

def allowed_users(allowed_roles=[]):
	def decorator(view_func):
		def wrapper_func(request, *args, **kwargs):
			
			group = None
			if request.user.groups.exists():
				group = request.user.groups.all()[0].name
			if group in allowed_roles:
				return view_func(request, *args, **kwargs)
			else:
				return HttpResponse('''
                    <h1>You are not authorized to view this page</h1>
                    <button onclick="window.history.back();">Go Back</button>
                ''')
		return wrapper_func
	return decorator


def unauthenticated_user(view_func):
	def wrapper_func(request, *args, **kwargs):
		if request.user.is_authenticated:
			if request.user.groups.filter(name='staff').exists():
				return redirect('client')
			elif request.user.groups.filter(name='vendor').exists():
				return redirect('client') 
			elif request.user.groups.filter(name='supervisor').exists():
				return redirect('supervisor')
			elif request.user.groups.filter(name='manager').exists():
				return redirect('manager')
			else:
				return redirect('home')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func