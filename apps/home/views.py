from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.contrib.auth.models import User
from .models import *
from .forms import *

model_dicts = {
    'dropoff':      (Dropoff, DropoffForm),
    'order':      (Order, OrderForm),
    'liquidator': (Liquidator, LiquidatorForm),
    'store':      (Store, StoreForm),
    'department':      (Department, DepartmentForm),
    'position':      (Position, PositionForm),
    'section':      (Section, SectionForm),
    'employee':      (Employee, EmployeeForm),
    'consignor':      (Consignor, ConsignorForm),
}

def _tmpl(s):
    return loader.get_template(f'home/{s}.html')

def _http(t=None, s=None, c=None, r=None):
    t = _tmpl(s) if t is None else t
    if c is None:
        return HttpResponse(t.render())
    return HttpResponse(t.render(c, r))

def index(request):
  return _http(s='index')

# Page processing
@login_required(login_url="/login/")
def pages(request):

    # Building URL context
    # http://www.ecothrift.us/path/to/menu-model-page.html?key=value&key=value
    url = request.path
    page = url.split('/')[-1]
    page_name, page_ext = page.split('.') if '.' in page else (page, '')
    segments =  page_name.split('-')
    menu, detail = segments[0], segments[-1]
    template = page_name
    instance = None

    # Initialize context
    context_vars = [
        'url', 'page', 'page_name', 'page_ext', 'menu', 'model', 'model_name', 'detail', 'model',
         'instance', 'form_class', 'form','template', 'new_href', 'edit_href', 'redirect', 'items'
    ]
    context = {}
    for v in context_vars: 
        if v in locals(): context[v] = locals()[v]

    # Add Key/Value context
    context.update(request.GET.dict())

    # Building model and form context
    if detail in ('new','edit','view'):
        model_name = segments[-2]
        model, form_class, = model_dicts[model_name]
        template = 'base-view' if detail == 'view' else 'base-edit'
        if detail == 'view':
            new_href = url.replace(f'-view.html','-new.html')
            edit_href = url.replace(f'-view.html','-edit.html?pk=')
            items = model.objects.values()
        else:
            redirect = url.replace(f'-{detail}.html','-view.html')
            if detail == 'new':
                form = form_class()
            else:
                instance = model.objects.get(**{model.pk:context['pk']})
                form = form_class(instance=instance)
        for v in context_vars:
            if v in locals(): context[v] = locals()[v]
        if request.method == 'POST':
            return post_form(request, context)
    elif page_name == 'home-profile':
        return home_profile(request, context)
    
    return basic_page(request, context)

# General template render
def basic_page(request, context):
    return _http(s=context['template'], c=context, r=request)

# General form post
def post_form(request, context):
    if context['instance'] is None:
        context['form'] = context['form_class'](data=request.POST, files=request.FILES)
    context['form'] = context['form_class'](data=request.POST, files=request.FILES, instance=context['instance'])
    if context['form'].is_valid():
        context['form'].save()
        return redirect(context['redirect'])
    else:
        print(context['form'])
    return _http(s=context['template'], c=context, r=request)

#
# This is a bit unordinary because it has multiple forms on the same page.
#
def home_profile(request, context):
    forms_instances = [
        (BasicUserForm, request.user),
        (ShopperForm, request.user.shopper),
        (ConsignorForm, request.user.consignor),
        (EmployeeForm, request.user.employee)
    ]
    context['forms'] = []
    for f, i in forms_instances:
        form = None
        if request.method == 'POST':
            form = f(data=request.POST, files=request.FILES, instance=i)
            if form.is_valid():
                form.save()
            else:
                print(form)
        else:
            form = f(instance=i)
        context['forms'] += [form]
        
    return _http(s='home-profile', c=context, r=request)
