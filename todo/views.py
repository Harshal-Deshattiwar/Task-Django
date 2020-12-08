from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import Queryform
from .models import Query
from django.utils import timezone
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'todo/home.html')

# Create your views here.
def signupuser(request):
    if request.method == "GET":
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        # Create new user
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')

            except IntegrityError:
                return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'This Username is already taken, please choose a new username' }) 
        else:
            return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'Passwords did not match'}) 

def loginuser(request):
    if request.method == "GET":
        return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html', {'form': AuthenticationForm(), 'error':'Username and password did not match'})
        else:
            login(request, user)
            return redirect('currenttodos')

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

@login_required        
def createquery(request):
    if request.method == "GET":
        return render(request, 'todo/createquery.html', {'form': Queryform()})
    else:
        try:
            form = Queryform(request.POST)
            newquery = form.save(commit=False)
            newquery.user = request.user
            newquery.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createquery.html', {'form': Queryform(), 'error':'Max 100 words for Title'})
@login_required    
def currenttodos(request):
    querys = Query.objects.filter(user=request.user, datecompleted__isnull=True)
    return render (request, 'todo/currenttodos.html', {'querys':querys})

@login_required    
def completedquerys(request):
    querys = Query.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todo/completedquerys.html', {'querys':querys})

@login_required    
def viewquery(request, query_pk):
    query = get_object_or_404(Query, pk=query_pk, user=request.user)
    if request.method == "GET":
        form = Queryform(instance=query)
        return render (request, 'todo/viewquery.html', {'query':query, 'form':form})
    else:
        try:
            form = Queryform(request.POST, instance=query)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/viewquery.html', {'query':query, 'form':form, 'error':'Bad info'})

@login_required    
def completequery(request, query_pk):
    query = get_object_or_404(Query, pk=query_pk, user=request.user)
    if request.method == 'POST':
        query.datecompleted = timezone.now()
        query.save()
        return redirect('currenttodos')

@login_required    
def deletequery(request, query_pk):
    query = get_object_or_404(Query, pk=query_pk, user=request.user)
    if request.method == 'POST':
        query.delete()
        return redirect('currenttodos')
    