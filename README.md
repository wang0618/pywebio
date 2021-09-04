<h1 align="center" name="pywebio-en">PyWebIO</h1>
<p align="center">
    <em>Write interactive web app in script way.</em>
</p>
<p align="center">
    <a href="https://percy.io/pywebio/pywebio">
        <img src="https://percy.io/static/images/percy-badge.svg" alt="Percy visual test">
    </a>
    <a href="https://codecov.io/gh/wang0618/PyWebIO">
        <img src="https://codecov.io/gh/wang0618/PyWebIO/branch/dev/graph/badge.svg" alt="Code coverage"/>
    </a>
    <a href="https://www.jsdelivr.com/package/gh/wang0618/PyWebIO-assets">
        <img src="https://data.jsdelivr.com/v1/package/gh/wang0618/PyWebIO-assets/badge?style=rounded" alt="Jsdelivr hit count"/>
    </a>
    <a href="https://pywebio.readthedocs.io/zh_CN/latest/?badge=latest">
        <img src="https://readthedocs.org/projects/pywebio/badge/?version=latest" alt="Documentation Status">
    </a>
    <a href="https://pypi.org/project/PyWebIO/">
        <img src="https://img.shields.io/pypi/v/pywebio?colorB=brightgreen" alt="Package version">
    </a>
    <a href="https://pypi.org/project/PyWebIO/">
        <img src="https://img.shields.io/badge/python->%3D%203.5.2-brightgreen" alt="Python Version">
    </a>
    <br/>
    <a href="https://lgtm.com/projects/g/wang0618/PyWebIO/context:python">
        <img src="https://img.shields.io/lgtm/grade/python/github/wang0618/PyWebIO.svg?colorB=brightgreen" alt="Python code quality">
    </a>
    <a href="https://lgtm.com/projects/g/wang0618/PyWebIO/context:javascript">
        <img src="https://img.shields.io/lgtm/grade/javascript/github/wang0618/PyWebIO.svg?colorB=brightgreen" alt="Javascript code quality">
    </a>
    <a href="https://github.com/wang0618/PyWebIO/blob/master/LICENSE">
        <img src="https://img.shields.io/github/license/wang0618/PyWebIO.svg" alt="License">
    </a>
    <br/>
    <a href="https://pywebio.readthedocs.io">[Document]</a> | <a href="http://pywebio-demos.pywebio.online/">[Demos]</a> | <a href="https://github.com/wang0618/PyWebIO/wiki/Why-PyWebIO%3F">[Why PyWebIO?]</a>
</p>

[English](README.md) | [中文](README-zh.md)

PyWebIO provides a series of imperative functions to obtain user input and output on the browser, turning the browser into a "rich text terminal", and can be used to build simple web applications or browser-based GUI applications without the need to have knowledge of HTML and JS. PyWebIO can also be easily integrated into existing Web services. PyWebIO is very suitable for quickly building applications that do not require complex UI.

<p align="center">
    <img src="https://raw.githubusercontent.com/wang0618/PyWebIO/dev/docs/assets/output_demo.gif" alt="PyWebIO output demo" width='609px'/>
    <img src="https://raw.githubusercontent.com/wang0618/PyWebIO/dev/docs/assets/input_demo.gif" alt="PyWebIO input demo" width='609px'/>
</p>


Features：

- Use synchronization instead of a callback-based method to get input
- Non-declarative layout, simple and efficient
- Less intrusive: old script code can be transformed into a Web application only by modifying the input and output operation
- Support integration into existing web services, currently supports Flask, Django, Tornado, aiohttp, FastAPI framework
- Support for ``asyncio`` and coroutine
- Support data visualization with third-party libraries, e.g., `plotly`, `bokeh`, `pyecharts`.

## Installation

Stable version:

```bash
pip3 install -U pywebio
```

Development version:
```bash
pip3 install -U https://code.aliyun.com/wang0618/pywebio/repository/archive.zip
```

**Prerequisites**: PyWebIO requires Python 3.5.2 or newer

## Quickstart

**Hello, world**

Here is a simple PyWebIO script to calculate the [BMI](https://en.wikipedia.org/wiki/Body_mass_index):

```python
from pywebio.input import input, FLOAT
from pywebio.output import put_text

def bmi():
    height = input("Your Height(cm)：", type=FLOAT)
    weight = input("Your Weight(kg)：", type=FLOAT)

    BMI = weight / (height / 100) ** 2

    top_status = [(14.9, 'Severely underweight'), (18.4, 'Underweight'),
                  (22.9, 'Normal'), (27.5, 'Overweight'),
                  (40.0, 'Moderately obese'), (float('inf'), 'Severely obese')]

    for top, status in top_status:
        if BMI <= top:
            put_text('Your BMI: %.1f, category: %s' % (BMI, status))
            break

if __name__ == '__main__':
    bmi()
```

This is just a very simple script if you ignore PyWebIO, but using the input and output functions provided by PyWebIO, you can interact with the code in the browser [[demo]](http://pywebio-demos.pywebio.online/bmi):

<p align="center">
    <a href="http://pywebio-demos.pywebio.online/?pywebio_api=bmi">
        <img src="https://raw.githubusercontent.com/wang0618/PyWebIO/dev/docs/assets/demo.gif" alt="PyWebIO demo" width="400px"/>
    </a>
</p>

**Serve as web service**

The above BMI program will exit immediately after the calculation, you can use [`pywebio.start_server()`](https://pywebio.readthedocs.io/en/latest/platform.html#pywebio.platform.tornado.start_server) to publish the `bmi()` function as a web application:

```python
from pywebio import start_server
from pywebio.input import input, FLOAT
from pywebio.output import put_text

def bmi(): # bmi() keep the same
    ...  

if __name__ == '__main__':
    start_server(bmi, port=80)
```

**Integration with web framework**

To integrate a PyWebIO application into Tornado, all you need is to add a `RequestHandler` to the existing Tornado application:

```python
import tornado.ioloop
import tornado.web
from pywebio.platform.tornado import webio_handler

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/bmi", webio_handler(bmi)),  # bmi is the same function as above
    ])
    application.listen(port=80, address='localhost')
    tornado.ioloop.IOLoop.current().start()
```

Now, you can open `http://localhost/bmi` for BMI calculation.

For integration with other web frameworks, please refer to [document](https://pywebio.readthedocs.io/en/latest/guide.html#integration-with-web-framework).

## Demos

 - [Basic demo](http://pywebio-demos.pywebio.online/) : PyWebIO basic input and output demos and some small applications written using PyWebIO.
 - [Data visualization demo](http://pywebio-charts.pywebio.online/) : Data visualization with the third-party libraries, e.g., `plotly`, `bokeh`, `pyecharts`.

## Document

Document is on [https://pywebio.readthedocs.io](https://pywebio.readthedocs.io)
