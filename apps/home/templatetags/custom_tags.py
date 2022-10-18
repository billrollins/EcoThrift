from ..views import *

register = template.Library()

##################################################################################################################
# Basic Funtions
##################################################################################################################

@register.filter()
def _Get(dict, key):
    return mark_safe(dict[key])

@register.filter()
def _Del(obj):
    return f'{type(obj).__name__}:{obj.pk}'

@register.filter()
def _Format(str, dict):
    return mark_safe(FORMAT(str, dict))

@register.filter()
def _Format2(str, dict1, dict2):
    return mark_safe(DOUBLE_FORMAT(str, dict1, dict2))

##################################################################################################################
# Colors
##################################################################################################################

@register.filter()
def _BgColor(color_name):
    html = f'background-color: {ET_COLORS[color_name]};'
    return mark_safe(html)

##################################################################################################################
# Basic Renders
##################################################################################################################

@register.filter()
def _Icon(i, size='1.em'):
    html = f'<i class="{i}" style="font-size: {size}"></i>'
    return mark_safe(html)

##################################################################################################################
# Notifications
##################################################################################################################

@register.filter()
def _Notifications(n):
    html = ''
    if n:
        html = ['<div class="position-fixed bottom-1 end-1 z-index-2">']
        for notif_icon, notif_head, notif_body, notif_id in n:
            html += [
                f'<div class="toast fade hide p-2 bg-white my-4" role="alert" aria-live="assertive" id="{notif_id}" aria-atomic="true">',
                f'  <div class="toast-header border-0">',
                f'    <i class="ni {notif_icon} me-2"></i>',
                f'    <span class="me-auto font-weight-bold">{notif_head}</span>',
                f'    <i class="fas fa-times text-md ms-3 cursor-pointer" data-bs-dismiss="toast" aria-label="Close"></i>',
                '  </div>'
            ]
            if notif_body:
                html += [
                    '<hr class="horizontal dark m-0">',
                    f'<div class="toast-body">{notif_body}</div>'
                ]
            html += ['</div>']
        html += ['</div>']
        html = '\n'.join(html)
    return mark_safe(html)

@register.filter()
def _NotificationJS(n):
    html = ''
    if n:
        _code = '\n'.join([
            "var {0} = document.getElementById('{0}')",
            "var toast_{0} = new bootstrap.Toast({0})",
            "toast_{0}.show()"
        ])
        _code = '\n\n'.join([_code.format(v) for _, _, _, v in n])
        html = '\n'.join([
            "<script>",
            "window.onload = (event) => {",
            _code,
            "}",
            "</script>"
        ])
    return mark_safe(html)

##################################################################################################################
# Page Filters
##################################################################################################################

@register.filter()
def _Element(e, context):
    render_types = {'Form': render_form,'Table': render_table,'App': render_app}
    return render_types[e['Type']](e, context)

def render_app(e, context):
    if e['Element'] == 'AddItemApp':
        
        context['ItemForm'] = FORMS(context['request'], f['Form'], f['Instance'])
        
        template = loader.get_template('forms/add-item-form.html')
        return template.render(context, context['request'])
    return template.render(context, context['request'])

def render_form(e, context):
    context['MetaForms'] = META_FORMS(e['Element'], context['request'])
    template = loader.get_template(context['MetaForms'][0]['Template'])
    return template.render(context, context['request'])

def render_table(e, context):
    context['TableDesign'] = TABLE_DESIGN[e['Element']]
    context['TableData'] = MODELS(context['TableDesign']['Model']).objects.all()
    template = loader.get_template(context['TableDesign']['Template'])
    return template.render(context, context['request'])

##################################################################################################################
# Table Filters
##################################################################################################################

@register.filter()
def _TableField(f, object_row):
    data_dict = object_row.__dict__
    for attr in [d[:-3] for d in data_dict if d[-3:] == '_id']:
        data_dict[f'{attr}_str'] = str(object_row.__getattribute__(attr))
    data_dict.update({'object':str(object_row)})
    html = f'<p class="text-xs mb-0 {f["FieldClass"]}">{f["FieldValue"]}</p>'
    if f["FieldHREF"]:
        html = f'<a href="{f["FieldHREF"]}">{html}</a>'
    return mark_safe(html.format(**data_dict))