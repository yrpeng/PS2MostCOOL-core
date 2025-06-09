# This is Open foam API
import json
import os
import sys
import fnmatch
import shutil
import numpy as np
import subprocess

from core.PSCore import PSCore
from core.APIs.OpenFOAM.foamFuncs import generateSTL, snappyHexMeshDict, controlDict, blockMeshDict, surfaceFeatureExtractDict, createPatchDict, creatRegion, regionProperties, TP, pP, BCs, solutionExport

def constructFoamCase(server, boundryConditions, currentPath, desPath, designInfo):
    """ This functions create OpenFOAM case structure for server that is come from PowerSynyh engine. 
    then run openfoan case and export the results.
    """

    currentPath = currentPath
    sourcePath = os.path.join(PSCore.PSRoot,'lib', 'python3.10', 'site-packages', 'core', 'APIs', 'OpenFOAM', 'FOAM_API_Template', 'foamcase')
    desPath = os.path.join(desPath, 'Initial_Lyout', 'Layout0') 
    if os.path.exists(desPath):
        shutil.rmtree(desPath, ignore_errors= True)

    os.makedirs(desPath, mode = 0o755, exist_ok= True)  

    #files = os.listdir(sourcePath)
    shutil.copytree(sourcePath, desPath, dirs_exist_ok= True)

    for i, comp in enumerate(server):
        comp.x = comp.x/1000
        comp.y = comp.y/1000
        comp.z = comp.z/1000
        if i>1:
            comp.width = round(comp.x + comp.width/1000, ndigits=4)
            comp.length = round(comp.y + comp.length/1000, ndigits=4)
            comp.height = round(comp.z + comp.height/1000, ndigits=4)
        else:
            comp.width = round(comp.width/1000, ndigits=4)
            comp.length = round(comp.length/1000, ndigits=4)
            comp.height = round(comp.height/1000, ndigits=4)
        

        #print(comp)
        generateSTL(comp, desPath, boundryConditions, designInfo)

    snappyHexMeshDict(server, desPath, boundryConditions)
    controlDict(server, desPath)
    blockMeshDict(server, desPath)
    surfaceFeatureExtractDict(server, desPath)
    createPatchDict(server, desPath, boundryConditions)
    creatRegion(server, desPath, 'system')
    creatRegion(server, desPath, 'constant')
    creatRegion(server, desPath, 'zero')
    regionProperties(server, desPath)
    TP(server, desPath)
    pP(server, desPath)
    BCs(server, boundryConditions, desPath)
    
	
    # Run OpenFOAM
    os.chdir(desPath)
    #os.chdir(currentPath)
    #os.chdir(desPath)
    print('Running OpenFOAM ...................')
    script = os.path.join(desPath, 'allRun.sh')
    subprocess.run(script, shell='True', executable="/bin/bash")
    
    # Export the results
    solutionExport(desPath, currentPath, boundryConditions, designInfo, server)
