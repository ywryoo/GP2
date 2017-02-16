# -*- coding: utf-8 -*-
"""
app.py
flask application that serves webpages
---
Written by Yangwook Ryoo, 2017
MIT License: see LICENSE at root directory
"""
from flask import Flask
from gp2gatherplot.gatherplot import gatherplot

app = Flask(__name__)
app.register_blueprint(gatherplot, url_prefix='/gatherplot')


@app.route('/')
def route_root():
    return 'Modules are Here!<br><a href="./gatherplot">gatherplot</a>'
