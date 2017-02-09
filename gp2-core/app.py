# -*- coding: utf-8 -*-
"""
app.py
flask application that serves webpages
Written by Yangwook Ryoo, 2017
MIT License: see LICENSE at root directory
"""
from flask import Flask
app = Flask(__name__)


@app.route('/')
def route_root():
    return 'Hello, World!'
