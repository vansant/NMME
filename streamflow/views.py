# Create your views here.
from django.http import HttpResponse

def streamflow(request):
    var = 15
    #return HttpResponse("Services Page")
    return HttpResponse("variable="+str(var))

