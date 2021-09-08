Miscellaneous
===============

.. _codemirror_options:

Commonly used Codemirror options
------------------------------------

* ``mode`` (str): The language of code. For complete list, see https://codemirror.net/mode/index.html
* ``theme`` (str): The theme to style the editor with. For all available theme, see https://codemirror.net/demo/theme.html
* ``lineNumbers`` (bool): Whether to show line numbers to the left of the editor.
* ``indentUnit`` (int): How many spaces a block (whatever that means in the edited language) should be indented. The default is 2.
* ``tabSize`` (int): The width of a tab character. Defaults to 4.
* ``lineWrapping`` (bool): Whether CodeMirror should scroll or wrap for long lines. Defaults to false (scroll).

For complete Codemirror options, please visit: https://codemirror.net/doc/manual.html#config

.. _nginx_ws_config:

Nginx WebSocket Config Example
---------------------------------

Assuming that the PyWebIO application is running at the ``localhost:5000`` address, if you want to access your PyWebIO application via ``http://server_ip/some_path/tool``, a sample Nginx configuration is as follows::

    map $http_upgrade $connection_upgrade {
        default upgrade;
        '' close;
    }

    server {
        listen 80;

        location /some_path/ {
            alias /path/to/pywebio/static/dir/;
        }
        location /some_path/tool {
             proxy_read_timeout 300s;
             proxy_send_timeout 300s;
             proxy_http_version 1.1;
             proxy_set_header Host $http_host;
             proxy_set_header Upgrade $http_upgrade;
             proxy_set_header Connection $connection_upgrade;
             proxy_pass http://localhost:5000/;
        }
    }


The above configuration file hosts the static files of PyWebIO on the ``/some_path/`` path, and reverse proxy ``/some_path/tool`` to ``localhost:5000``.

The path of the static file of PyWebIO can be obtained with the command ``python3 -c "import pywebio; print(pywebio.STATIC_PATH)"``, you can also copy the static file to other directories::

    cp -r `python3 -c "import pywebio; print(pywebio.STATIC_PATH)"` ~/web
