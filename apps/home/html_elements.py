from .forms import *

##################################################################################################################
# Html element functions
##################################################################################################################

def store_input(id=None, name=None, required=None):
    html = f'<select id="{id or "store_id"}" {f"name={name}" if name else "" }class="form-control"{" required" if required else ""}>/n'
    for v, s in enumerate(Store.objects.all()):
            html += f'    <option value="{v}">{s}</option>/n'
    html += f'</select>'
    return html
