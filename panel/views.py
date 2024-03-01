from django.shortcuts import render

# Create your views here.
def testView(request):
    return render (request, 'panel/index.html')


def loginPage(request):
    return render(request, 'panel/login.html')