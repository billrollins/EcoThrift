from ..views import *

register = template.Library()

@register.filter()
def dict_get(d, k):
    return d[k]

@register.filter()
def delete_str(obj):
    return f'{obj.model_name}:{obj.__dict__[obj._pk_]}'

    

@register.filter()
def make_icon(i, size='1.em'):
    html = f'<i class="{i}" style="font-size: {size}"></i>'
    return mark_safe(html)

@register.filter()
def filter_format(str, dict1):
    if type(dict1) != dict:
        dict1 = dict1.__dict__
    return str.format(**dict1)

@register.filter()
def filter_format_2(str, dict1, dict2):
    return DOUBLE_FORMAT(str, dict1, dict2)

@register.filter()
def ntf_make(n):
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
def ntf_show(n):
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

def render_p(data, Value_Just, Value_Case, Value, HREF, **kwargs):
    html = f'<p class="text-xs mb-0 {Value_Just} {Value_Case}">{Value}</p>'
    if HREF:
        html = f'<a href="{HREF}">{html}</a>'    
    return html.format(**data)


@register.filter()
def view_fields(field, row_data):
    if field['Value_Type'] == 'p':
        html = render_p(row_data.__dict__, **field)
    elif field['Value_Type'] == 'custom':
        html = DOUBLE_FORMAT(field['Value'], field, row_data.__dict__)
    
    return mark_safe(html)

    
@register.filter()
def write_element(e, request):

    if e['Type'] == 'form':
        return render_form(request, e['Name'])
    elif e['Type'] == 'table':
        return render_table(request, e['Name'])

    return ''