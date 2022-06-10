# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
from zipfile import  ZipFile

from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date, timedelta
from dotenv import load_dotenv
from PIL import Image
import numpy
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import gzip
import shutil
import rasterio
from rasterio.io import MemoryFile

numpy.seterr(divide='ignore')

def get_pixels_from_files(product_title):
    with ZipFile(f'{product_title}.zip', 'r') as satelite_zip:
        list_of_all_subfiles = ZipFile.infolist(satelite_zip)
        allowed_formats = ['B04_10m.jp2', 'B08_10m.jp2', 'B8A_20m.jp2', 'B11_20m.jp2', 'B02_20m.jp2', 'B03_20m.jp2']
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


def get_pixels_from_files2(product_title):
    with ZipFile(f'{product_title}.zip', 'r') as satelite_zip:
        list_of_all_subfiles = ZipFile.infolist(satelite_zip)
        allowed_formats = ['B04_10m.jp2', 'B08_10m.jp2', 'B8A_20m.jp2', 'B11_20m.jp2', 'B02_20m.jp2', 'B03_20m.jp2']
        filtered_files = list()
        for allowed_format in allowed_formats:
            filtered_files_part = [k for k in list_of_all_subfiles if allowed_format in k.filename]
            filtered_files.extend(filtered_files_part)
        opened_files = [satelite_zip.open(filtered_file) for filtered_file in filtered_files]
        #print(opened_files)
        returned = {}
        for file in opened_files:
            name = file.name.split('/')[-1].split('_')[-2]
            with MemoryFile(file) as f:
                with f.open() as op:
                    image = op.read(1)
                    if('B08' in name):
                        image= (image[::2,::2] + image[1::2,1::2]) //2
                    image_pixels = image
                    returned[name]=image_pixels 
            #image = MemoryFile(file)#.open().read(1)
            #image=image.open()
            #image=image.read(1)
            #print(image)
            
          
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


def find_products(api,geojson_path,date1,date2):
     # download single scene by known product id
    # api.download('21d68494-012e-4416-b5a4-810959b00d4e')

    # search by polygon, time, and Hub query keywords
    footprint = geojson_to_wkt(read_geojson(geojson_path)) #'geojson/river_deltas.geojson'
    products = api.query(footprint, date=(date1, date2),     #'20211219', date(2021, 12, 29)
                         platformname='Sentinel-2',
                         cloudcoverpercentage=(0, 30),
                         processinglevel = 'Level-2A')
    # products = api.query(footprint, date=('20211219', date(2021, 12, 29)),
    #                      platformname='Sentinel-2',
    #                      cloudcoverpercentage=(0, 30),
    #                      limit=1)
    # print(len(products))
    # print(products)
    return products


def extract_frames_to_gzips(api, products, limit, directory):
    #print(products.items())
    for item in products:
        print(products[item]['summary'])

    single_frame_product = next(iter(products))
    productPrint = products[single_frame_product]['footprint']
    current_count = 0
    last_date = date.today()
    ignores=['S2A_MSIL2A_20211209T083341_N0301_R021_T36RUV_20211209T104201','S2B_MSIL2A_20220113T083219_N0301_R021_T36RUV_20220113T105226','S2B_MSIL2A_20220212T082939_N0400_R021_T36RUV_20220212T112743','S2B_MSIL2A_20220423T082559_N0400_R021_T36RUV_20220423T114801']
    for item in products:
        if current_count < limit:
            if 'generationdate' in products[item].keys():
                if products[item]['footprint'] == productPrint and products[item]['generationdate'].date() <= last_date - timedelta(days=7) and products[item]['identifier'] not in ignores:
                    last_date = products[item]['generationdate'].date()
                    print(last_date)
                    #continue
                    if current_count>-1:
                        try:
                            api.download(item)
                        except Exception as e:
                            print(e)
                            print('error downloading')
                            continue
                        pixels_array = get_pixels_from_files(products[item]['identifier'])
                        if len(pixels_array) != 0:
                            current_count += 1
                        os.remove(f'{products[item]["identifier"]}.zip')
                        pickle_file_path = f'{directory}/{products[item]["identifier"]}_{last_date}.pickle'
                        try:
                            pickle.dump(pixels_array, open(pickle_file_path, "wb"))
                        except (OSError, IOError) as e:
                            pickle.dump(pixels_array, open(pickle_file_path, "wb"))

                        # with open(pickle_file_path, 'rb') as f_in:
                        #     with gzip.open(f'{pickle_file_path}.gz', 'wb') as f_out:
                        #         shutil.copyfileobj(f_in, f_out)

                        # os.remove(pickle_file_path)
                        print(products[item]['generationdate'])
                    else:
                        current_count += 1


def extract_frames_to_gzips2(api, products, limit, directory):
    #print(products.items())
    for item in products:
        print(products[item]['summary'])

    single_frame_product = next(iter(products))
    productPrint = products[single_frame_product]['footprint']
    current_count = 0
    last_date = date.today()
    ignores=['S2A_MSIL2A_20211209T083341_N0301_R021_T36RUV_20211209T104201','S2B_MSIL2A_20220113T083219_N0301_R021_T36RUV_20220113T105226','S2B_MSIL2A_20220212T082939_N0400_R021_T36RUV_20220212T112743','S2B_MSIL2A_20220423T082559_N0400_R021_T36RUV_20220423T114801']
    for item in products:
        if current_count < limit:
            if 'generationdate' in products[item].keys():
                if products[item]['footprint'] == productPrint and products[item]['generationdate'].date() <= last_date - timedelta(days=7) and products[item]['identifier'] not in ignores:
                    last_date = products[item]['generationdate'].date()
                    print(last_date)
                    #continue
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
                            pickle.dump(pixels_array, open(pickle_file_path, "wb"))

                        # with open(pickle_file_path, 'rb') as f_in:
                        #     with gzip.open(f'{pickle_file_path}.gz', 'wb') as f_out:
                        #         shutil.copyfileobj(f_in, f_out)

                        # os.remove(pickle_file_path)
                        print(products[item]['generationdate'])
                    else:
                        current_count += 1


def plot_vege_moist(frame):
    frame.plot(legend=False)
    plt.xlabel('Indeks wilgotności')
    plt.ylabel('Indeks wegetacji')
    plt.show()
    # Image.fromarray(vegeIndex,'L').show()
    # Image.frombytes('L',(5490,5490),vegeIndex).show()


def plot_time_plot(dates, frames):
    labels = dates
    maxes = []
    averages = []
    
    for frame in frames:
        frame.reset_index(inplace=True,drop=True)
        # max = frame[frame[1] == frame[1].max()].fillna(0).values.flatten().tolist()
        # print(max)
        # maxes.append(max[1])
        # averages.append(max[0])
        max = frame.groupby(by=0).mean()
        print(max)
        print('\n\nselected:\n')
        max = max[max[1]==max[1].max()].reset_index(drop=True)
        
        #max=max.values.flatten().tolist()
        print(max)
        maxes.append(max[1])    
        averages.append(max[0])
        
    zipped = zip(labels,maxes,averages)
    sortedZip = sorted(zipped)
    labels,maxes,averages = zip(*sortedZip)

    # maxes = maxes/numpy.linalg.norm(maxes)
    # averages = averages/numpy.linalg.norm(averages)
    x = numpy.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width / 2, maxes, width, label='Wegetacja')
    rects2 = ax.bar(x + width / 2, averages, width, label='Wilgotność')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Wartość indeksu')
    ax.set_xlabel('Data')
    ax.set_title('Wilgotność i wegetacja wg daty')
    ax.set_xticks(x, labels)
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    fig.tight_layout()
    plt.savefig('./plotted.png')
    #plt.show()



def plot_time_plot_outter(dates,maxes,averages):
    labels = dates
    zipped = zip(labels,maxes,averages)
    sortedZip = sorted(zipped)
    labels,maxes,averages = zip(*sortedZip)
    
    # maxes = maxes/numpy.linalg.norm(maxes)
    # averages = averages/numpy.linalg.norm(averages)
    x = numpy.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width / 2, maxes, width, label='Wegetacja')
    rects2 = ax.bar(x + width / 2, averages, width, label='Wilgotność')
    fig.set_figheight(6)
    fig.set_figwidth(15)
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Wartość indeksu')
    ax.set_xlabel('Data')
    ax.set_title('Wilgotność i wegetacja wg daty')
    ax.set_xticks(x, labels)
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    fig.tight_layout()
    
    plt.savefig('./plotted.png')
    #plt.show()

def plot_time_plot_inner(frame):
    frame.reset_index(inplace=True,drop=True)
    # max = frame[frame[1] == frame[1].max()].fillna(0).values.flatten().tolist()
    # print(max)
    # maxes.append(max[1])
    # averages.append(max[0])
    max = frame.groupby(by=0).mean()
    print(max)
    print(max[1])
    print(max[1].max())
    print('\n\nselected:\n')
    max = max[max[1]==max[1].max()]
    
    #max=max.values.flatten().tolist()
    print(max)
    return max

def plot_results(directory):
    #pixels_dictionaries = list()
    frames = list()
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
                #print(pixels_dictionary)
                #pixels_dictionaries.append(pixels_dictionary)
                moistIndex = moisture(pixels_dictionary)
                vegeIndex = vegetation(pixels_dictionary)
                frame = pd.concat([pd.Series(moistIndex.flatten()), pd.Series(vegeIndex.flatten())], axis=1)
                #frames.append(frame)
                max = plot_time_plot_inner(frame)
                maxes.append(max[1].values[0])
                print('\n\n\nINDEX:\n')
                print(max.index) 
                print(max.index.values)
                print(max.index.values[0])      
                averages.append(max.index.values[0])
                # plot_vege_moist(frame)
    #print(frames)
    print(maxes)
    print(averages)
    plot_time_plot_outter(dates, maxes,averages)




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    load_dotenv()
    # connect to the API
    print(os.environ.get("USER_sentinel"))
    print(os.environ.get("PASSWORD_sentinel"))
    api = SentinelAPI(os.environ.get("USER_sentinel"), os.environ.get("PASSWORD_sentinel"), 'https://apihub.copernicus.eu/apihub') 
    dir = './output3'
   # products = find_products(api, 'geojson/temperate_countryside.geojson', '20201219', date(2022, 4, 29))
   # extract_frames_to_gzips2(api, products, 100, dir)
    plot_results(dir)

    #products2 = find_products(api,'geojson/river_deltas.geojson','20220119',date(2022, 3, 29))
    #products.update(products2)
    #print(products)
    #this downloads 1 product

    #print(productFileName)
    exit(0)
    #api.download(productDWN) #ogarniete title juz
    # print(productDWN)

    #plot_vege_moist("S2A_MSIL2A_20211228T230821_N0301_R015_T49CEN_20211229T021039") #tu tymczasowo na sztywno, ogarniemy dalej automatyzacje
    

    



