import requests
import json
import csv
from bs4 import BeautifulSoup
import pycountry
import os

# yapf: disable

BAROMETER_CATEGORIES = {
    "journalistsKilled": "https://rsf.org/en/barometer?year=2021&type_id=233#list-barometre",
    "citizensJournalistsKilled": "https://rsf.org/en/barometer?year=2021&type_id=240#list-barometre",
    "mediaAssistantsKilled": "https://rsf.org/en/barometer?year=2021&type_id=234#list-barometre",
    "journalistsImprisoned": "https://rsf.org/en/barometer?year=2021&type_id=235#list-barometre",
    "citizensJournalistsImprisoned": "https://rsf.org/en/barometer?year=2021&type_id=237#list-barometre",
    "mediaAssistantsImprisoned": "https://rsf.org/en/barometer?year=2021&type_id=236#list-barometre"
}

WPF_INDEX_URL = "https://rsf.org/sites/default/files/index_2021_pour_import_-_index_2020_-_pour_import_1_1_-_index_2020_-_pour_import_1_1.csv"

TABLE_SITES = {  # sites and more with tables of all countries
    "fragileStatesIndex": "https://en.wikipedia.org/wiki/List_of_countries_by_Fragile_States_Index",
    "globalPeaceIndex": "https://en.wikipedia.org/wiki/Global_Peace_Index",
    "population": "https://www.worldometers.info/world-population/population-by-country",
    "systemOfGovernment": "https://en.wikipedia.org/wiki/List_of_countries_by_system_of_government",
    "gdp": "https://www.worldometers.info/gdp/gdp-by-country/",
    "worldPopulation": "https://www.worldometers.info/world-population/"
}

# yapf: enable


def isoify_country_name(name):
    name_map = {
        "Congo-Brazzaville": "Congo",
        "North Korea": "Korea, Democratic People's Republic of",
        "Iran": "Iran, Islamic Republic of",
        "Laos": "Lao People's Democratic Republic",
        "Morocco / Western Sahara": "Morocco",
        "Russia": "Russian Federation",
        "Syria": "Syrian Arab Republic",
        "Venezuela": "Venezuela, Bolivarian Republic of",
        "Vietnam": "Viet Nam",
        "Palestine[a]": "Palestine, State of",
        "Palestine": "Palestine, State of",
        "Israel[a]": "Israel",
        "Tanzania": "Tanzania, United Republic of",
        "Bolivia": "Bolivia, Plurinational State of",
        "Bosnia-Herzegovina": "Bosnia and Herzegovina",
        "Micronesia": "Micronesia, Federated States of",
        "São Tomé and Príncipe": "Sao Tome and Principe",
        "Moldova": "Moldova, Republic of",
        "Cape Verde": "Cabo Verde",
        "Brunei": "Brunei Darussalam",
        "South Korea": "Korea, Republic of",
        "Czech Republic": "Czechia",
        "Taiwan": "Taiwan, Province of China",
        "The Gambia": "Gambia",
        "East Timor": "Timor-Leste",
        "Kyrgyz Republic": "Kyrgyzstan",
        "Cote d'Ivoire": "Côte d'Ivoire",
        "Republic of the Congo": "Congo",
        "Czech Republic (Czechia)": "Czechia",
        "State of Palestine": "Palestine, State of",
        "Sao Tome & Principe": "Sao Tome and Principe",
        "St. Vincent & Grenadines": "Saint Vincent and the Grenadines",
        "U.S. Virgin Islands": "Virgin Islands, U.S.",
        "Saint Kitts & Nevis": "Saint Kitts and Nevis",
        "Faeroe Islands": "Faroe Islands",
        "Sint Maarten": "Sint Maarten (Dutch part)",
        "Turks and Caicos": "Turks and Caicos Islands",
        "Saint Martin": "Saint Martin (French part)",
        "British Virgin Islands": "Virgin Islands, British",
        "Caribbean Netherlands": "Bonaire, Sint Eustatius and Saba",
        "Wallis & Futuna": "Wallis and Futuna",
        "Saint Barthelemy": "Saint Barthélemy",
        "Saint Helena": "Saint Helena, Ascension and Tristan da Cunha",
        "Saint Pierre & Miquelon": "Saint Pierre and Miquelon",
        "Falkland Islands": "Falkland Islands (Malvinas)",
        "Holy See": "Holy See (Vatican City State)",
        "Bahamas, The": "Bahamas",
        "China, People's Republic of": "China",
        "Congo, Republic of the": "Congo",
        "Federated States of Micronesia": "Micronesia, Federated States of",
        "Gambia, The": "Gambia",
        "Korea, North": "Korea, Democratic People's Republic of",
        "Korea, South": "Korea, Republic of",
        "Vatican City": "Holy See (Vatican City State)",
        "Côte d’Ivoire": "Côte d'Ivoire",
        "Haïti": "Haiti",
        "Guinea Bissau": "Guinea-Bissau",
        "Democratic Republic of the Congo": "Congo, The Democratic Republic of the",
        "DR Congo": "Congo, The Democratic Republic of the",
        "Democratic Republic of Congo": "Congo, The Democratic Republic of the",
        "Congo, Democratic Republic of the": "Congo, The Democratic Republic of the",
        "United States of America": "United States",
    }

    if name_map.get(name):
        return name_map[name]

    return name


def get_country(name):
    name = name.strip()
    name = isoify_country_name(name)
    return pycountry.countries.get(name=name)


def rsf_barometer(dataset):

    for category_name in BAROMETER_CATEGORIES:
        res = requests.get(BAROMETER_CATEGORIES[category_name])
        soup = BeautifulSoup(res.text, features="html.parser")

        country_els = soup.select(".barometre-accordion > li")

        for country_el in country_els:
            raw_country_name = country_el.select_one("button").text
            country_name = raw_country_name.split("(")[0].strip()

            iso_country = get_country(country_name)

            code = iso_country.alpha_2

            if not dataset.get(code):
                dataset[code] = {}

            person_els = country_el.select(".barometre-people-list > li")

            for person_el in person_els:
                person_data = {}
                datapoints = person_el.select("p")

                person_data["date"] = datapoints[0].text.strip()
                person_data["name"] = datapoints[1].text.strip()
                person_data["job"] = datapoints[2].text.strip()

                if not dataset[code].get("barometer"):
                    dataset[code]["barometer"] = {}

                if not dataset[code]["barometer"].get(category_name):
                    dataset[code]["barometer"][category_name] = []

                dataset[code]["barometer"][category_name].append(person_data)

        print(f"scraped {category_name}")

    return dataset


def wpf_index(dataset):
    with open(".temp_wpf_data.csv", "wb") as f:
        f.write(requests.get(WPF_INDEX_URL).content)

    index_csv = csv.DictReader(open(".temp_wpf_data.csv", "r",
                                    encoding="utf8"))

    for row in index_csv:
        # not official countries so skip them
        if row["ISO"] in ["CTU", "XCD", "XKO"]:
            continue

        iso_country = pycountry.countries.get(alpha_3=row["ISO"])

        code = iso_country.alpha_2

        data = {}

        data["rank2020"] = int(row["Rank 2020"])
        data["rank2021"] = int(row["Rank2021"])
        data["score2020"] = float(row["Score 2020"].replace(",", "."))

        # muss noch berechnen
        # dataset[code]["score2021"] = ""

        data["abuseScore"] = float(row["Sco Exa"].replace(",", "."))

        if not dataset.get(code):
            dataset[code] = {}

        if not dataset[code].get("pressFreedomIndex"):
            dataset[code]["pressFreedomIndex"] = {}

        dataset[code]["pressFreedomIndex"] = data

        # dataset[code]["underlyingSituationScore"] = float(row["Sco A"].replace(",", "."))

    print("scraped wpf index data from rsf")


def scrape():
    dataset = {}
    rsf_barometer(dataset)
    wpf_index(dataset)


    #Wikipedia tables

    # FRAGILE STATE INDEX - more points = more fragile - https://en.wikipedia.org/wiki/List_of_countries_by_Fragile_States_Index

    # scrapes the tables
    res = requests.get(TABLE_SITES["fragileStatesIndex"])
    soup = BeautifulSoup(res.text, features="html.parser")
    category = 'fragileStatesIndex'
    countries = soup.select("table.wikitable tbody tr")[1:]

    for country_el in countries:

        country_data = {}

        # scratches for the x columns in each line of the table
        rank = int(country_el.select('td')[0].text.strip())
        raw_country_name = country_el.select('td')[1].text.strip()
        score2021 = float(country_el.select('td')[2].text.strip())
        try:
            changeFrom2020 = float(country_el.select('td')[3].text.strip())
        except ValueError:
            changeFrom2020 = 0

        # israel und palästina haben [a] hinter, ich habe das einfach in die Liste geschrieben, wäre replace() schneller?
        country_name = raw_country_name


        # getting countries name and converting it to ISO code
        country_name = isoify_country_name(country_name)
        iso_country = pycountry.countries.get(name=country_name)

        # checks if country is in dataset yet and adds it if needed
        if not dataset.get(iso_country.alpha_2):
            dataset[iso_country.alpha_2] = {}

        # adds scratched data to temp dict
        country_data['rank'] = rank
        country_data['score2021'] = score2021
        country_data['changeFrom2020'] = changeFrom2020

        # adds information to the dataset
        dataset[iso_country.alpha_2][category] = country_data

    print('scraped fragileStatesIndex')

    # GLOBAL PEACE INDEX - more points = less peace - better rank = more peace - https://en.wikipedia.org/wiki/Global_Peace_Index

    # scrapes the tables
    res = requests.get(TABLE_SITES["globalPeaceIndex"])
    soup = BeautifulSoup(res.text, features="html.parser")
    category = 'globalPeaceIndex'
    countries = (soup.select("table.wikitable.sortable")[0]).select("tbody tr")[1:]

    for country_el in countries:

        country_data = {}

        # scratches for the x columns in each line of the table
        rank2021 = int(country_el.select('td')[1].text.replace("=", "").strip())
        raw_country_name = country_el.select('td')[0].text
        score2021 = float(
            country_el.select('td')[2].text.replace("=", "").strip())
        # rankChangeFrom2018 = country_el.select('td')[3].text.strip()
        # rankChangeFrom2018 = int(rankChangeFrom2018) - int(rank2019)

        country_name = raw_country_name.strip()
        # checks if country is in pycountry and skips it if not
        if country_name == "Kosovo":
            continue

        # getting countries name and converting it to ISO code
        country_name = isoify_country_name(country_name)
        iso_country = pycountry.countries.get(name=country_name)

        #checks if country is in dataset yet and adds it if needed
        if not dataset.get(iso_country.alpha_2):
            dataset[iso_country.alpha_2] = {}

        # adds scratched data to temp dict
        country_data['rank2021'] = rank2021
        country_data['score2021'] = score2021
        # country_data['rankChangeFrom2018'] = changeFrom2020

        # adds information to the dataset
        dataset[iso_country.alpha_2][category] = country_data

    print('scraped globalPeaceIndex')


    # systemOfGovernment - https://en.wikipedia.org/wiki/List_of_countries_by_system_of_government

    # scrapes the tables
    res = requests.get(TABLE_SITES["systemOfGovernment"])
    soup = BeautifulSoup(res.text, features="html.parser")
    category = 'systemOfGovernment'
    countries = (
        soup.select("table.wikitable.sortable")[0]).select("tbody tr")[1:]

    for country_el in countries:

        country_data = {}

        # scratches for the x columns in each line of the table
        raw_country_name = country_el.select('td')[0].text
        constitutionalForm = country_el.select('td')[1].text.strip()
        headOfState = country_el.select('td')[2].text.strip()
        basisOfExecutiveLegitimacy = country_el.select('td')[3].text.replace("[note 1]", "").strip()

        country_name = raw_country_name.strip()

        # checks if country is in pycountry and skips it if not
        if country_name == "Kosovo":
            continue

        # getting countries name and converting it to ISO code
        country_name = isoify_country_name(country_name)
        iso_country = pycountry.countries.get(name=country_name)

        # checks if country is in dataset yet and adds it if needed
        if not dataset.get(iso_country.alpha_2):
            dataset[iso_country.alpha_2] = {}

        # adds scratched data to temp dict
        country_data['constitutionalForm'] = constitutionalForm
        country_data['headOfState'] = headOfState
        country_data['basisOfExecutiveLegitimacy'] = basisOfExecutiveLegitimacy

        # adds information to the dataset
        dataset[iso_country.alpha_2][category] = country_data

    print('scraped systemOfGovernment')



    # RSF table

    #url - https://rsf.org/en/ranking_table

    res = requests.get('https://rsf.org/en/ranking_table')
    soup = BeautifulSoup(res.text, features="html.parser")
    category = 'url'
    countries = soup.select("td a")

    for country_el in countries:
        
        # scratches for the x columns in each line of the table
        raw_country_name = country_el.text
        url = country_el['href']

        country_name = raw_country_name.strip()

        #checks if country is officialy recognized and skips it if not
        if country_name == "Northern Cyprus" or country_name == "OECS" or country_name == "Kosovo":
            continue
        #getting countries name and converting it to ISO code
        country_name = isoify_country_name(country_name)
        iso_country = pycountry.countries.get(name=country_name)
        
        #checks if country is in dataset yet and adds it if needed
        if not dataset.get(iso_country.alpha_2):
            dataset[iso_country.alpha_2] = {}
        

        
        #adds information to the dataset
        dataset[iso_country.alpha_2][category] = "https://rsf.org"+url

    print('scraped URLs')



    # Worldometer tables
    
    # population - https://www.worldometers.info/world-population/population-by-country/

    # scrapes the tables
    res = requests.get(TABLE_SITES["population"])
    soup = BeautifulSoup(res.text, features="html.parser")
    category = 'population'
    countries = soup.select("table tbody tr")

    for country_el in countries:
        country_data = {}
        
        # scratches for the x columns in each line of the table
        raw_country_name = country_el.select('td')[1].text
        population = int(
            country_el.select('td')[2].text.replace(",", "").strip())
        yearlyPopulationChangePercent = float(country_el.select('td')[3].text.replace(",", "").replace("%", "").strip())
        worldShare = float(country_el.select('td')[11].text.replace("%", "").strip())

        country_name = raw_country_name.strip()

        # checks if country is officialy recognized and skips it if not
        if country_name == "Channel Islands":
            continue

        # getting countries name and converting it to ISO code
        country_name = isoify_country_name(country_name)
        iso_country = pycountry.countries.get(name=country_name)

        # checks if country is in dataset yet and adds it if needed
        if not dataset.get(iso_country.alpha_2):
            dataset[iso_country.alpha_2] = {}
        
        # adds scratched data to temp dict
        country_data['population'] = population
        country_data['yearlyPopulationChangePercent'] = yearlyPopulationChangePercent
        country_data['worldShare'] = worldShare

        
        # adds information to the dataset
        dataset[iso_country.alpha_2][category] = country_data

    print('scraped population')


    # GDP - https://www.worldometers.info/gdp/gdp-by-country/ - in US-dollar

    # scrapes the tables
    res = requests.get(TABLE_SITES["gdp"])
    soup = BeautifulSoup(res.text, features="html.parser")
    category = 'economy'
    countries = soup.select("table tbody tr")

    for country_el in countries:
        country_data = {}
        
        # scratches for the x columns in each line of the table
        raw_country_name = country_el.select('td')[1].text
        gdp = int(
            country_el.select('td')[2].text.replace(",", "").replace("$", "").strip())
        yearlyGdpGrowthPercent = float(country_el.select('td')[4].text.replace("%", "").strip())
        gdpPerCapita = int(country_el.select('td')[6].text.replace(",", "").replace("$", "").strip())
        worldShare = float(country_el.select('td')[7].text.replace("%", "").strip())


        country_name = raw_country_name.strip()

        # checks if country is officialy recognized and skips it if not
        if country_name == "Channel Islands":
            continue

        # getting countries name and converting it to ISO code
        country_name = isoify_country_name(country_name)
        iso_country = pycountry.countries.get(name=country_name)

        # checks if country is in dataset yet and adds it if needed
        if not dataset.get(iso_country.alpha_2):
            dataset[iso_country.alpha_2] = {}
        
        # adds scratched data to temp dict
        country_data['gdp'] = gdp
        country_data['yearlyGdpGrowthPercent'] = yearlyGdpGrowthPercent
        country_data['gdpPerCapita'] = gdpPerCapita
        country_data['worldShare'] = worldShare
        
        # adds information to the dataset
        dataset[iso_country.alpha_2][category] = country_data

    print('scraped GDP')






    for code in dataset:
        iso_country = pycountry.countries.get(alpha_2=code)
        dataset[code]["name"] = iso_country.name
        dataset[code]["officialName"] = iso_country.official_name if hasattr(
            iso_country, "official_name") else iso_country.name

    

    # WorldWide info - https://www.worldometers.info
    world_data = {}
    # scrapes the tables
    res = requests.get(TABLE_SITES["worldPopulation"])
    soup = BeautifulSoup(res.text, features="html.parser")
    category = 'worldwide'
    years = soup.select("table tbody tr")[0]
        
        
    # scratches for the x columns in each line of the table
    population = int(years.select('td')[1].text.replace(",", "").strip())
    yearlyChange = float(years.select('td')[2].text.replace("%", "").strip())
    
    # adds scratched data to temp dict
    world_data['population'] = population
    world_data['yearlyChangePercent'] = yearlyChange
    
    # adds information to the dataset
    dataset[category] = world_data

    print('scraped WorldWideInformation')



    return dataset

with open("static/dataset.js", "w") as f:
    f.write("var dataset = ")
    json.dump(scrape(), f)
    


os.remove(".temp_wpf_data.csv") 

print("scraping complete")