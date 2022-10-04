from .html_elements import *

##################################################################################################################
# General Pages, Processing
##################################################################################################################

def get_context(request):
    _context = {
        'request':          request,
        'user':             request.user,
        'Sidebar':          SIDEBAR,
        'Notifications':    LOAD_NOTIFICATIONS(),
        'ExtendedUser':     request.user.extendeduser, 
        'Shopper':          request.user.extendeduser.shopper,       
        'Consignor':        request.user.extendeduser.consignor,
        'Employee':         request.user.extendeduser.employee,
        'PageName':         request.path.split('/')[-1],
        'PageDesign':       PAGE_DESIGN[request.path.split('/')[-1]],
        }
    return _context

@login_required(login_url='login/')
def pages(request):
    if request.path.split('/')[-1] == '': return redirect('/Dashboard')
    context = get_context(request)
    context.update({'Context':context})
    if context['PageDesign']['Type'] == 'Advanced':
        return advanced_page(context)
    return basic_page(context)

def basic_page(context):
    if context['request'].method == 'POST': 
        return form_post(context, context['request'])
    template = loader.get_template(context['PageDesign']['Template'])
    return HttpResponse(template.render(context, context['request']))

def advanced_page(context):
    if context['PageName'] == 'AddOrderItems':        
        context['pk'] = context['request'].GET['pk']
        context['order'] = Order.objects.get(pk=context['pk'])
        context['OrderStr'] = str(context['order'])
        context['Form'] = FORMS(context['request'], 'OrderForm')
    template = loader.get_template(context['PageDesign']['Template'])
    return HttpResponse(template.render(context, context['request']))



##################################################################################################################
# Form POST Handeler
##################################################################################################################

def form_post(context, request):
    form_name, _inst, valid_redirect, invalid_redirect = request.POST.get('FormName'), request.POST.get('Instance'), request.POST.get('RedirectValid'), request.POST.get('RedirectInvalid')
    form = FORMS(request, form_name, _inst)
    model_name = form.Meta.model.__name__
    if form.is_valid():
        m = form.save()
        add_notification(
            icon='save',
            heading=f"{request.POST['FormName']}",
            body=f"{m} - {'Saved' if _inst else f'Created'}"
        )        
        return redirect(valid_redirect)    
    msg_head = f"{_inst} - Failed to Save" if _inst else f"Could not create {model_name}",
    msg_body = "Form Errors:/n"
    msg_body = '/n -'.join([f'{k}:  {v}'for k,v in form.errors.items()])
    add_notification(icon='warn', heading=msg_head, body=msg_body)
    return redirect(invalid_redirect)

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
# Ajax Functions
##################################################################################################################

def process_manifest(request, context):    

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

def delete(request):
    redirect=''
    if request.method == 'POST':
        if 'RedirectValid' in request.POST:
            redirect = request.POST['RedirectValid']
        del_str = request.POST['del_str']
        model_nm, pk = del_str.split(':')
        model = MODELS(model_nm)
        obj = model.objects.get(pk=int(pk))
        obj_str = f'{obj}'
        obj.delete()
        add_notification(icon='delete', heading=f'Deleted {model_nm}: {obj_str}')
    else:
        add_notification(icon='delete', heading=f'Delete Failed')
        return JsonResponse({'result':'fail', 'redirect':redirect})
    return JsonResponse({'result':'success', 'redirect':redirect})


def get_order_items(request):
    items = Order.objects.get(**{Order._pk_:request.POST['pk']})
    return JsonResponse({'items':items})

def get_store_input(request):
    _store_input = store_input()
    return JsonResponse({'store_input':_store_input})