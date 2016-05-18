from wdom.tag import Ul

ul = Ul()
ul.innerHTML = '''\
<li>item1</li>
<li>item2</li>
<li>item3</li>
<li>item4</li>
'''

print(ul.html_noid)  # <ul><li>...

# Accessing child nodes
# for child in ul.childNodes:
#     print(child.html)

# or, first/lastChild
print(ul.firstChild.html)
print(ul.lastChild.html)

# excluding Text nodes
for child in ul.children:
    print(child.html)

# first/lastElementChild
print(ul.firstElementChild.html)
print(ul.lastElementChild.html)
