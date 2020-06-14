from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'home/home.html')

def welcome(request):
    return render(request, 'home/welcome.html')