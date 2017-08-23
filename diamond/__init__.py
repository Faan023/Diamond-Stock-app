from flask import Flask


app = Flask(__name__)
app.secret_key = 'no chance of me telling you!'

import diamond.views
