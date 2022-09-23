from .forms import *

##################################################################################################################
# General Pages, Processing
##################################################################################################################

def get_basic_context():
    return {'sidebar':SIDEBAR}

def render(context, request=None):
    template = loader.get_template(context["Template"])
    return HttpResponse(template.render(context, request))

@login_required(login_url='login/')
def pages(request):
    context = get_basic_context()
    if request.method == 'POST':
        return form_post(context, request)    
    page_nm = request.path.split('/')[-1]
    if page_nm == '':
        page_nm = 'Dashboard'
    context.update(PAGE_DESIGN[page_nm])
    context['request'] = request
    context['notifications'] = load_notifications()
    return render(context, request)

def delete(request):
    response = {'result':'success'}
    if request.method == 'POST':
        del_str = request.POST['del_str']
        model_nm, pk = del_str.split(':')
        model = MODELS[model_nm]
        obj = model.objects.filter(id=int(pk))
        obj_str = f'{obj}'
        obj.delete()
        add_notification(icon='delete', heading=f'Deleted {model_nm}: {obj_str}')
    else:
        add_notification(icon='delete', heading=f'Delete Failed')
        response = {'result':'fail'}
    return JsonResponse(response)

def render_form(request, name):
    template, meta_forms = GET_META_FORM(request, name)
    return template.render({'meta_forms':meta_forms}, request)


def render_table(request, name):
    context = TABLE_DESIGN[name]
    context['Data'] = MODELS[context['Model']].objects.all()    
    template = loader.get_template(context["Template"])
    return template.render(context, request)


# General form post
def form_post(context, request):
    form_name = request.POST['Form_Name']
    pk = request.POST['PK']
    Redirect_Valid = request.POST['Redirect_Valid']
    Redirect_Invalid = request.POST['Redirect_Invalid']


    form_class = FORMS[form_name]
    instance = GET_FORM_INSTANCE(request, pk, form_class.model)
    form = form_class(data=request.POST, files=request.FILES, instance=instance)

    if form.is_valid():
        m = form.save()
        msg = 'Saved' if instance else f'Created'
        add_notification(icon='save', heading=f'{form_name.capitalize()}', body=f'{m} - {msg}')        
        return redirect(Redirect_Valid)
    
    msg = f'{instance} - Failed to Save' if instance else f'Could not create {form_name.capitalize()}'
    msg2 = '/n'.join([f'{k}:  {v}'for k,v in form.errors.items()])
    add_notification(icon='warn', heading=msg, body=msg2)

    return redirect(Redirect_Invalid)

##################################################################################################################
# @receivers
##################################################################################################################

@receiver(post_save, sender=User)
def create_extended_user(sender, instance, created, **kwargs):
    if created:
        ExtendedUser.objects.create(base_user=instance)

@receiver(post_save, sender=ExtendedUser)
def create_user_extentions(sender, instance, created, **kwargs):
    if created:
        Employee.objects.create(user=instance)
        Shopper.objects.create(user=instance)
        Consignor.objects.create(user=instance)

@receiver(post_save, sender=Order)
def post_save_order(sender, instance, created, **kwargs):
    # If an order was just saved with a manifest file; redirect to manifest file processing
    global receiver_variable
    if instance.manifest_file:
        receiver_variable = {'redirect': f'/manifest-process.html?pk={instance.id}'}
    return

##################################################################################################################
# Special Pages
##################################################################################################################

def home_profile(context, request):
    _forms = [
        ('user-form', UserForm, request.user),
        ('shopper-form', ShopperForm, request.user.shopper),
        ('consignor-form', ConsignorForm, request.user.consignor),
        ('employee-form', EmployeeForm, request.user.employee)
    ]

    if request.method == 'POST':
        submitted_form = request.POST['button']
        for nm, f, i in _forms:

            if submitted_form == nm:
                form = f(data=request.POST, files=request.FILES, instance=i)
                if form.is_valid():
                    add_notification(icon='save', heading=f'{nm.capitalize()}', body=f'{i} - Updated')
                    form.save()
                else:
                    add_notification(icon='warn', heading=f'{nm.capitalize()}', body=f'{i} - Failed to Update')
        return redirect(context['redirect'])
    
    context['forms'] = [(nm, f(instance=i)) for nm, f, i in _forms]
        
    return render(context, request)


def manifest_process(context, request):
    global notifications
    
    myOrder = Order.objects.get(**{Order._pk_:context['pk']})
    df = pd.read_csv(myOrder.manifest_file)
    fields = [
        [['Description', 'description'],['Department', 'department'],['Brand', 'brand'],['Category 1', 'category_1'],['Category 2', 'category_2']],
        [['Quantity', 'quantity'],['Unit Retail', 'unit_retail'],['Ext Retail', 'ext_retail'],['Fulfilled', 'fulfilled'], ['Delivered', 'delivered']]
    ]

    if request.method == 'POST':
        # Delete previous line items

        lines = Order_Line.objects.filter(order_id = myOrder.id).all()
        if len(lines) > 0:
            add_notification(icon='delete', heading=f'Deleted {len(lines)} rows from Order_Line')
            lines.delete()

        posted_fields = {}
        for field_row in fields:
            for lbl, field in field_row:
                if request.POST[field]:
                    posted_fields[field] = request.POST[field]
        for r in df.iterrows():
            kwargs = {'order': myOrder}
            kwargs.update(
                {k: r[1][v] for k,v in posted_fields.items()}
            )
            newOrder_Line = Order_Line(**kwargs)
            newOrder_Line.save()

        add_notification(icon='add', heading=f'Added {df.shape[0]} rows to Order_Line')

        return redirect('/operations-order-view.html')

    else:
        context['template'] = 'manifest-process'        
        context['df'] = df
        context['fields'] = fields
        
    return render(context, request)
