from wdom.document import get_document
from wdom.server import start

if __name__ == '__main__':
    document = get_document()
    h1 = document.createElement('h1')
    h1.textContent = 'Hello, WDOM'
    document.body.appendChild(h1)
    start()
