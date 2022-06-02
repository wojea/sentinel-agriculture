# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
from zipfile import  ZipFile

from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
from dotenv import load_dotenv
from PIL import Image
import numpy
import pandas as pd
import matplotlib.pyplot as plt


def get_pixels_from_files(product_title):
    with ZipFile(f'{product_title}.zip', 'r') as satelite_zip:
        list_of_all_subfiles = ZipFile.infolist(satelite_zip)
        allowed_formats = ['B04_10m.jp2', 'B08_10m.jp2', 'B8A_20m.jp2', 'B11_20m.jp2', 'B02_20m.jp2']
        filtered_files = list()
        for allowed_format in allowed_formats:
            filtered_files_part = [k for k in list_of_all_subfiles if allowed_format in k.filename]
            filtered_files.extend(filtered_files_part)
        opened_files = [satelite_zip.open(filtered_file) for filtered_file in filtered_files]
        #print(opened_files)
        returned = {}
        for file in opened_files:
            name = file.name.split('/')[-1].split('_')[-2]
            image = Image.open(file)
            image = image.resize((5490,5490))
            image_pixels = numpy.array(image)
            returned[name]=image_pixels
        print(returned)
        return returned

def extract_tile_name_from_prod_title(title):
    return title.split("_")[-2:][0]


def unzip(product):
    with ZipFile(f'{product["title"]}.zip', 'r') as satelite_zip:
        list_of_all_subfiles = ZipFile.infolist(satelite_zip)
        allowed_formats = ['B04_10m.jp2', 'B08_10m.jp2', 'B8A_20m.jp2', 'B11_20m.jp2', 'B02_20m.jp2']
        filtered_files = list()
        for allowed_format in allowed_formats:
            filtered_files_part = [k for k in list_of_all_subfiles if allowed_format in k.filename]
            filtered_files.extend(filtered_files_part)
        opened_files = [satelite_zip.open(filtered_file) for filtered_file in filtered_files]

def vegetation(pixels_dict):
    agri = numpy.nan_to_num(((pixels_dict['B08']-pixels_dict['B04'])/(pixels_dict['B08']+pixels_dict['B04'])))
    return agri

def moisture(pixels_dict):
    moist = numpy.nan_to_num((pixels_dict['B8A']-pixels_dict['B11'])/(pixels_dict['B8A']+pixels_dict['B11']))
    return moist

def plot_vege_moist(file):
        pixs = get_pixels_from_files(file)
        moistIndex = moisture(pixs)
        vegeIndex= vegetation(pixs)
        frame = pd.concat([pd.Series(moistIndex.flatten()),pd.Series(vegeIndex.flatten())],axis=1).groupby(0).mean()
        print(frame)
        frame.plot(legend=False)
        plt.xlabel('Indeks wilgotności')
        plt.ylabel('Indeks wegetacji')
        plt.show()
        #Image.fromarray(vegeIndex,'L').show()
        #Image.frombytes('L',(5490,5490),vegeIndex).show()


def find_products(api,geojson_path,date1,date2):
     # download single scene by known product id
    # api.download('21d68494-012e-4416-b5a4-810959b00d4e')

    # search by polygon, time, and Hub query keywords
    footprint = geojson_to_wkt(read_geojson(geojson_path)) #'geojson/river_deltas.geojson'
    products = api.query(footprint, date=(date1,date2 ),     #'20211219', date(2021, 12, 29)   
                         platformname='Sentinel-2',
                         cloudcoverpercentage=(0, 30),)
    # products = api.query(footprint, date=('20211219', date(2021, 12, 29)),
    #                      platformname='Sentinel-2',
    #                      cloudcoverpercentage=(0, 30),
    #                      limit=1)
    # print(len(products))
    # print(products)
    return products

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    load_dotenv()
    # connect to the API
    api = SentinelAPI(os.environ.get("USER"), os.environ.get("PASSWORD"), 'https://apihub.copernicus.eu/apihub')

    products = find_products(api,'geojson/river_deltas.geojson','20211219',date(2022, 4, 29))
    #products2 = find_products(api,'geojson/river_deltas.geojson','20220119',date(2022, 3, 29))
    #products.update(products2)
    #print(products)
    #this downloads 1 product
    productDWN = next(iter(products))
    productFileName = products[productDWN]['identifier']
    productPrint = products[productDWN]['footprint']
    for item in products:
        #print(item)
        if(products[item]['footprint'] == productPrint):
            print(products[item]['generationdate'])
    #print(productFileName)
    exit(0)
    #api.download(productDWN) #ogarniete title juz
    # print(productDWN)

    #plot_vege_moist("S2A_MSIL2A_20211228T230821_N0301_R015_T49CEN_20211229T021039") #tu tymczasowo na sztywno, ogarniemy dalej automatyzacje
    

    



