from wdom.document import set_app
from wdom.server import start
from wdom.tag import Div, H1, Input

class MyElement(Div):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.h1 = H1('Hello, WDOM', parent=self)  
        self.input = Input(parent=self)
        self.input.addEventListener('input', self.update)

    def update(self, event):
        self.h1.textContent = event.target.value

if __name__ == '__main__':
    set_app(MyElement())
    start()
