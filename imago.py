# from PIL import Image
import pickle
import rasterio
from rasterio.windows import Window
import numpy as np
from matplotlib import pyplot
from PIL import Image
np.seterr(divide='ignore')
file = './output3/S2A_MSIL2A_20220227T100951_N0400_R022_T33UWV_20220227T125650_2022-02-27.pickle'
file2 = './output2/S2A_MSIL2A_20220118T083301_N0301_R021_T36RUV_20220118T115959_2022-01-18.pickle'


# testF = './imgoinputs/T36RUV_20211227T084249_B02_20m.jp2'

# test1 = np.array(Image.open(testF)).astype('uint16')
# test2 = rasterio.open(testF,'r').read(1)

# # print(test1)

# # print('\n\n\n\n')
# # print(test2)

# test1Flat = test1.flatten()
# test2Flat = test2.flatten()

# print(np.histogram(test1Flat//test2Flat))

# exit(0)


with open(file2, 'rb') as opened:
    p_d = pickle.load(opened)


    # prefix = './imgoinputs/T36RUV_20211227T084249_'
    # prefix = './imgoinputs2/T49CEN_20211228T230821_'
    # ['B04_10m.jp2', 'B08_10m.jp2', 'B8A_20m.jp2', 'B11_20m.jp2', 'B02_20m.jp2']


    # b = rasterio.open(prefix+'B02_20m.jp2','r') # B
    # b1 =  rasterio.open(prefix+'B03_20m.jp2','r').read(1) # G
    # b2 =  rasterio.open(prefix+'B04_20m.jp2','r').read(1) # R

    # b3 = rasterio.open(prefix+'B08_10m.jp2','r')# resize
    # # b3.transform = b.transform
    # b3 = b3.read(1)
    # b3 = (b3[::2,::2] + b3[1::2,1::2])//2
    # b = b.read(1)
    # b4 = rasterio.open(prefix+'B8A_20m.jp2','r').read(1)
    # b5 = rasterio.open(prefix+'B11_20m.jp2','r').read(1)

    b = p_d['B02']
    b1 = p_d['B03']
    b2=(p_d['B04'][::2,::2]  + p_d['B04'][1::2,1::2])//2
    b3=(p_d['B08'][::2,::2]  + p_d['B08'][1::2,1::2])//2
    #b3 = (b3[::2,::2] + b3[1::2,1::2])//2
    #print(len(b2))
    b4=p_d['B8A']
    b5=p_d['B11']

    print(len(b))
    print(len(b1))
    print(len(b2))
    print(len(b3))
    print(len(b4))
    print(len(b5))

    print('max - ' +  str(np.nan_to_num(np.floor_divide( (b3 - b2),(b3+b2))).max()))
    print('max - ' +  str(np.nan_to_num(np.floor_divide( (b3 - b2),(b3+b2))).min()))
    vege = (b3 - b2)//(b3+b2)

    moist = (b4 - b5)//(b4+b5)

    proportion = 64

    # outBand1 = b2 //proportion
    outBand2 = (proportion-1)*vege//proportion
    outBand3 = (proportion-1)*moist//proportion

    empty = 0 *b


    # with rasterio.open(exampleImg) as opened:
    displayTrueColor = np.dstack((b2,b1,b))//proportion
    displayVegeMask = np.dstack((empty,outBand2,empty)) * 4
    displayMoistMask = np.dstack((empty,empty,outBand3)) * 4
    # print(display)
    #disp = rasterio.plot.show([exampleImg,exampleImg2,exampleImg3])
    pyplot.imsave('./out-true2.jpg',(proportion * displayTrueColor//128).astype("uint8"))
    pyplot.imsave('./out-vege2.jpg',(displayVegeMask//2).astype("uint8"))
    pyplot.imsave('./out-mois2t.jpg',(displayMoistMask//2).astype("uint8"))
    pyplot.imsave('./out-true-moist2.jpg',((displayTrueColor + displayMoistMask)//2).astype("uint8"))
    pyplot.imsave('./out-true-vege2.jpg',((displayTrueColor + displayVegeMask)//2).astype("uint8"))
    pyplot.imsave('./out-both-masks2.jpg',((displayTrueColor + displayVegeMask + displayMoistMask)//2).astype("uint8"))
    # with rasterio.open('./out.jp2','w',driver='JP2OpenJPEG', width=b.width,height=b.height,count=3, dtype=b.dtypes[0], crs=b.crs) as rgb:
    #     rgb.write(b.read(1),1)
    #     rgb.write(b1.read(1),2)
    #     rgb.write(b2.read(1),3)



    #pyplot.imsave('./out.jpg',imgo, cmap='turbo')
    #print(imgo)
    # print(imgo.height)
    # 3imgo.show()
    #e = (np.array(imgo)//256).astype('uint8')
    #Image.fromarray(e).show()
    exit(0)


with open(file, 'rb') as opened:
    pixels_dictionary = pickle.load(opened)
    print(pixels_dictionary)
    imgo = Image.fromarray(pixels_dictionary['B02'],'I;16')
    print(imgo.mode)
    imgo.show()