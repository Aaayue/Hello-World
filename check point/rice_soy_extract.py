import os
import osr
import gdal
import json
import random
import logging
import subprocess
import numpy as np
from shapely import geometry
logger = logging.getLogger()


def getSRSPair(src):
    # 获取投影参考系与地理参考系信息
    pros = osr.SpatialReference()
    pros.ImportFromWkt(src.GetProjection())
    geos = pros.CloneGeogCS()
    return pros, geos


def img2geo(src, x, y):
    # 获取图像坐标与地理坐标的转换
    cols = src.RasterXSize
    rows = src.RasterYSize
    bands = src.RasterCount

    # GDAL六参数模型
    geotransform = src.GetGeoTransform()
    origX = geotransform[0]
    origY = geotransform[3]
    pixel_width = geotransform[1]
    pixel_height = geotransform[5]
    rotate1 = geotransform[2]
    rotate2 = geotransform[4]
    # 坐标转化
    geox = x * pixel_width + origX + y * rotate1
    geoy = y * pixel_height + origY + x * rotate2
    return geox, geoy


def img2latlon(src, x, y):
    geox, geoy = img2geo(src, x, y)
    geos, pros = getSRSPair(src)
    trans = osr.CoordinateTransformation(geos, pros)
    coords = trans.TransformPoint(geox, geoy)
    return [coords[1], coords[0]]


def geo2lonlat(src, geox, geoy):
    geos, pros = getSRSPair(src)
    trans = osr.CoordinateTransformation(geos, pros)
    coords = trans.TransformPoint(geox, geoy)
    return coords[:2]


def clip_tif(src_path, json_path, band=1):
    # clip_path = src_path.replace(".tif", "_clip.tif")
    clip_path = '/home/zy/projects/2017_30m_cdls_clip.img'
    # input("\nssssssss")
    # print(json_path,src_path,clip_path)
    subprocess.run(
        ['gdalwarp', '--config', 'GDALWARP_IGNORE_BAD_CUTLINE', 'YES', '-of', 'HFA', '-overwrite', '-cutline',
         json_path, src_path,
         '-crop_to_cutline', clip_path,
         ])
    # input("ddd")
    tmp = gdal.Open(clip_path)
    if tmp is None:
        logger.debug('Clip-tif failed! T-T')
        return False
    cols = tmp.RasterXSize
    rows = tmp.RasterYSize
    band = tmp.GetRasterBand(band)
    band_arr = band.ReadAsArray(0, 0, cols, rows)
    return tmp, band_arr


def creat_json(polygon, geojson_dict, json_path):
    wkt = polygon.wkt
    str_list = wkt.split('(')[-1].split(')')[0].split(',')
    poly_list = []

    for i in range(len(str_list)):
        tmp1 = str_list[i].split()
        tmp3 = [float(x) for x in tmp1]
        poly_list.append(tmp3)
    # print(poly_list)

    geojson_dict["features"][0]['geometry']["coordinates"] = [poly_list]
    print(geojson_dict)
    with open(json_path, "w") as fp:
        print(json.dumps(geojson_dict), file=fp)


def projcs_trans(src_tif, des_tif):
    subprocess.run(
        ['gdalwarp', '-overwrite', '-s_srs', '/home/zy/projects/utm_15N.prj', '-t_srs',
         '/home/zy/data_pool/cleanup/waterfall_data/tmp/2017_30m_cdls/acea.prj',
         src_tif, des_tif]
    )
    src = gdal.Open(des_tif)
    if src is None:
        logger.debug('Transform-tif failed! T-T')
        return False
    cols = src.RasterXSize
    rows = src.RasterYSize
    band = src.GetRasterBand(1)
    band_arr = band.ReadAsArray(0, 0, cols, rows)
    return src, band_arr


def extract(src_arr, label, num):
    idx = np.where(src_arr == label)
    row_arr = idx[0]
    col_arr = idx[1]
    try:
        rand_idx = random.sample(range(len(row_arr)), num)
    except Exception as e:
        logger.debug('{}, point number beyond the length of source array, {} > {}'.format(e, num, len(row_arr)))
        return
    print(rand_idx[:20])
    rand_row = row_arr[rand_idx]
    rand_col = col_arr[rand_idx]
    label_list = list(zip(rand_col, rand_row))
    return label_list


def rice_soy_extract(tile_path, cdl_path, geojson_dict, json_path):
    """
    function to extract rice and soybean from landsat crop mask
    :param tile_path: landsat tiff path
    :param cdl_path: cdl img path
    :return:
    rice = [(lat1, lon1), (lat2, lon2), ...]
    soybean = [(lat1, lon1), (lat2, lon2), ...]
    """
    # 读取landsat图像和对应的边框坐标
    des_tif = tile_path.replace('.tif', '_nad83.tif')
    src_tile, band2 = projcs_trans(tile_path, des_tif)
    tile_geo_trans = src_tile.GetGeoTransform()
    print(tile_geo_trans)
    cols1 = src_tile.RasterXSize
    rows1 = src_tile.RasterYSize
    tile_arr = src_tile.ReadAsArray(0, 0, cols1, rows1)
    temp1 = tile_geo_trans[0] + tile_geo_trans[1] * cols1
    temp2 = tile_geo_trans[3] + tile_geo_trans[5] * rows1
    x1, y1 = geo2lonlat(src_tile, tile_geo_trans[0], tile_geo_trans[3])
    x2, y1 = geo2lonlat(src_tile, temp1, tile_geo_trans[3])
    x2, y2 = geo2lonlat(src_tile, temp1, temp2)
    x1, y2 = geo2lonlat(src_tile, tile_geo_trans[0], temp2)
    # src_tile_p = [[tile_geo_trans[0], tile_geo_trans[3]], [temp1, tile_geo_trans[3]], [temp1, temp2],
    #               [tile_geo_trans[0], temp2], [tile_geo_trans[0], tile_geo_trans[3]]]
    src_tile_p = [[x1, y1], [x2, y1], [x2, y2], [x1, y2], [x1, y1]]
    poly1 = geometry.Polygon([p[0], p[1]] for p in src_tile_p)
    print(poly1, poly1.is_valid, poly1.exterior.type)
    creat_json(poly1, geojson_dict, json_path)
    cdl_clip_src, cdl_arr = clip_tif(cdl_path, json_path, band=1)
    clip_geo_trans = cdl_clip_src.GetGeoTransform()
    print(clip_geo_trans)
    print(np.shape(tile_arr), np.shape(cdl_arr))
    rice_img = extract(cdl_arr, 3, 10000)
    soy_img = extract(cdl_arr, 5, 10000)
    # 图像坐标转经纬度
    rice_geo = []
    soy_geo = []
    for (x, y) in rice_img:
        geox, geoy = img2latlon(cdl_clip_src, x, y)
        rice_geo.append((geox, geoy))
    for (x, y) in soy_img:
        geox, geoy = img2latlon(cdl_clip_src, x, y)
        soy_geo.append((geox, geoy))
    return rice_geo, soy_geo


if __name__ == '__main__':
    json_path = '/tmp/geo.json'
    geojson_dict = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[]]
                }
            }
        ]
    }
    tile_path = '/home/zy/projects/23-35-20170401-20170630.tif'
    cdl_path = '/home/zy/data_pool/cleanup/waterfall_data/tmp/2017_30m_cdls/2017_30m_cdls.img'
    rice, soy = rice_soy_extract(tile_path, cdl_path, geojson_dict, json_path)
    print(len(rice), 'rice:', rice[1:10])
    print(len(soy), 'soy:', soy[1:10])
    # dict = {'rice': [], 'soy': []}
    # dict['rice'] = rice
    # dict['soy'] = soy
    # print(dict['rice'][1:10])
    # labels = ['rice', 'soy']
    # for label in labels:
    #     path = os.path.join('/home/zy/Documents/crop', label+'_points.json')
    #     with open(path, 'w') as fp:
    #         json.dump(dict[label], fp)
    tile_id = '023-035'
    rice_dict = {tile_id: rice}
    soy_dict = {tile_id: soy}
    np.savez('/home/zy/Documents/crop/rice_distribution_2017.npz', rice_dict)
    np.savez('/home/zy/Documents/crop/soy_distribution_2017.npz', soy_dict)

