from flask import Flask, render_template, request, redirect, url_for, session, json, Blueprint
from flask_bootstrap import Bootstrap
from flask_analytics import Analytics
import os
import csv
import pandas as pd

def create_app(configfile=None):
    app = Flask(__name__)
    app.config.from_object(__name__)
    Bootstrap(app)
    Analytics(app)
    return app

app = create_app()

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
      try:
          year_selected = request.form['year']
      except:
          errors.append("Unable to get URL. Please make sure it's valid and try again.")
      return redirect(url_for('get_year', year=year_selected))

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "data", "velo.json")
    json_data = json.load(open(json_url))
    years_data = []
    for row in json_data:
      years_data.append(row['year'])

    csv_nation = os.path.join(SITE_ROOT, "data", "palmares_nation.csv")
    nation_df = pd.read_csv(csv_nation, sep=",")

    csv_equipe = os.path.join(SITE_ROOT, "data", "palmares_equipe.csv")
    equipe_df = pd.read_csv(csv_equipe, sep=",")
    
    return render_template('index.html', years=years_data, data=json_data, nation=nation_df,  equipe=equipe_df)


#@app.route("/<int(min=1903, max=2015):year>")
@app.route("/<int:year>")
def get_year(year):
    if year >= 1915 and year <= 1918 or year >= 1940 and year <= 1946:
        word = "==> triste année pour le velo..."
        return render_template('404.html', year=str(year), word=word), 404
    
    elif year < 1903:
        word = "Pas encore de tour de france à cette époque..."
        return render_template('404.html', year=str(year), word=word), 404
    
    elif year >= 2016:
        word = "pas encore arrivée !"
        return render_template('404.html', year=str(year), word=word), 404
    
    else:
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "data", "velo.json")
        json_data = json.load(open(json_url))
      
        #Get data by winners
        for row in json_data:
          if row['year'] == year:
            json_selected = row
            vainqueur = json_selected['Vainqueur']

        stats_selected = []
        stats_grimpeur = []
        stats_sprinter = []
        stats_jeune = []
        for row in json_data:
          if row['Vainqueur'] == vainqueur:
            stats_selected.append(row)
          if row['Grand Prix de la montagne'] == vainqueur:
            stats_grimpeur.append(row)
          if row['Par points'] == vainqueur:
            stats_sprinter.append(row)
          if row['Meilleur jeune'] == vainqueur:
            stats_jeune.append(row)

        #Get other win data
        csv_url = os.path.join(SITE_ROOT, "data", "palmares.csv")
        palma = pd.read_csv(csv_url, sep=",")
        palma_same_year = palma.loc[palma['Année'] == year]
        
        victoire_etendue = palma.loc[(palma['Vainqueur'] == vainqueur) | (palma['Deuxième'] == vainqueur) | (palma['Troisième'] == vainqueur)]
        victoire_etendue = victoire_etendue.drop(['Nationalité first', 'Nationalité second', 'Nationalité third'], 1)

        average_speed_by_step = []
        average_distance_by_step = []
        for year in stats_selected:
            average_speed_by_step.append(year['Vitesse moyenne'])
            average_distance_by_step.append(year['Distance (en km)'])

        #Coutning things
        count_grimpeur = 0
        for year in stats_grimpeur:
          count_grimpeur += 1

        count_sprinter = 0
        for year in stats_sprinter:
          count_sprinter += 1

        first_count = len(victoire_etendue.loc[victoire_etendue['Vainqueur'] == vainqueur])
        second_count = len(victoire_etendue.loc[victoire_etendue['Deuxième'] == vainqueur])
        third_count = len(victoire_etendue.loc[victoire_etendue['Troisième'] == vainqueur])
        total_count = len(victoire_etendue)
        victory_count = [total_count, first_count, second_count, third_count, count_grimpeur, count_sprinter, stats_jeune]
      
        return render_template('years.html', years=json_selected, palmares=victoire_etendue, stats=victory_count)

if __name__ == '__main__':    
    #app.jinja_env.cache = {}
    app.run(host='0.0.0.0', debug=True)
