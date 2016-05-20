from wdom.tag import Ul, Li

ul = Ul()
li1 = Li('item1')
li2 = Li('item2')
...

ul.appendChild(li1)
ul.appendChild(li2)
...
print(ul.html_noid)

# by append
ul2 = Ul()
ul2.append(Li('item1'), Li('item2'))
print(ul2.html_noid)
