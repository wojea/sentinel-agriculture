import os
from zipfile import  ZipFile

from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date, timedelta
from dotenv import load_dotenv
import numpy
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import rasterio
from rasterio.io import MemoryFile

numpy.seterr(divide='ignore')


def get_pixels_from_files2(product_title):
    with ZipFile(f'{product_title}.zip', 'r') as satelite_zip:
        list_of_all_subfiles = ZipFile.infolist(satelite_zip)
        allowed_formats = ['B04_10m.jp2', 'B08_10m.jp2', 'B8A_20m.jp2', 'B11_20m.jp2', 'B02_20m.jp2', 'B03_20m.jp2']
        filtered_files = list()
        for allowed_format in allowed_formats:
            filtered_files_part = [k for k in list_of_all_subfiles if allowed_format in k.filename]
            filtered_files.extend(filtered_files_part)
        opened_files = [satelite_zip.open(filtered_file) for filtered_file in filtered_files]
        returned = {}
        for file in opened_files:
            name = file.name.split('/')[-1].split('_')[-2]
            with MemoryFile(file) as f:
                with f.open() as op:
                    image = op.read(1)
                    if('B08' in name):
                        image= (image[::2,::2] + image[1::2,1::2]) //2  # zmniejszanie rozmiaru obrazu poprzez uśrednienie par pixeli
                    image_pixels = image
                    returned[name]=image_pixels 
            
          
        print(returned)
        return returned



def vegetation(pixels_dict):
    agri = numpy.nan_to_num(((pixels_dict['B08']-pixels_dict['B04'])/(pixels_dict['B08']+pixels_dict['B04'])))
    return agri


def moisture(pixels_dict):
    moist = numpy.nan_to_num((pixels_dict['B8A']-pixels_dict['B11'])/(pixels_dict['B8A']+pixels_dict['B11']))
    return moist


def find_products(api,geojson_path,date1,date2):
    footprint = geojson_to_wkt(read_geojson(geojson_path))
    products = api.query(footprint, date=(date1, date2),
                         platformname='Sentinel-2',
                         cloudcoverpercentage=(0, 30),
                         processinglevel = 'Level-2A')
    return products


def extract_bands(api, products, limit, directory):
    for item in products:
        print(products[item]['summary'])
    single_frame_product = next(iter(products)) #wymuszenie by pobrane produkty byly z jednej kratki
    productPrint = products[single_frame_product]['footprint']
    current_count = 0
    last_date = date.today()
    ignores=[] #nazwy pomijanych produktow
    for item in products:
        if current_count < limit:
            if 'generationdate' in products[item].keys():
                if products[item]['footprint'] == productPrint and products[item]['generationdate'].date() <= last_date - timedelta(days=7) and products[item]['identifier'] not in ignores:
                    last_date = products[item]['generationdate'].date()
                    if current_count>-1:
                        try:
                            api.download(item)
                        except Exception as e:
                            print(e)
                            print('error downloading')
                            continue
                        pixels_array = get_pixels_from_files2(products[item]['identifier'])
                        if len(pixels_array) != 0:
                            current_count += 1
                        os.remove(f'{products[item]["identifier"]}.zip')
                        pickle_file_path = f'{directory}/{products[item]["identifier"]}_{last_date}.pickle'
                        try:
                            pickle.dump(pixels_array, open(pickle_file_path, "wb"))
                        except (OSError, IOError) as e:
                            print(e)
                            print('Error pickle')
                    else:
                        current_count += 1



def plot_time_plot_outter(dates,maxes,averages):
    labels = dates
    zipped = zip(labels,maxes,averages)
    sortedZip = sorted(zipped)
    labels,maxes,averages = zip(*sortedZip) # sortowanie pod dacie
    x = numpy.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width / 2, maxes, width, label='Wegetacja')
    rects2 = ax.bar(x + width / 2, averages, width, label='Wilgotność')
    fig.set_figheight(6)
    fig.set_figwidth(15)
    ax.set_ylabel('Wartość indeksu')
    ax.set_xlabel('Data')
    ax.set_title('Wilgotność i wegetacja wg daty')
    ax.set_xticks(x, labels)
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    fig.tight_layout()
    
    plt.savefig('./Wilgotnosc_wegetacja_plot.png')
    #plt.show()

def plot_time_plot_inner(frame):
    frame.reset_index(inplace=True,drop=True)
    max = frame.groupby(by=0).mean()
    max = max[max[1]==max[1].max()]
    return max

def plot_results(directory):
    dates = list()
    maxes = []
    averages = []
    for filename in os.listdir(directory):
        date = filename.split("_")[-1].split(".")[0]
        dates.append(date)
        print(date)
        f = os.path.join(directory, filename)
        if os.path.isfile(f) and ('.pickle' in filename):
            with open(f, 'rb') as opened:
                pixels_dictionary = pickle.load(opened)
                moistIndex = moisture(pixels_dictionary)
                vegeIndex = vegetation(pixels_dictionary)
                frame = pd.concat([pd.Series(moistIndex.flatten()), pd.Series(vegeIndex.flatten())], axis=1)
                max = plot_time_plot_inner(frame)
                maxes.append(max[1].values[0])
                print('\n\n\nINDEX:\n')
                print(max.index) 
                print(max.index.values)
                print(max.index.values[0])      
                averages.append(max.index.values[0])
    plot_time_plot_outter(dates, maxes,averages)


if __name__ == '__main__':
    load_dotenv()
    # connect to the API
    print(os.environ.get("USER_sentinel"))
    print(os.environ.get("PASSWORD_sentinel"))
    api = SentinelAPI(os.environ.get("USER_sentinel"), os.environ.get("PASSWORD_sentinel"), 'https://apihub.copernicus.eu/apihub') 
    
    #pobieranie produktow
    dir = './folder'
    products = find_products(api, 'geojson/temperate_countryside.geojson', '20201219', date(2022, 4, 29))
    extract_bands(api, products, 100, dir)


    #utworzenie wykresow zaleznosci wegetacji od wilgotnosci
    plot_results(dir)

    exit(0)

    



