import math
import osgeo.ogr as ogr
from rsgislib.vectorutils import createPolyVecBBOXs
from rsgislib.vectorutils import writeVecColumn
from rsgislib.vectorutils import popBBOXCols

def zero_pad_num_str(num_val, str_len=3, round_num=False, round_n_digts=0, integerise=False):
    """
    A function which zero pads a number to make a string

    :param num_val: number value to be processed.
    :param str_len: the number of characters in the output string.
    :param round_num: boolean whether to round the input number value.
    :param round_n_digts: If rounding, the number of digits following decimal points to round to.
    :param integerise: boolean whether to integerise the input number
    :return: string with the padded numeric value.

    """
    if round_num:
        num_val = round(num_val, round_n_digts)
    if integerise:
        num_val = int(num_val)

    num_str = "{}".format(num_val)
    num_str = num_str.zfill(str_len)
    return num_str
    

def create_latlon_name(x_col_val, y_col_val, prefix='', postfix='', latlong=True, int_coords=True, zero_x_pad=3, zero_y_pad=2, non_neg=True):
    """
    
    """
    name = ""
    if int_coords:
        x_col_val = int(x_col_val)
        y_col_val = int(y_col_val)
    
    x_col_val_neg = False
    y_col_val_neg = False
    if non_neg:
        if x_col_val < 0:
            x_col_val_neg = True
            x_col_val = x_col_val * (-1)
        if y_col_val < 0:
            y_col_val_neg = True
            y_col_val = y_col_val * (-1)
    
    if zero_x_pad > 0:
        x_col_val_str = zero_pad_num_str(x_col_val, str_len=zero_x_pad, round_num=False, round_n_digts=0, integerise=int_coords)
    else:
        x_col_val_str = '{}'.format(x_col_val)
        
    if zero_y_pad > 0:
        y_col_val_str = zero_pad_num_str(y_col_val, str_len=zero_y_pad, round_num=False, round_n_digts=0, integerise=int_coords)
    else:
        y_col_val_str = '{}'.format(y_col_val)
    
    if latlong:
        hemi = 'N'
        if y_col_val_neg:
            hemi = 'S'
        east_west = 'E'
        if x_col_val_neg:
            east_west = 'W'
        
        name = '{}{}{}{}{}{}'.format(prefix, hemi, y_col_val_str, east_west, x_col_val_str, postfix)
    else:
        name = '{}E{}N{}{}'.format(prefix, x_col_val_str, y_col_val_str, postfix)
        
    return name


def createWGS84VectorGrid(outputVec, vecDriver, vecLyrName, grid_x, grid_y, bbox, overlap=None, tile_names_col='tile_names', tile_name_prefix=''):
    """
A function which creates a regular grid across a defined area.

:param outputVec: outout file
:param vecDriver: the output vector layer type.
:param vecLyrName: output vector layer
:param epsgCode: EPSG code of the output projection
:param grid_x: the size in the x axis of the grid cells.
:param grid_y: the size in the y axis of the grid cells.
:param bbox: the area for which cells will be defined (MinX, MaxX, MinY, MaxY).
:param overlap: the overlap added to each grid cell. If None then no overlap applied.

"""
    epsgCode = 4326
    minX = float(bbox[0])
    maxX = float(bbox[1])
    minY = float(bbox[2])
    maxY = float(bbox[3])
    grid_x = float(grid_x)
    grid_y = float(grid_y)
    
    nXCells = math.floor((maxX-minX)/grid_x)
    x_remain = (maxX-minX) - (grid_x * nXCells)
    
    nYCells = math.floor((maxY-minY)/grid_y)
    y_remain = (maxY-minY) - (grid_y * nYCells)
    
    print("Cells: [{0}, {1}]".format(nXCells, nYCells))
    
    bboxs = []
    tile_names = []
    for i in range(nYCells):
        cMaxY = maxY - (i*grid_y)
        cMinY = cMaxY - grid_y
        for j in range(nXCells):
            cMinX = minX + (j*grid_x)
            cMaxX = cMinX + grid_x
            tile_names.append(create_latlon_name(cMinX, cMaxY, prefix=tile_name_prefix))
            if overlap is None:
                bboxs.append([cMinX, cMaxX, cMinY, cMaxY])
            else:
                bboxs.append([cMinX-overlap, cMaxX+overlap, cMinY-overlap, cMaxY+overlap])
        if x_remain > 0:
            cMinX = minX + (nXCells*grid_x)
            cMaxX = cMinX + x_remain
            tile_names.append(create_latlon_name(cMinX, cMaxY, prefix=tile_name_prefix))
            if overlap is None:
                bboxs.append([cMinX, cMaxX, cMinY, cMaxY])
            else:
                bboxs.append([cMinX-overlap, cMaxX+overlap, cMinY-overlap, cMaxY+overlap])
    if y_remain > 0:
        cMaxY = maxY - (nYCells*grid_y)
        cMinY = cMaxY - y_remain
        for j in range(nXCells):
            cMinX = minX + (j*grid_x)
            cMaxX = cMinX + grid_x
            tile_names.append(create_latlon_name(cMinX, cMaxY, prefix=tile_name_prefix))
            if overlap is None:
                bboxs.append([cMinX, cMaxX, cMinY, cMaxY])
            else:
                bboxs.append([cMinX-overlap, cMaxX+overlap, cMinY-overlap, cMaxY+overlap])
        if x_remain > 0:
            cMinX = minX + (nXCells*grid_x)
            cMaxX = cMinX + x_remain
            tile_names.append(create_latlon_name(cMinX, cMaxY, prefix=tile_name_prefix))
            if overlap is None:
                bboxs.append([cMinX, cMaxX, cMinY, cMaxY])
            else:
                bboxs.append([cMinX-overlap, cMaxX+overlap, cMinY-overlap, cMaxY+overlap])
    
    for bbox in bboxs:
        if bbox[2] < -180:
            bbox[2] = -180
        if bbox[3] > 180:
            bbox[3] = 180
    
    createPolyVecBBOXs(outputVec, vecLyrName, vecDriver, epsgCode, bboxs)
    writeVecColumn(outputVec, vecLyrName, tile_names_col, ogr.OFTString, tile_names)


createWGS84VectorGrid('../../srtm_overlap_tiles.gpkg', 'GPKG', 'srtm_tiles', 1, 1, [-180, 180, -56, 60], overlap=0.0277777778, tile_name_prefix='srtm_')
popBBOXCols('../../srtm_overlap_tiles.gpkg', 'srtm_tiles', xminCol='xmin', xmaxCol='xmax', yminCol='ymin', ymaxCol='ymax')

createWGS84VectorGrid('../../srtm_tiles.gpkg', 'GPKG', 'srtm_tiles', 1, 1, [-180, 180, -56, 60], tile_name_prefix='srtm_')
popBBOXCols('../../srtm_tiles.gpkg', 'srtm_tiles', xminCol='xmin', xmaxCol='xmax', yminCol='ymin', ymaxCol='ymax')


