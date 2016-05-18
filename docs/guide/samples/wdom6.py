from wdom.tag import Button

class MyButton(Button):
    class_ = 'btn'

print(MyButton().html_noid)
# <button class="btn"></button>

# This is almost same as:
class MyButton2(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute('class', 'btn')
        ...

# class-level classes are not able to remove from instance
btn = MyButton()
btn.classList.remove('btn')
print(btn.html_noid)  # <button class="btn"></button>

btn2 = MyButton2()
btn2.classList.remove('btn')
print(btn2.html_noid)  # <button></button>

# Inherited class_ not overrides super-classes class_
class DefaultButton(MyButton):
    class_ = 'btn-default'

db = DefaultButton()
print(db.html_noid)  # <button class="btn btn-default"></button>
