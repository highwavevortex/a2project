from flask import Flask, render_template, redirect, url_for, request
import mongoengine
import models

mongoengine.connect()

if __name__ == "__main__":
    app.run(debug = True)