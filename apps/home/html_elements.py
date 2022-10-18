from .forms import *

##################################################################################################################
# Html element functions
##################################################################################################################


##################################################################################################################
# Table elements
##################################################################################################################

def table_per_page_html(scale=1, selected=2):
    if scale == 0:
        return ''
    select_list = [i * scale for i in [2, 5, 10, 25, 100]]
    options = '/n'.join([f'<option value="{o}">{o}</option>' for o in select_list])
    html = f'''<div class="dataTable-dropdown">
        <label>
            <select class="dataTable-selector">
                {options}
            </select>
            entries per page
        </label>
    </div>'''
    return html

def table_search_html(search=True):
    if search:
        html = '''
            <div class="dataTable-search">
            <input class="dataTable-input" placeholder="Search..." type="text">
        </div>'''
        return html
    return ''

def table_dim_html(row_dict, field_list, fclass_list):
    html_list = [
        f'<td><p class="text-xs mb-0 {_fc}">{_f.format(**row_dict)}</p></td>'
        for _f, _fc in zip(field_list, fclass_list)
    ]
    return '\n'.join(html_list)

def table_html(fields, labels, data, fieldclass=None, id=None, edit_btn='', del_btn='', search=True, sortable='sortable', height='500px', per_page_scale=1):
    id = id or 'this_table'
    fieldclass = fieldclass or ['text-left' for _ in fields]
    h_fieldclass = [f + 'text-uppercase' for f in fieldclass]
    if edit_btn:
        edit_btn = f'<td class="text-center"><a id="{id}_edit_btn" href="#" onclick="{edit_btn}"><i class = "fa fa-pen text-info" ></i></a>'
        labels = ['Edit'] + labels
        h_fieldclass = ['text-uppercase text-center'] + h_fieldclass
    if del_btn:
        del_btn = f'<td class="text-center"><a id="{id}_del_btn" href="#" onclick="{del_btn}"><i class = "fa fa-trash text-danger" ></i></a>'
        labels += ['Delete']
        h_fieldclass = h_fieldclass + ['text-uppercase text-center']

    headings = '\n'.join([f'<th class="{_fldcls} text-secondary text-xxs font-weight-bolder opacity-7 nopad">{_lbl}</th>' for _lbl, _fldcls in zip(labels, h_fieldclass) ])

    table_data = [
        edit_btn.format(**_row.__dict__) +
        table_dim_html(_row.__dict__, fields, fieldclass) +
        del_btn.format(**_row.__dict__)
        for _row in data
        ]
    table_data = '</tr>\n<tr>'.join(table_data)
    html = f'''
<div class="table-responsive">
    <div class = "dataTable-wrapper">
        <table class="table table-flush" id="datatable-basic">            
                <thead class="thead-light"><tr>{headings}</tr></thead>
                <tbody><tr>{table_data}</tr></tbody>            
        </table>
    </div>
</div>'''
    return html

##################################################################################################################
# Form elements
##################################################################################################################

def form_content_html(fields):
    field_html, s = '', 0
    for _s, _l, _f in fields:
        s += _s
        if s > 12:
            field_html += '</div>\n<div class="row mt-3">'
            s -= 12
        field_html += f'<div class="col-{_s}"><label>{_l}</label>{_f}</div>'
    return f'<div class="row mt-3">{field_html}</div>'

def select_html(option_list, id='select-id', onchange=''):
    options = '/n'.join([f'<option value="{_val}">{_lbl}</option>'for _val, _lbl in option_list])
    if onchange: onchange = f' onchange="{onchange}" onfocus="this.selectedIndex = -1;"'
    html = f'<select class="form-select" id="{id}"{onchange}>{options}</select>'
    return mark_safe(html)