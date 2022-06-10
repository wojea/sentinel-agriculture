# from PIL import Image
import pickle
import rasterio
import numpy as np
from matplotlib import pyplot
from PIL import Image
np.seterr(divide='ignore')
file = '' # plik spakowany w formacie .pickle z pasmami pobranymi z produktow sentinela 2

with open(file, 'rb') as opened:
    pixels_dictionairy = pickle.load(opened)

    #wczytywanie pasm ze slownika
    b = pixels_dictionairy['B02']
    b1 = pixels_dictionairy['B03']
    b2=pixels_dictionairy['B04']
    b3=(pixels_dictionairy['B08'][::2,::2]  + pixels_dictionairy['B08'][1::2,1::2])//2
    b4=pixels_dictionairy['B8A']
    b5=pixels_dictionairy['B11']

    vege = (b3 - b2)//(b3+b2)
    moist = (b4 - b5)//(b4+b5)

    proportion = 64 # proporcja masek do kolorow 1:(proportion-1)

    outBand2 = (proportion-1)*vege//proportion # indeks wegetacji
    outBand3 = (proportion-1)*moist//proportion # indeks wilgotnosci

    empty = 0 *b #pasmo czarnych pixeli

    displayTrueColor = np.dstack((b2,b1,b))//proportion
    displayVegeMask = np.dstack((empty,outBand2,empty))
    displayMoistMask = np.dstack((empty,empty,outBand3))

    # dzielenia zastosowano w celu uniknięcia artefaktów w przejściu z formatu 16 bit do 8 bit

    pyplot.imsave('./out-true.jpg',(proportion * displayTrueColor//128).astype("uint8"))
    pyplot.imsave('./out-vege.jpg',(displayVegeMask//2).astype("uint8"))
    pyplot.imsave('./out-moist.jpg',(displayMoistMask//2).astype("uint8"))
    pyplot.imsave('./out-true-moist.jpg',((displayTrueColor + displayMoistMask)//2).astype("uint8"))
    pyplot.imsave('./out-true-vege.jpg',((displayTrueColor + displayVegeMask)//2).astype("uint8"))
    pyplot.imsave('./out-both-masks.jpg',((displayTrueColor + displayVegeMask + displayMoistMask)//2).astype("uint8"))

    exit(0)
