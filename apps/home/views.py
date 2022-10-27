from traitlets import Instance
from .html_elements import *

##################################################################################################################
# General Pages, Processing
##################################################################################################################

def index(request):
    template = loader.get_template('home/index.html')
    return HttpResponse(template.render({}, request))

def get_context(request):
    _context = {
        'request':          request,
        'csrftoken':        request.COOKIES['csrftoken'],
        'user':             request.user,
        'Sidebar':          SIDEBAR,
        'Today':            STR_TODAY(),        
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

def Dashboard(context):
    _csrf_token = context['request'].COOKIES['csrftoken']
    context['form_html'] = GetFormHTML(_csrf_token, 'DashForm')
    template = loader.get_template('home/dashboard.html')
    return HttpResponse(template.render(context, context['request']))

def basic_page(context):
    if context['request'].method == 'POST': 
        return form_post(context, context['request'])
    template = loader.get_template(context['PageDesign']['Template'])
    return HttpResponse(template.render(context, context['request']))

def advanced_page(context):
    if context['PageName'] == 'ProcessOrder':
        context['pk'] = context['request'].GET['pk']
        context['Order'] = Order.objects.get(pk=context['pk'])
        context['OrderStr'] = str(context['Order'])
        context['form_html'] = GetFormHTML(context['csrftoken'], 'ProcessOrderForm', clear=True)
        
    elif context['PageName'] == 'CheckInOrder':
        context['pk'] = context['request'].GET['pk']
        context['Order'] = Order.objects.get(pk=context['pk'])
        context['OrderStr'] = str(context['Order'])
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
        try:
            heading=f"{request.POST['FormName']}",
            body=f"{m} - {'Saved' if _inst else f'Created'}"
        except:
            heading=f"Saved Model: Error on Model Str",
            body=""
        add_notification(icon='save',heading=heading,body=body)        
        return redirect(valid_redirect)    
    msg_head = f"{_inst} - Failed to Save" if _inst else f"Could not create {model_name}",
    msg_body = "Form Errors:/n"
    msg_body = '/n -'.join([f'{k}:  {v}'for k,v in form.errors.items()])
    add_notification(icon='warn', heading=msg_head, body=msg_body)
    return redirect(invalid_redirect)

##################################################################################################################
# Custom Form Functions
##################################################################################################################

def GetFormHTML(csrf_token, form_name, clear=False):
    _form = GET_NEW_FORM(form_name)
    if clear: _form.clear()
    _form_html = mark_safe(_form.get_html(csrf_token))
    return _form_html

def SaveForm(csrf_token, form_name, val_dict, pk_dict={}):
    _form = GET_NEW_FORM(form_name)
    vals = _form.update_pks(pk_dict)
    vals.update(val_dict)
    if _form.is_valid(vals):
        result = 'success'
        _form.save()
        _form.clear()
    else:
        result = 'fail'
    _form_html = mark_safe(_form.get_html(csrf_token))
    return result, _form_html

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

def AjxProcManifest(request):
    myOrder = Order.objects.get(pk=request.POST['order_id'])
    df = pd.read_csv(myOrder.manifest_file)
    df.columns = df.columns.str.lower()
    heading_template, heading_fields = GET_MANIFEST_FIELDS(df.columns)
    df = df[list(heading_fields)].rename(columns=heading_fields)
    success_cnt, fail_cnt = 0, 0
    for _, line_item in df.iterrows():
        kwargs = DICT_REMOVE_EMPTY(dict(line_item))
        new_item = Item(**kwargs)
        new_item.employee_id = request.POST['employee_id']
        new_item.order_id = request.POST['order_id']
        new_item.status_date = request.POST['status_date']
        try:
            new_item.save()
            success_cnt += 1
        except:
            fail_cnt += 1

    add_str = f'Added {success_cnt} rows to Order'
    add_notification(icon='add', heading=add_str)

    fail_str = f'Could not add {fail_cnt} rows to Order'
    add_notification(icon='warn', heading=fail_str)

    return JsonResponse({'response':add_str})

def AjxDeleteItem(request):
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

def AjxGetFormHTML(request):
    _form_html = GetFormHTML(request.POST['csrfmiddlewaretoken'], request.POST['form_name'])
    return JsonResponse({'form_data':_form_html})

def AjxSaveForm(request):
    result, _form_html = SaveForm(request.POST['csrfmiddlewaretoken'], request.POST['form_name'], request.POST.dict())
    return JsonResponse({'result':result, 'form_data':_form_html})

def AjxFormData(request):
    form_name = request.POST['FormName']
    form = FORMS(request, form_name, instance=request.POST.get('pk'), get_cur_data=True)
    design = FORM_DESIGN[form_name]
    fields = [(fd['Size'], fd['Label'], form[fd['Field']]) for fd in design['Fields']]
    _form_data = form_content_html(fields)
    return JsonResponse({'form_data':_form_data})

def AjxProcOrderAgg(request):
    result = 'Fail'
    cmd = request.POST['Command']
    order_id = request.POST['order_id']

    if cmd =='DELETE_ALL':
        exclude = ['CheckedIn']
        items = Item.objects.filter(
                order_id = order_id
            ).exclude(
                status__in=exclude
            )
        del_cnt = items.count()
        items.delete()
        add_notification(icon='delete', heading=f'Deleted {del_cnt} Items!')
        result = 'Success'
    elif cmd == 'FILL_DELIVERED':
        filter = ['']
        items = Item.objects.filter(
                order_id = order_id
            ).filter(
                status__in=filter
            )
        for i in items:
            i.status = 'Delivered'
        Item.objects.bulk_update(items, ['status'])
        result = 'Success'        
        add_notification(icon='save', heading=f'Updated {items.count()} Items!')

    return JsonResponse({'result':result})

def AjxTableData(request):
    # Get fields
    table_name = request.POST['TableName']

    design = TABLE_DESIGN[table_name]
    fields = [fd['FieldValue'] for fd in design['Fields']]
    labels = [fd['Head'] for fd in design['Fields']]
    fieldclass = [fd['FieldClass'] for fd in design['Fields']]

    # Get Objects
    thisorder = Order.objects.get(pk=request.POST['pk'])
    _cols = "DESCRIPTION, CONDITION, RETAIL_AMOUNT, STATUS, CREATED_DATE, STATUS_DATE"
    data = Item.objects.raw(f"SELECT 1 AS ID, {_cols}, COUNT(*) AS QTY FROM HOME_ITEM WHERE ORDER_ID = {thisorder.pk} GROUP BY {_cols}")

    # Get table HTML
    _table_data = table_html(fields, labels, data, fieldclass=fieldclass, id='item_tbl', edit_btn=design['Edit'], del_btn=design['Delete'])
    
    return JsonResponse({'table_data':_table_data})

def AjxCheckIn(request):
    # Get fields
    item_pk = request.POST['item_pk']
    item = Item.objects.get(pk=item_pk)
    item.status = 'CheckedIn'
    item.status_date = STR_TODAY()
    item.save()
    add_notification(icon='save', heading="Checked In Item", body=item.__str__())
    return JsonResponse({})