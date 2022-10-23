#############################################################
# Since I'm not importing variables.py I need some duplicate
# imports and functions here
#############################################################	

import numpy as np

def DICTS_FORMAT(str, dicts, cycles=3):
    for z in range(cycles):
        for dict_name, dict_kvs in dicts.items():        
            for k,v in dict_kvs.items(): 
                str = str.replace(f'{dict_name}[{k}]', f'{v}')
    return str

#############################################################
# Custom Form Class
#############################################################

class EcoForm():
    name = None
    fields = None
    status = None
    errors = None
    cleaned_values = None
    field_dict = None
    form_dict = None
    format_dicts = None
    _header = None
    _footer = None

    def __init__(self, name, fields, elements):
        self.name = name
        self.fields = fields
        self.field_dict = {f.name : f for f in self.fields}
        for f in self.fields: f.set_form(self)        
        self.status = 'Initialized'
        self.update()
        self._header, self._footer = EcoForm.ElementBuilder(elements)
        return
    
    #######################################
    # Static Functions
    #######################################
    
    def B_(label, onclick=None, icon=None):
        icon = f'<span class="btn-inner--icon"><i class = "fa {icon}" ></i></span>' if icon else ''
        onclick = f'onclick="{onclick}"' if onclick else ''
        button_html = f'<button class="btn px-2 mx-2" type="button" {onclick}>{icon}<span class="btn-inner--text mx-1">{label}</span></button>'
        return button_html

    def H_(heading, size=5, _class="m-2"):
        heading_html = f'<h{size} class="{_class}">{heading}</h{size}>'
        return heading_html

    def P_(heading, size=5, _class="m-2"):
        paragraph_html = f'<p class="{_class}">{heading}</p>'
        return paragraph_html
    
    def ElementRow(elmts):
        col_ind = np.array([len(e) > 0 for e in elmts])   
        _len = col_ind.sum() 
        if _len == 0: return ''
        _align = np.array(['start','center','end'])
        col_sizes = np.array([4,4,4])    
        if not(_len == 2 and col_ind[1]):
            col_sizes = (col_ind * 12. / _len).astype(int)
        elmts = ['\n'.join(e) for e in elmts]
        elmts = [
            f'<div class="col-{s} text-{a}">\n{e}\n</div>'
            for e, a, s, i in zip(elmts, _align, col_sizes, col_ind)
            if i == 1
        ]
        elmts = "\n".join(elmts)
        html = f'<div class="row">\n{elmts}\n</div>'
        return html

    def ElementBuilder(elements):
        elmts = [[[],[],[]],[[],[],[]]]
        for e, i, j in elements: elmts[i][j] += [e]
        _header = EcoForm.ElementRow(elmts[0])
        _header = f'<div class="card-header">{_header}</div>' if _header else ''
        _footer = EcoForm.ElementRow(elmts[1])
        _footer = f'<div class="card-footer">{_footer}</div>' if _footer else ''
        return _header, _footer

    #######################################
    # Html Functions
    #######################################

    def get_html(self, csrf_token):
        _html= f'''
        <form action="" method="POST" enctype="multipart/form-data" name="{self.name}" id="{self.name}">
            {self.header_html()}            
            <div class="row card-body"><div class="col-12">                
                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">            
                {self.field_html()}                    
            </div></div>
            {self.footer_html()}
        </form>
        '''
        return _html

    def header_html(self):
        _header_html = DICTS_FORMAT(self._header, self.format_dicts)
        return _header_html

    def footer_html(self):
        _footer_html = DICTS_FORMAT(self._footer, self.format_dicts)
        return _footer_html

    def field_html(self):
        field_html = ''
        _rowhtml, _colidx = '', 0
        for _fld in self.fields:
            _rowhtml += _fld.get_html()
            _colidx += _fld.col_size
            if _colidx >= 12:
                field_html += f'<div class="row mt-4">{_rowhtml}</div>'
                _rowhtml, _colidx = '', 0
        if _rowhtml:
            field_html += f'<div class="row mt-4">{_rowhtml}</div>'
        return field_html    

    #######################################
    # Misc Functions
    #######################################

    def update(self):        
        self.form_dict = {
            'name':self.name,
            'status':self.status
        }
        self.format_dicts = {
            'form_dict': self.form_dict,
            'field_dict': self.field_dict
        }
        return

    def is_valid(self, val_dict):
        _valid = True
        _errors, _cleaned_values = {}, {}
        for _fld in self.fields:
            print(_fld.name)
            res = _fld.is_valid(val_dict[_fld.name])
            _errors[_fld.name] = res[0]
            _cleaned_values[_fld.name] = res[1]
            if _errors[_fld.name]:
                _valid = False
        self.errors = _errors
        self.cleaned_values = _cleaned_values
        return _valid
    
    def clear(self):
        self.clean_values = None
        self.errors = None
        for _fld in self.fields:
            _fld.clear()
        return


#############################################################
# Custom Form Input Fields
#############################################################


class EcoFormField():
    label = None
    name = None
    attrs = None
    state = None
    visible = None
    required = None
    col_size = None
    cleaned_value = None
    error = None
    type = 'text'
    form = None
    form_fields = None

    def __init__(self, name, label=None, attrs = {}, state = 0,
     visible = True, required = False, col_size = 12):
        self.name = name
        self.label = label        
        self.attrs = self._add_or_create_attr('class', 'form-control', attrs=attrs)
        self.state = state
        self.visible = visible
        self.required = required
        self.col_size = col_size
        return

    def set_form(self, form):
        self.form = form
        self.field_dict = self.form.field_dict
        return

    def _clean(self, value):
        _clean_value = value    
        return _clean_value

    def _add_or_create_attr(self, key, value, attrs=None):
        attrs = (self.attrs if attrs is None else attrs).copy()
        if key in attrs:
            attrs[key] += f' {value}'
        else:
            attrs[key] = value
        return attrs

    def get_html(self):
        _label = f'<label>{self.label}</label>' if self.label else ''
        _attrs = self.attrs
        _value = f'value="{self.cleaned_value}"' if self.cleaned_value else ''
        if self.error:
            _attrs = self._add_or_create_attr('class', 'is-invalid', _attrs)
            _error = f'title="{self.error}"'
        else:
            _error = ''
        _attrs = " ".join([f'{k}="{v}"' for k,v in _attrs.items()])
        _html = f'''
            <div class="col-{self.col_size}">{_label}                
                <input {_error} type="{self.type}" name="{self.name}" id="{self.name}" {_value} {_attrs}>
            </div>
        '''
        return _html

    def is_valid(self, value):
        self.error = None
        self.cleaned_value = self._clean(value)
        if self.cleaned_value == "":
            if self.required:
                self.error = f"{self.name} field is required"
        return self.error, self.cleaned_value
    
    def clear(self):
        self.cleaned_value = None
        self.error = None
        return

class EcoNumberField(EcoFormField):
    type = 'number'

class EcoEmailField(EcoFormField):
    type = 'email'

class EcoPasswordField(EcoFormField):
    type = 'password'

class EcoDateField(EcoFormField):
    type = 'date'

class EcoTimeField(EcoFormField):
    type = 'time'

class EcoTextChoiceField(EcoFormField):
    type = 'text'    
    def __init__(
        self, name, choices, label=None, attrs = {}, state = 0, visible = True,
        required = False, col_size = 12):
        super(EcoTextChoiceField, self).__init__(name, label=None, attrs = {}, state = 0, visible = True, required = False, col_size = 12)
        self.choices = choices
        return

    def get_html(self):
        _label = f'<label>{self.label}</label>' if self.label else ''
        _attrs = self.attrs
        _attrs = " ".join([f'{k}="{v}"' for k,v in _attrs.items()])
        _options = "\n".join([f'<option value="{_val}">{_lbl}</option>"' for _val, _lbl in self.choices])
        _html = f'''
            <div class="col-{self.col_size}">{_label}
                <select name="{self.name}" class="form-control" id="{self.name}" {_attrs}>
                    <option value="" selected="">---------</option>
                    {_options}
                </select>
            </div>
        '''
        return _html

class EcoIntChoiceField(EcoFormField):
    type = 'int'

class EcoDecimalChoiceField(EcoFormField):
    type = 'int'