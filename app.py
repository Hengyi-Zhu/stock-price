from flask import Flask, render_template, request, redirect
import pandas as pd
import numpy as np
import requests
import datetime
from bokeh.plotting import figure
from bokeh.embed import components 

###

def prev_month(date):
    if date.month == 1:
        return date.replace(month=12,year=date.year-1)
    else:
        try:
            return date.replace(month=date.month-1)
        except ValueError:
            if date.month == 3 and 29 <= date.day <= 31:
                if date.year%4 == 0:
                    return prev_month(date=date.replace(day=29))
                else:
                    return prev_month(date=date.replace(day=28))
            else:
                return prev_month(date=date.replace(day=date.day-1))

def get_data_and_plot(Ticker):
    Ticker_url = 'https://www.quandl.com/api/v3/datasets/WIKI/%s.json?api_key=G72-GcKE_-wu3BJaS64B' % Ticker
    r = requests.get(Ticker_url)
    Ticker_json = r.json()

    Ticker_header = Ticker_json['dataset']['column_names']
    Ticker_data_lst = Ticker_json['dataset']['data']
    Ticker_data_pd = pd.DataFrame(Ticker_data_lst, columns=Ticker_header)
    prev_month_date = prev_month(datetime.date.today())
    Ticker_data_prev_month = Ticker_data_pd.ix[Ticker_data_pd['Date'] >= str(prev_month_date) ] 

    Ticker_close = np.array(Ticker_data_prev_month['Close'])
    Ticker_date = np.array(Ticker_data_prev_month['Date'], dtype=np.datetime64)

    plot = figure(width=600, height=400, x_axis_type="datetime")
    plot.line(Ticker_date, Ticker_close, legend = "%s: Close" % Ticker)
    plot.title = "last month's closing prices for %s" % Ticker.upper()
    plot.legend.location = "top_left"
    plot.xaxis.axis_label = 'Date'
    plot.yaxis.axis_label = 'Price'
    
    script, div = components(plot)
    return script, div

###

app = Flask(__name__)

@app.route('/')
def main():
    return redirect('/index')

@app.route('/index',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else: 
        global Ticker, script, div
        Ticker = request.form["ticker"]
        script, div = get_data_and_plot(Ticker)
        return redirect('/graph')
        
@app.route('/graph')
def bokeh_graph():
    return render_template('bokeh_graph.html', script=script, div=div, ticker=Ticker.upper())

if __name__ == '__main__':
    app.run(port=33507)
        
    