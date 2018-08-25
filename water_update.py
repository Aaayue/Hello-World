import os
import gdal
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import filters

def seg_td(
        img: bytearray,
        value: int,
        wid: tuple = (5, 5),
        step: tuple = (3, 4),
        water_range: tuple = (-12, -16),
) -> (bytearray, int):
    """
    Function:
        covert to img to bit by threshold
    input:
        img: ...
    output:
        (img, int): ..
        int: threshold
    """
    # get threshold
    blur = cv2.bilateralFilter(img, 15, 15 * 2, 15 / 2)
    blur[np.isnan(blur)] = 0.0
    blur[np.isinf(blur)] = 0.0
    data_mask2 = blur[blur != 0]
    threshold = filters.threshold_otsu(data_mask2)
    if (threshold > water_range[0]) | (threshold < water_range[1]):
        # self.my_logger.warning("Use -13 as threshold here")
        threshold = -13

    ret1, bin_img = cv2.threshold(blur, threshold, value, cv2.THRESH_BINARY_INV)

    return bin_img, ret1

def water_extract(water_range: tuple = (-12, -16), raw_tif) :
    """
    Function:
        post-process tif image
    :param
        self: input .tif file path
    :return:
        src_ds: geo information of input image
        new_img: an nd-array of the processed image
    """
    src_ds = gdal.Open(raw_tif)
    src_geo_trans = src_ds.GetGeoTransform()
    cols = src_ds.RasterXSize
    rows = src_ds.RasterYSize
    band = src_ds.GetRasterBand(1)
    water_data = band.ReadAsArray(0, 0, cols, rows)
    data_mask = np.logical_and(
            np.greater(water_data, 0.0),
            np.less_equal(water_data, 1.0)
            )
    data_orig = np.multiply(data_mask, water_data)
    data_orig[data_orig == 0.0] = 1.0
    data_orig = 10 * np.log10(data_orig)

    # get threshold
    new_img, ret1 = seg_td(data_orig, 255)



