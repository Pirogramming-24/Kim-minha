from django.shortcuts import render, redirect
from .models import User
from .forms import UserForm

# Create your views here.
def list(request):
    users = User.objects.all()
    context = {
        'users': users
    }
    return render(request, 'users/list.html', context)

def create(request):
    if request.method == 'GET':
        form = UserForm()
        context = {
            'form': form
        }
        return render(request, 'users/create.html', context)
    else:
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('users:list')

def update(request, pk):
    user = User.objects.get(id=pk)

    if request.method == 'GET':
        form = UserForm(instance=user)
        context = {
            'form': form,
            'user': user,
            'pk': pk,
        }
        return render(request, 'users/update.html', context)
    else:
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
        return redirect('users:list')

def delete(request, pk):
    user = User.objects.get(id=pk)
    user.delete()
    return redirect('users:list')