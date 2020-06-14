from django.shortcuts import render

# Create your views here.

def hello_world(request):
    return render(request, 'hello_world/hello_world.html')
