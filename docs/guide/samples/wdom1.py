from wdom.document import set_app
from wdom.server import start
from wdom.tag import Div, H1, Input

class MyElement(Div):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.h1 = H1()
        self.h1.textContent = 'Hello, WDOM'
        self.input = Input()
        self.input.addEventListener('input', self.update)
        self.appendChild(self.input)
        self.appendChild(self.h1)

    def update(self, event):
        self.h1.textContent = event.target.value

if __name__ == '__main__':
    set_app(MyElement())
    server = start()
