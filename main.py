# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
from zipfile import Path, ZipFile

from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
from dotenv import load_dotenv # take environment variables from .env.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    load_dotenv()
    # connect to the API
    api = SentinelAPI(os.environ.get("USER"), os.environ.get("PASSWORD"), 'https://apihub.copernicus.eu/apihub')

    # download single scene by known product id
    # api.download('21d68494-012e-4416-b5a4-810959b00d4e')

    # search by polygon, time, and Hub query keywords
    # footprint = geojson_to_wkt(read_geojson('map.geojson'))
    products = api.query(date=('20211219', date(2021, 12, 29)),
                         platformname='Sentinel-2',
                         cloudcoverpercentage=(0, 30),
                         limit=1)

    api.download(next(iter(products)))
    with ZipFile(f'{products[next(iter(products))]["title"]}.zip', 'r') as satelite_zip:
        list_of_all_subfiles = ZipFile.infolist(satelite_zip)
        allowed_formats = ['B04_20m.jp2', 'B03_20m.jp2', 'B02_20m.jp2']
        filtered_files = list()
        for allowed_format in allowed_formats:
            filtered_files_part = [k for k in list_of_all_subfiles if allowed_format in k.filename]
            filtered_files.extend(filtered_files_part)
        opened_files = [satelite_zip.open(filtered_file) for filtered_file in filtered_files]
        print(opened_files)

    # archive = Path(ZipFile(f'{products[next(iter(products))]["title"]}.zip', 'r')).iterdir()
    # for x in archive:
    #     xsliced = str(x)[:-1]
    #     print(xsliced)
    #     subdir = Path.open(x)
    #     for y in subdir:
    #         print(y)
    # print(archive)
    # print(next(iter(products)))
    # print('\n')
    # print(api.get_product_odata('14a2aa57-167c-49c0-b0bf-7623a8f74247'))
    # api.download('14a2aa57-167c-49c0-b0bf-7623a8f74247')
    # api.to_geojson(products)

    # # download all results from the search
    # api.download_all(products)
    #
    # # GeoJSON FeatureCollection containing footprints and metadata of the scenes
    # api.to_geojson(products)
    #
    # # GeoPandas GeoDataFrame with the metadata of the scenes and the footprints as geometries
    # api.to_geodataframe(products)

    # # Get basic information about the product: its title, file size, MD5 sum, date, footprint and
    # # its download url
    # api.get_product_odata(<product_id>)
    #
    # # Get the product's full metadata available on the server
    # api.get_product_odata(<product_id>, full=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
