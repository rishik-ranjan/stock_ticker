from flask import Flask, render_template, request, redirect

from bokeh.plotting import figure
from bokeh.embed import components 
from bokeh.resources import INLINE

import numpy as np
import requests
import pandas as pd

from datetime import datetime

app = Flask(__name__)

def convert_date(val):    # function to convert date to python's date object.
    y, m, d = val.split('-')
    return datetime(int (y), int(m), int(d))

col_keys = [u'Date', u'Open', u'High', u'Low',\
        u'Close', u'Volume', u'Ex-Dividend', u'Split Ratio',\
        u'Adj. Open', u'Adj. High', u'Adj. Low', u'Adj. Close',\
        u'Adj. Volume']
col_values = range(0,13)
col_dict = dict(zip(col_keys,col_values))

app.vars = {}
@app.route('/')
def blank():
    return redirect('/index')

@app.route('/index',methods=['GET','POST'])
def index():
	if request.method == 'GET':
		return render_template('index.html')
	else:
		app.vars['stock'] = request.form['stockticker']
		app.vars['features'] = request.form.getlist('features')

	        f = open('check.txt','w')
                f.write('%s\n'%(app.vars['stock']))
                f.write('%s\n'%(app.vars['features']))
                f.close()			
		return redirect('/main')
		
@app.route('/main',methods=['GET'])
def main():
    TOOLS = 'pan,box_zoom,wheel_zoom,reset,save'
    plot = figure(tools=TOOLS,
        title='Data from Quandle WIKI set',
        x_axis_label='date',
        x_axis_type='datetime')
    plot.title_text_color = "navy"
    api_url = {}
    stock_dict = {}
    i = 0
    colors = ['blue','green','beige','olive']
    if app.vars['features'] == []:
        return render_template('err.html')
        
    for feature in app.vars['features']:
        try:
            api_url[feature] = 'https://www.quandl.com/api/v3/datasets/WIKI/{}.json?'\
        'api_key=CzXv5hmRkss8g3Prakdw&'\
        'column_index={}&'\
        'collapse=daily'.format(app.vars['stock'],col_dict[feature])	    
            session = requests.Session()
            session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
            raw_data = session.get(api_url[feature])
            stock_dict = raw_data.json()
            if i==0:
                stock_df = pd.DataFrame(stock_dict['dataset']['data'],columns=['Date',feature])
                stock_df.Date = stock_df.Date.map(convert_date)
            else:
                stock_df[feature] = np.array(stock_dict['dataset']['data'])[:,1]
            i += 1
        except KeyError:
            return render_template('err.html')  
   
        plot.line(stock_df.Date,stock_df[feature],line_color=colors[i],legend=app.vars['stock']+":"+feature)
    jsresources = INLINE.js_raw
    cssresources = INLINE.css_raw
    script, div = components(plot,INLINE)        
    return render_template('graph.html', script=script, div=div,\
    jsresources = jsresources, cssresources = cssresources)


if __name__ == '__main__':
  app.run(port=33507)
