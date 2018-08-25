import cv2
import numpy as np
from skimage import data,filters
import matplotlib.pyplot as plt


image = cv2.imread('/home/zy/data_pool/U-TMP/out/S1A_IW_GRDH_1SSV_20150109T112521_20150109T112553_004094_004F43_7041_Cal_Deb_ML_Spk_SRGR_TC.tif',-1)
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# 异常值处理，以35为分界线
un_index = np.where(image>=1.0)
un_x = un_index[0]
un_y = un_index[1]
num = len(un_x)

for i in range(num):
    image[un_x[i], un_y[i]] = 1.0

eps = 1e-7
temp = 10*np.log(image+eps)
temp-=np.min(temp)
image = temp.astype('uint8')



# thresh = filters.threshold_otsu(temp)   #返回一个阈值
# print('threshold:', thresh)

plt.subplot(131), plt.imshow(image)
plt.title("source image"), plt.xticks([]), plt.yticks([])
plt.subplot(132)
plt.hist(image.ravel(), 256, range=(0,255), fc='k', ec='k')
plt.title("Histogram"), plt.xticks([]), plt.yticks([])
blur = cv2.GaussianBlur(image,(5,5),0)
# ret1, th1 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
# ret1, th1 = cv2.threshold(image, 0.044, 255, cv2.THRESH_BINARY_INV)
ret1, th1 = cv2.adaptiveThreshold(image, 255, )
print('threshold is ', ret1)
plt.subplot(133), plt.imshow(th1, "gray")
plt.title("2-Mode Method"), plt.xticks([]), plt.yticks([])
plt.show()
