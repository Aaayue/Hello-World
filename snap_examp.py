import sys
sys.path.append('/root/.snap/snap-python')
import os
os.environ.update({"LD_LIBRARY_PATH":"."})

import snappy
from snappy import ProductIO

ReprojectOp = snappy.jpy.get_type('org.esa.snap.core.gpf.common.reproject.ReprojectionOp')
in_file = '/home/zy/data_pool/U-TMP/S1A_IW_SLC__1SSV_20150109T112521_20150109T112553_004094_004F43_7041_Cal_deb_Spk_TC.dim'
out_file = '/home/zy/data_pool/U-TMP/S1A_IW_SLC__1SSV_20150109T112521_20150109T112553_004094_004F43_7041_Cal_deb_Spk_TC_reproj.dim'

product = ProductIO.readProduct(in_file)

# op = ReprojectOp()
# op.setSourceProduct(product)
# op.setParameter('crs', 'AUTO:42001')
# op.setParameter('resampling', 'Nearest')

parameters = HashMap()
parameters.put('crs', 'AUTO:42001')
parameters.put('resampling', 'Nearest')
reprojProduct = GPF.createProduct('Reproject', parameters, product)

# sub_product = op.getTargetProduct()
# ProductIO.writeProduct(sub_product, out_file, 'BEAM-DIMAP')

# # 产生了目标文件.dim和文件夹.data,但写入完成后,程序不能自动结束