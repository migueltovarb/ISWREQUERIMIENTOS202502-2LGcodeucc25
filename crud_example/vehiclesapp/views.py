from django.shortcuts import render, HttpResponsePermanentRedirect, get_object_or_404

# Create your views here.

#relative import of forms
from .models import vehiculo
from .forms import vehiculoForm

def create_view(request):
    context ={}
    form = vehiculoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return HttpResponsePermanentRedirect("/")
    context['form']= form
    return render(request, "create_view.html", context)

def list_view(request):
    context ={}
    context["dataset"] = vehiculo.objects.all()
         
    return render(request, "list_view.html", context)

def update_view(request, id):
    context ={}
    obj = get_object_or_404(vehiculo, id=id)
    form = vehiculoForm(request.POST or None, instance = obj)
    if form.is_valid():
        form.save()
        return HttpResponsePermanentRedirect("/")
    context["form"] = form
    return render(request, "update_view.html", context)

def delete_view(request, id):
    context ={}
    obj = get_object_or_404(vehiculo, id=id)
    if request.method =="POST":
        obj.delete()
        return HttpResponsePermanentRedirect("/")
    return render(request, "delete_view.html", context)