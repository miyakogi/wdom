from wdom.server import start
from wdom.document import get_document

if __name__ == '__main__':
    document = get_document()
    h1 = document.createElement('h1')
    h1.textContent = 'Hello, WDOM'
    def rev_text(event):
        h1.textContent = h1.textContent[::-1]
    h1.addEventListener('click', rev_text)
    document.body.appendChild(h1)
    start()
