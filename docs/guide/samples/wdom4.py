from wdom.tag import Input

input = Input(type='checkbox')
print(input.html_noid)  # <input type="checkbox">

# this is equivalent to:
input = Input()
input.setAttribute('type', 'checkbox')
# also same as:
input.type = 'checkbox'
