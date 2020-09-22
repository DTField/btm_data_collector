# Imports
import math
import numpy as np
import arcpy
from arcpy.sa import Aspect, Curvature, Slope, Sin, Cos

from . import utils
from . import ruggedness
from . import surface_area_to_planar_area as SAPR


def main(siteData=None, excel_doc=None, export=False, expFold=None, clipDEM=False, in_dem=None, clipOrtho=False, in_ortho=None):
    
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = siteData
    
    data = np.ones([1, 10], dtype = object)
    
    
    utils.msg ("The Mean Complexity Value Collector is doing something...")
    
    
    try:
        if clipDEM is True:
        
            utils.msg("Clipping DEMs...")
            
            clipPolys = arcpy.ListFeatureClasses("*", "Polygon")
            
            for clipPoly in clipPolys:
                
                utils.msg(clipPoly)
                
                desc = arcpy.Describe(clipPoly)
                ext = desc.extent
                
                arcpy.Clip_management(in_dem, str(ext), siteData + "//" + clipPoly + "_DEM_1cm_Clip", clipPoly, "#", "ClippingGeometry")
            
    except Exception as e:
        utils.msg(e, mtype='error')
        
    try:
        if clipOrtho is True:
        
            utils.msg("Clipping DEMs...")
            
            clipPolys = arcpy.ListFeatureClasses("*", "Polygon")
            
            for clipPoly in clipPolys:
                
                utils.msg(clipPoly)
                
                desc = arcpy.Describe(clipPoly)
                ext = desc.extent
                
                arcpy.Clip_management(in_ortho, str(ext), siteData + "//" + clipPoly + "_Ortho_Clip", clipPoly, "#", "ClippingGeometry")
            
    except Exception as e:
        utils.msg(e, mtype='error')
        
    
    try:
        
        if export is True:
            
            clips = arcpy.ListRasters("*","ALL")
            
            for clip in clips:
                if clip.endswith("Clip"):
                    arcpy.RasterToOtherFormat_conversion(clip, expFold, "TIFF")
        
    except Exception as e:
        utils.msg(e, mtype='error')
        
    
    
    try:    
        
        #get raster clips
        demClips = arcpy.ListRasters("*", "ALL")
        
        #Collect BTM complexity data        
        for input_raster in demClips:
            
            utils.msg(input_raster)
            
            if input_raster.endswith("_DEM_1cm_Clip"):
                
                rasterName = str(input_raster).replace("_DEM_1cm_Clip","")
                data[0,0] = rasterName
                
                #aspect
                utils.msg("Calculating aspect...")
                aspect = Aspect(input_raster)
                aspect.save(siteData + "//" + rasterName + "_Aspect_1cm")
                
                meanAspectResult = arcpy.GetRasterProperties_management(aspect, "Mean")
                meanAspect = meanAspectResult.getOutput(0)
                data[0,1] = str(meanAspect)
                
                #Statistical aspect
                utils.msg("Calculating statistical aspects...")
                
                aspect_rad = aspect * (math.pi / 180)
                
                aspect_sin = Sin(aspect_rad)
                aspect_sin.save(siteData + "//" + rasterName + "_Aspect_sin_1cm")
                aspect_cos = Cos(aspect_rad)
                aspect_cos.save(siteData + "//" + rasterName + "_Aspect_cos_1cm")
                
                meanAspSinResult = arcpy.GetRasterProperties_management(aspect_sin, "Mean")
                meanAspSin = meanAspSinResult.getOutput(0)
                data[0,2] = str(meanAspSin)
                
                meanAspCosResult = arcpy.GetRasterProperties_management(aspect_cos, "Mean")
                meanAspCos = meanAspCosResult.getOutput(0)
                data[0,3] = str(meanAspCos)
                
                #slope
                utils.msg("Calculating BTM slope...")
                M = Slope(input_raster, "DEGREE", 1)
                M.save(siteData + "//" + rasterName + "_Slope_1cm")
                meanMResult = arcpy.GetRasterProperties_management(M, "Mean")
                meanM = meanMResult.getOutput(0)
                data[0,4] = str(meanM)
                
                
                #Curvature
                utils.msg("Calculating Curvatures...")
                
                curv = Curvature(input_raster, 1, siteData + "//" + rasterName + "_Curv_pro_1cm", siteData + "//" + rasterName + "_Curv_plan_1cm")
                curv.save(siteData + "//" + rasterName + "_Curv_1cm")
                
                proCurv = arcpy.Raster(siteData + "//" + rasterName + "_Curv_pro_1cm")
                planCurv = arcpy.Raster(siteData + "//" + rasterName + "_Curv_plan_1cm")
                
                meanCurvResult = arcpy.GetRasterProperties_management(curv, "Mean")
                meanCurv = meanCurvResult.getOutput(0)
                data[0,5] = str(meanCurv)
                
                meanProCurvResult = arcpy.GetRasterProperties_management(proCurv, "Mean")
                meanProCurv = meanProCurvResult.getOutput(0)
                data[0,6] = str(meanProCurv)
                
                meanPlanCurvResult = arcpy.GetRasterProperties_management(planCurv, "Mean")
                meanPlanCurv = meanPlanCurvResult.getOutput(0)
                data[0,7] = str(meanPlanCurv)
                
                #surface area to planar ratio
                utils.msg("Calculating Surface Area to Planar Ratio...")
            
                SAPR.main(input_raster, siteData + "//" + rasterName + "_SAPR_1cm")
            
                sapr = arcpy.Raster(siteData + "//" + rasterName + "_SAPR_1cm")
                    
                meanSAPRResult = arcpy.GetRasterProperties_management(sapr, "Mean")
                meanSAPR = meanSAPRResult.getOutput(0)
                data[0,8] = str(meanSAPR)
                
                
                #vrm
                utils.msg("Calculating VRM...")
                
                ruggedness.main(input_raster, 3, siteData + "//" + rasterName + "_VRM_1cm")
                vrm = arcpy.Raster(siteData + "//" + rasterName + "_VRM_1cm")
                
                meanVRMResult = arcpy.GetRasterProperties_management(vrm, "Mean")
                meanVRM = meanVRMResult.getOutput(0)
                data[0,9] = str(meanVRM)
                
                #Saving the data
                utils.msg("Writing to .csv...")
                
                with open(excel_doc, "ab") as f:
                    np.savetxt(f, data, delimiter=',', fmt = '%s')
                
    except Exception as e:
            utils.msg(e, mtype='error')