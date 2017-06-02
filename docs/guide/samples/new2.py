import asyncio
from wdom.tag import Div, H1, Input
from wdom.document import get_document
from wdom.server import start_server, stop_server

class MyElement(Div):
    tag = 'my-element'  # custom tag name
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.h1 = H1('Hello, WDOM', parent=self)  
        self.input = Input(parent=self)
        self.input.addEventListener('input', self.update)

    def update(self, event):
        self.h1.textContent = event.target.value

if __name__ == '__main__':
    document = get_document()
    # Register MyElement
    document.defaultView.customElements.define('my-element', MyElement)
    # Make instance of MyElement from HTML
    document.body.insertAdjacentHTML('beforeend', '<my-element></my-element>')
    # Or, from createElement method
    my_element = document.createElement('my-element')
    document.body.appendChild(my_element)

    start_server()
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        stop_server()
