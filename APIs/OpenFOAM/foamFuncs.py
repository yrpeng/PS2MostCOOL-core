# This Scrip contains functions to craete OpenFoam dictionaries and files.
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import matplotlib.animation as animation
import shutil
from functools import reduce
from stl import mesh
from stl import stl
import json
import fluidfoam as ff
import traceback
from core.PSCore import PSCore

sourcePath = sourcePath = os.path.join(PSCore.PSRoot,'lib', 'python3.10', 'site-packages', 'core', 'APIs', 'OpenFOAM', 'FOAM_API_Template', 'scripts')

def generateSTL(components, path, boundryConditions, designInfo):
    """ 
    This function creates the stl files based on the geometry of server and its components. 
    such as PCB, CPUs, GPUs, HS, and PSUs , 
    """
    
    search_text = "X"
    search_text1 = "Y"
    search_text2 = "Z"
    search_text3 = "L"
    search_text4 = "W"
    search_text5 = "H"
    search_text6 = "h"  # for Heat Sink

    replace_text = str(components.x)
    replace_text1 = str(components.y)
    replace_text2 = str(components.z)
    replace_text3 = str(components.width)
    replace_text4 = str(components.length)
    replace_text5 = str(components.height)
    if components.name[0:2] == 'HS':    # HS
        #print(components.height, round(components.power[0]/1000, ndigits=4))
        direction = boundryConditions[1]['Direction']
        replace_text6 = str(0.30 * (components.height - components.z) + components.z)  #"0.026"
        if designInfo['designType'] == 'Converter':
            '''nFins = 4  # 10 for server board and 5 for converter
            width = (components.length - components.y)
            #space = width/(2*nFins) # for server board
            #start = space/2 # for server board
            #w = np.arange(start, width, space) + float(replace_text1)  # for server board
            w = np.zeros((1, 2*nFins-1))
            finsWidth = (width/0.04)*0.003
            #print(finsWidth)
            finChannel = (width - nFins*finsWidth)/(nFins - 1)
            #print(finChannel)
            for ind, i in enumerate(np.arange(0.5, nFins-0.5, 0.5)):
                #print(i)
                w[:, ind] = np.ceil(i)*finsWidth + (np.floor(i)*finChannel)
            w = list(w[0] + + float(replace_text1))
            file = 'heatsink.stl'''

        elif designInfo['designType'] == 'Server':
            pass
            
        finNums = int(components.power[1])
        finWidth = round(components.power[2] / 1000, ndigits=4) # 0.005
        #width = (components.length - components.y)
        if direction in ['RL', 'LR']:
            #print('*********************************************************')
            width = (components.length - components.y)
            chnnelWidth = (width - (finNums * finWidth)) / (finNums - 1)

        elif direction in ['BF', 'FB']:
            #print('----------------------------------------------------')
            width = (components.width - components.x)
            chnnelWidth = (width - (finNums * finWidth)) / (finNums - 1)
        
        #chnnelWidth = (width - (finNums * finWidth)) / (finNums - 1)
        #print('---------------------------------')
        #print('finWidth = ', finWidth)
        #print('chnnelWidth = ', chnnelWidth)
        X = components.x    # X coordinate
        Y = components.y
        Z = components.z
        L = components.width
        W = components.length
        H = Z + round(components.power[0] / 1000, ndigits=4)

        # Define the 8 vertices of the cube
        vertices = np.array([\
            [X, Y, Z],
            [L, Y, Z],
            [L, W, Z],
            [X, W, Z],
            [X, Y, H],
            [L, Y, H],
            [L, W, H],
            [X, W, H]])

        # Define the faces composing the cube
        verticesXmin = np.take(vertices, [0, 4, 7, 3], axis=0)
        verticesXmax = np.take(vertices, [1, 5, 6, 2], axis=0)
        verticesYmin = np.take(vertices, [0, 1, 5, 4], axis=0)
        verticesYmax = np.take(vertices, [3, 2, 6, 7], axis=0)
        verticesZmin = np.take(vertices, [0, 1, 2, 3], axis=0)
        verticesZmax = np.take(vertices, [4, 5, 6, 7], axis=0)
        verticesXYZ = [verticesXmin, verticesXmax, verticesYmin, verticesYmax, verticesZmin, verticesZmax]

        # Define the 12 triangles composing the cube
        facesXmin = np.array([\
            [2, 3, 1],
            [3, 0, 1]])

        facesXmax = np.array([\
            [1, 3, 2],
            [1, 0, 3]])

        facesYmin = np.array([\
            [0, 1, 2],
            [3, 0, 2]])

        facesYmax = np.array([\
            [2, 1, 0],
            [2, 0, 3]])

        facesZmin = np.array([\
            [0, 3, 2],
            [1, 0, 2]])

        facesZmax = np.array([\
            [2, 3, 0],
            [2, 0, 1]])
        facesXYZ = [facesXmin, facesXmax, facesYmin, facesYmax, facesZmin, facesZmax]
        
        # Name of each face
        name = ['x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max']
        # Normal vector
        normal = [[-1, 0, 0], [1, 0, 0], [0, -1, 0], [0, 1, 0], [0, 0, -1], [0, 0, 1]]

        for index in range(len(verticesXYZ)):
            if index == 5:
                pass
            
            else:
                # Create the mesh
                face = mesh.Mesh(np.zeros(facesXYZ[index].shape[0], dtype=mesh.Mesh.dtype), calculate_normals=False)
                #face = mesh.Mesh(np.zeros(facesXYZ[index].shape[0], dtype=mesh.Mesh.dtype))
                for i, f in enumerate(facesXYZ[index]):
                    face.normals = normal[index]
                    for j in range(3):
                        face.vectors[i][j] = verticesXYZ[index][f[j],:]
                
                fileName = os.path.join(sourcePath, 'face.stl')
                face.save(fileName,mode=stl.ASCII, update_normals=False)
                
                with open(fileName, 'r') as file:
                    data = file .read()
                
                filePath = os.path.join(path, 'constant/triSurface/')
                fileName = filePath + components.name + '.stl' 
                with open(fileName, 'a') as file:
                    file.write(data)
                    file.close()
        # Creating Fins
        if direction in ['RL', 'LR']:
            start = components.y
            stop = components.y + width
            translation = np.array([[0, finWidth, 0], [0, finWidth, 0], [0,chnnelWidth , 0], [0, chnnelWidth, 0]])
        elif direction in ['BF', 'FB']:
            start = components.x
            stop = components.x + width
            translation = np.array([[finWidth, 0, 0], [chnnelWidth, 0, 0], [chnnelWidth, 0 , 0], [finWidth, 0, 0]])

        for num, value in enumerate(np.arange(start, stop, finWidth + chnnelWidth)):
            
            if direction in ['RL', 'LR']:
                X = components.x    # X coordinate
                Y = value
                Z = components.z + round(components.power[0] / 1000, ndigits=4) #Z0 + hsDims[3]
                L = components.width    #X + hsDims[0]
                W = Y + finWidth
                H = components.height   #Z + hsDims[2]
                
            elif direction in ['BF', 'FB']:
                X = value    # X coordinate
                Y = components.y
                Z = components.z + round(components.power[0] / 1000, ndigits=4)
                L = X + finWidth 
                W = components.length
                H = components.height
            
            # Define the 8 vertices of the cube
            vertices = np.array([\
                [X, Y, Z],
                [L, Y, Z],
                [L, W, Z],
                [X, W, Z],
                [X, Y, H],
                [L, Y, H],
                [L, W, H],
                [X, W, H]])
            
            # Define the faces composing the cube
            verticesXmin = np.take(vertices, [0, 4, 7, 3], axis=0)
            verticesXmax = np.take(vertices, [1, 5, 6, 2], axis=0)
            verticesYmin = np.take(vertices, [0, 1, 5, 4], axis=0)
            verticesYmax = np.take(vertices, [3, 2, 6, 7], axis=0)
            verticesZmin = np.take(vertices, [0, 1, 2, 3], axis=0)
            verticesZmax = np.take(vertices, [4, 5, 6, 7], axis=0)
            verticesXYZ = [verticesXmin, verticesXmax, verticesYmin, verticesYmax, verticesZmin, verticesZmax]
            
            # Define the 12 triangles composing the cube
            facesXmin = np.array([\
                [2, 3, 1],
                [3, 0, 1]])
            
            facesXmax = np.array([\
                [1, 3, 2],
                [1, 0, 3]])
            
            facesYmin = np.array([\
                [0, 1, 2],
                [3, 0, 2]])
            
            facesYmax = np.array([\
                [2, 1, 0],
                [2, 0, 3]])
            
            facesZmin = np.array([\
                [0, 3, 2],
                [1, 0, 2]])
            
            facesZmax = np.array([\
                [2, 3, 0],
                [2, 0, 1]])
            facesXYZ = [facesXmin, facesXmax, facesYmin, facesYmax, facesZmin, facesZmax]
            
            name = ['x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max']
            
            normal = [[-1, 0, 0], [1, 0, 0], [0, -1, 0], [0, 1, 0], [0, 0, -1], [0, 0, 1]]
            
            for index in range(len(verticesXYZ)):
                if index == 4 and num < (finNums - 1):

                    #translation = np.array([[0, finWidth, 0], [0, finWidth, 0], [0,chnnelWidth , 0], [0, chnnelWidth, 0]])
                    verticesXYZ[index] += translation
                elif num >= (finNums - 1) and index == 4:
                    index += 1
                # Create the mesh
                face = mesh.Mesh(np.zeros(facesXYZ[index].shape[0], dtype=mesh.Mesh.dtype), calculate_normals=False)
                for i, f in enumerate(facesXYZ[index]):
                    face.normals = normal[index]
                    for j in range(3):
                        face.vectors[i][j] = verticesXYZ[index][f[j],:]

                fileName = os.path.join(sourcePath, 'face.stl')
                face.save(fileName,mode=stl.ASCII, update_normals=False)
                
                with open(fileName, 'r') as file:
                    data = file .read()
                
                filePath = os.path.join(path, 'constant/triSurface/')
                fileName = filePath + components.name + '.stl' 
                with open(fileName, 'a') as file:
                    file.write(data)
                    file.close()

    else:   # Components
        X = components.x    # X coordinate
        Y = components.y
        Z = components.z
        L = components.width
        W = components.length
        H = components.height

        # Define the 8 vertices of the cube
        vertices = np.array([\
            [X, Y, Z],
            [L, Y, Z],
            [L, W, Z],
            [X, W, Z],
            [X, Y, H],
            [L, Y, H],
            [L, W, H],
            [X, W, H]])

        # Define the faces composing the cube
        verticesXmin = np.take(vertices, [0, 4, 7, 3], axis=0)
        verticesXmax = np.take(vertices, [1, 5, 6, 2], axis=0)
        verticesYmin = np.take(vertices, [0, 1, 5, 4], axis=0)
        verticesYmax = np.take(vertices, [3, 2, 6, 7], axis=0)
        verticesZmin = np.take(vertices, [0, 1, 2, 3], axis=0)
        verticesZmax = np.take(vertices, [4, 5, 6, 7], axis=0)
        verticesXYZ = [verticesXmin, verticesXmax, verticesYmin, verticesYmax, verticesZmin, verticesZmax]

        # Define the 12 triangles composing the cube
        facesXmin = np.array([\
            [2, 3, 1],
            [3, 0, 1]])

        facesXmax = np.array([\
            [1, 3, 2],
            [1, 0, 3]])

        facesYmin = np.array([\
            [0, 1, 2],
            [3, 0, 2]])

        facesYmax = np.array([\
            [2, 1, 0],
            [2, 0, 3]])

        facesZmin = np.array([\
            [0, 3, 2],
            [1, 0, 2]])

        facesZmax = np.array([\
            [2, 3, 0],
            [2, 0, 1]])
        facesXYZ = [facesXmin, facesXmax, facesYmin, facesYmax, facesZmin, facesZmax]

        name = ['x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max']

        normal = [[-1, 0, 0], [1, 0, 0], [0, -1, 0], [0, 1, 0], [0, 0, -1], [0, 0, 1]]

        for index in range(len(verticesXYZ)):

            # Create the mesh
            face = mesh.Mesh(np.zeros(facesXYZ[index].shape[0], dtype=mesh.Mesh.dtype), calculate_normals=False, name= name[index])
            for i, f in enumerate(facesXYZ[index]):
                face.normals = normal[index]
                for j in range(3):
                    face.vectors[i][j] = verticesXYZ[index][f[j],:]
            fileName = os.path.join(sourcePath, 'face.stl')
            face.save(fileName,mode=stl.ASCII, update_normals=False)
            
            with open(fileName, 'r') as file:
                data = file .read()
            
            filePath = os.path.join(path, 'constant/triSurface/')
            fileName = filePath + components.name + '.stl' 
            with open(fileName, 'a') as file:
                file.write(data)
                file.close()
                
def snappyHexMeshDict(server, path, boundryConditions):
    """ 
    This function creates the snappy hex mesh dictionary.
    """
    
    CGPU, HS, PD = seperate(server)
    direction = boundryConditions[1]['Direction']
    header = 'FoamFile\n{\n\tversion	2.0;\n\tclass	dictionary;\n\tformat	ascii;\n\tlocation	"system";\n\tobject	snappyHexMeshDict;\n}\ncastellatedMesh	true;\nsnap	true;\naddLayers	false;\ngeometry\n{'
    
    fileName = os.path.join(sourcePath, 'snappyHexMeshDict')
    with open(fileName, "w") as file:
        file.write(header)
        file.write('\n')
        file.close()

    for comp in server:
        if comp.material_name == 'aluminum':
            geometry = str('\t' + comp.name + '.stl\n\t{\n\t\ttype	triSurfaceMesh;\n\t\tprimitiveType	box;\n\t\tname	' + comp.name + ';''\n\t\tincludedAngle	120.0;' '\n\t}')
        
        elif comp.name == 'Air':

            if direction == 'LR':
                geometry = str('\t' + comp.name + '.stl\n\t{\n\t\ttype	triSurfaceMesh;\n\t\tprimitiveType	box;\n\t\tname	' + comp.name + ';\
                                \n\t\tmax	(' + str(comp.width) + ' ' + str(comp.length) + ' ' + str(comp.height) + \
                                ');\n\t\tmin	(' + str(comp.x) + ' ' + str(comp.y) + ' ' + str(comp.z) +\
                                    ');\n\t\tfaceGroups\n\t\t{\n\t\t\tx_min\n\t\t\t{\n\t\t\t\tname	' + comp.name + '_inlet' + ';\n\t\t\t}\
                                        \n\t\t\tx_max\n\t\t\t{\n\t\t\t\tname	' + comp.name + '_outlet' + ';\n\t\t\t}\
                                        \n\t\t\ty_min\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t\ty_max\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t\tz_min\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t\tz_max\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t}\
                                        \n\t}')
            elif direction == 'RL':
                geometry = str('\t' + comp.name + '.stl\n\t{\n\t\ttype	triSurfaceMesh;\n\t\tprimitiveType	box;\n\t\tname	' + comp.name + ';\
                                \n\t\tmax	(' + str(comp.width) + ' ' + str(comp.length) + ' ' + str(comp.height) + \
                                ');\n\t\tmin	(' + str(comp.x) + ' ' + str(comp.y) + ' ' + str(comp.z) +\
                                    ');\n\t\tfaceGroups\n\t\t{\n\t\t\tx_min\n\t\t\t{\n\t\t\t\tname	' + comp.name + '_outlet' + ';\n\t\t\t}\
                                        \n\t\t\tx_max\n\t\t\t{\n\t\t\t\tname	' + comp.name + '_inlet' + ';\n\t\t\t}\
                                        \n\t\t\ty_min\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t\ty_max\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t\tz_min\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t\tz_max\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t}\
                                        \n\t}')
            elif direction == 'BF':
                geometry = str('\t' + comp.name + '.stl\n\t{\n\t\ttype	triSurfaceMesh;\n\t\tprimitiveType	box;\n\t\tname	' + comp.name + ';\
                                \n\t\tmax	(' + str(comp.width) + ' ' + str(comp.length) + ' ' + str(comp.height) + \
                                ');\n\t\tmin	(' + str(comp.x) + ' ' + str(comp.y) + ' ' + str(comp.z) +\
                                    ');\n\t\tfaceGroups\n\t\t{\n\t\t\tx_min\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t\tx_max\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t\ty_min\n\t\t\t{\n\t\t\t\tname	' + comp.name + '_outlet' + ';\n\t\t\t}\
                                        \n\t\t\ty_max\n\t\t\t{\n\t\t\t\tname	' + comp.name + '_inlet' + ';\n\t\t\t}\
                                        \n\t\t\tz_min\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t\tz_max\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t}\
                                        \n\t}')
            elif direction == 'FB':
                geometry = str('\t' + comp.name + '.stl\n\t{\n\t\ttype	triSurfaceMesh;\n\t\tprimitiveType	box;\n\t\tname	' + comp.name + ';\
                                \n\t\tmax	(' + str(comp.width) + ' ' + str(comp.length) + ' ' + str(comp.height) + \
                                ');\n\t\tmin	(' + str(comp.x) + ' ' + str(comp.y) + ' ' + str(comp.z) +\
                                    ');\n\t\tfaceGroups\n\t\t{\n\t\t\tx_min\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t\tx_max\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t\ty_min\n\t\t\t{\n\t\t\t\tname	' + comp.name + '_inlet' + ';\n\t\t\t}\
                                        \n\t\t\ty_max\n\t\t\t{\n\t\t\t\tname	' + comp.name + '_outlet' + ';\n\t\t\t}\
                                        \n\t\t\tz_min\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t\tz_max\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t}\
                                        \n\t}')                            
        else:
            geometry = str('\t' + comp.name + '.stl\n\t{\n\t\ttype	triSurfaceMesh;\n\t\tprimitiveType	box;\n\t\tname	' + comp.name + ';\
                                \n\t\tmax	(' + str(comp.width) + ' ' + str(comp.length) + ' ' + str(comp.height) + \
                                ');\n\t\tmin	(' + str(comp.x) + ' ' + str(comp.y) + ' ' + str(comp.z) +\
                                    ');\n\t\tfaceGroups\n\t\t{\n\t\t\tx_min\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t\tx_max\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t\ty_min\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t\ty_max\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t\tz_min\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t\tz_max\n\t\t\t{\n\t\t\t\tname	' + comp.name + ';\n\t\t\t}\
                                        \n\t\t}\
                                        \n\t}')
            
            #print(geometry.expandtabs(4))
            
        with open(fileName, "a") as file:
            file.write(geometry)
            file.write('\n')
            file.close()

    with open(fileName, 'a') as file:
        castellatedMeshControls = '}\ncastellatedMeshControls\n{\n\tlocationsInMesh (\n'
        file.write(castellatedMeshControls)
        file.close()

    for comp in server:

        if comp.name == 'Air':
            locX = comp.x + 0.02
            locY = comp.y + 0.02
            locZ = str(comp.height - 0.010)
            
        elif comp.name in HS:
            locX = comp.x + 0.01
            locY = comp.y + 0.02
            locZ = str(comp.z + 0.005)
        #elif comp.name == 'HS2':
            #locZ = str(comp.z + 0.01)
        elif comp.name in CGPU:
            locX = comp.x + 0.01
            locY = comp.y + 0.01
            locZ = str(comp.height - 0.001)
            
        elif comp.name == 'PCB':
            locX = comp.x + 0.01
            locY = comp.y + 0.01
            locZ = str(comp.height - 0.001)
            
        else:
            locX = comp.x + 0.02
            locY = comp.y + 0.003
            locZ = str(comp.height - 0.01)

        location = '\t\t((' + str(round(locX, ndigits=4)) + ' ' + str(round(locY, ndigits=4)) + ' ' + locZ + ') ' + comp.name.lower() + ')\n'
        with open(fileName, "a") as file:
            file.write(location)
            file.close()        
    with open(fileName, "a") as file:
        file.write(');\n\trefinementSurfaces\n\t{\n')
        file.close()    

    for comp in server:
        if comp.name == 'Air':
            l = 1
            h = 1
        elif comp.name in CGPU:  # in ['CPU1', 'GPU1']:
            l = 1
            h = 2
        elif comp.name in HS:  # in ['CPU1', 'GPU1']:
            l = 1
            h = 2
        elif comp.name == 'PCB':
            l = 1
            h = 2
        elif comp.name[1:3] == 'SU':
            l = 1
            h = 1
        else:
            l = 1
            h = 2
        refinementSurfaces = '\t\t' + comp.name + '\n\t\t{\n\t\t\tlevel ' + '(' + str(l) + ' ' + str(h) + ');\n\t\t\tpatchInfo\n\t\t\t{\n\t\t\t\ttype	wall;\n\t\t\t}\n\t\t}\n'
        with open(fileName, "a") as file:
            file.write(refinementSurfaces)
            file.close()
    with open(fileName, "a") as file:
            file.write('\t}\n\trefinementRegions\n\t{\n\t}\n\tlimitRegions\n\t{\n\t}\n\tfeatures\n\t(\n')
            file.close()

    for comp in server:
        features = '\t{\n\t\tfile ' + '"' + comp.name + '.eMesh";\n\t\tlevels ((0 0));\n\t}\n'
        with open(fileName, "a") as file:
            file.write(features)
            file.close()

    with open(fileName, "a") as file:
            file.write('\t);\n\tmaxLocalCells	1000000;\n\tmaxGlobalCells	10000000;\n\tnCellsBetweenLevels	4;\n\tmaxLoadUnbalance	0.1;\
                    \n\tminRefinementCells	10;\n\tresolveFeatureAngle	30.0;\n\tallowFreeStandingZoneFaces	true;\n}\n')
            file.close()
    with open(fileName, "a") as file:
            snapControls = 'snapControls\n{\n\ttolerance	1.0;\n\tnSmoothPatch	3;\n\tnSolveIter	50;\n\tnRelaxIter	5;\n\tnFeatureSnapIter	10;\
                \n\timplicitFeatureSnap	true;\n\texplicitFeatureSnap	true;\n\tmultiRegionFeatureSnap	true;\n\tnFaceSplitInterval	5;\n}\n'
            file.write(snapControls)
            file.close()
    with open(fileName, "a") as file:
            addLayersControls = 'addLayersControls\n{\n\tlayers\n\t{\n\t}\n\trelativeSizes	true;\n\tminThickness	0.1;\n\tfirstLayerThickness	0.2;\
                \n\texpansionRatio	1.25;\n\tnGrow	0;\n\tfeatureAngle	180.0;\n\tmaxFaceThicknessRatio	0.5;\n\tnSmoothSurfaceNormals	5;\
                \n\tnSmoothThickness	10;\n\tminMedialAxisAngle	90.0;\n\tmaxThicknessToMedialRatio	0.5;\n\tnMedialAxisIter	100;\
                \n\tnSmoothNormals	3;\n\tslipFeatureAngle	30.0;\n\tnRelaxIter	5;\n\tnBufferCellsNoExtrude	0;\n\tnLayerIter	50;\
                \n\tnRelaxedIter	20;\n\tdetectExtrusionIsland	true;\n}\n'
            file.write(addLayersControls)
            file.close()
    with open(fileName, 'a') as file:
            meshQualityControls  = 'meshQualityControls\n{\n\tmaxNonOrtho	65.0;\n\tmaxBoundarySkewness	20.0;\n\tmaxInternalSkewness	4.0;\
                \n\tmaxConcave	80.0;\n\tminVol	1.0E-14;\n\tminTetQuality	1.0E-20;\n\tminArea	-1.0;\n\tminTwist	0.02;\n\tminTriangleTwist	-1.0;\
                \n\tminDeterminant	0.01;\n\tminFaceWeight	0.05;\n\tminVolRatio	0.01;\n\tminVolCollapseRatio	0.1;\n\tnSmoothScale	4;\
                \n\terrorReduction	0.75;\n\trelaxed\n\t{\n\t\tmaxNonOrtho	75.0;\n\t}\n}\nmergeTolerance	1.0E-6;\ndebug	0;' 
            file.write(meshQualityControls)


    with open(fileName, 'r') as file:
        data = file.read()
    filePath = os.path.join(path, 'system/')
    fileNmae = os.path.join(filePath, 'snappyHexMeshDict') 
    with open(fileNmae, 'w') as file: 

         # Writing the replaced data in our 
        # text file 
        file.write(data)
        file.close()
    
def controlDict(server, path):
    """ 
    This function creates the control dictionary.
    """
    
    CGPU, HS, PD = seperate(server)

    header = """FoamFile
{
    class dictionary;
    format ascii;
    location	system;
    object controlDict;
    version 2.0;
}
#include "./inputs"
application	chtMultiRegionSimpleFoam;
deltaT	1;
endTime	$endTime;
purgeWrite	2;
startFrom	latestTime;
startTime	0;
stopAt	endTime;
timeFormat	general;
timePrecision	6;
writeControl	timeStep;
writeInterval	10;
writePrecision	7;
runTimeModifiable	true;
compression	uncompressed;
writeFormat	binary;
libs	("libfvMotionSolvers.dll" "libturbulenceModels.dll" "libturbulenceModelSchemes.dll" "libfvOptions.dll");"""
    fileName = os.path.join(sourcePath, 'controlDict')
    with open(fileName, "w") as file:
        file.write(header)
        #file.write('\n')
        file.close()

    functions = """
functions
{
	writeExtraFieldsInAir
	{
		libs	("libutilityFunctionObjects.dll");
		objects	(rho);
		type	writeObjects;
		writeOption	anyWrite;
		enabled	true;
		log	true;
		writeControl	writeTime;
		region	air;
	}"""

    with open(fileName, "a") as file:
        file.write(functions)
        #file.write('\n')
        file.close()

    i = 0
    for comp in server:
        if comp.name in CGPU:
            name = comp.name
            HS = HS
            surName = '\n\tsurface-' + name + '\n\t{'

            with open(fileName, "a") as file:
                file.write(surName)
                file.close()

            namel = name.lower()
            hs = HS[i].lower()

            temp = """
        type surfaceFieldValue;
        libs
        (
            "fieldFunctionObjects"
        );
        regionType patch;
        name {namel}_to_{hs};
        surfaceFormat none;
        fields
        (
            T
        );
        operation areaAverage;
        writeFields false;
        executeControl timeStep;
        executeInterval 1;
        writeControl timeStep;
        writeInterval 1;
        updateHeader false;
        log false;
        region {namel};""".format(namel=namel, hs=hs)
            
            with open(fileName, "a") as file:
                file.write(temp)
                file.write('\n\t}')
                file.close()
            i+=1
    optimization = """
}
OptimisationSwitches
{
	fileHandler	uncollated;
	fileModificationSkew	0;
	maxMasterFileBufferSize	1.0E9;
	maxThreadFileBufferSize	1.0E9;
	mpiBufferSize	200000000;
}"""

    with open(fileName, "a") as file:
        file.write(optimization)
        file.close()

    with open(fileName, 'r') as file:
        data = file.read()
    filePath = os.path.join(path, 'system/')
    fileNmae = os.path.join(filePath, 'controlDict') 
    with open(fileNmae, 'w') as file: 
        file.write(data)
        file.close()
        
def blockMeshDict(server, path):
    """ 
    This function creates the block mesh dictionary.
    """
    
    header = """FoamFile
{
    version	2.0;
	format	ascii;
	class	dictionary;
	location	"system";
	object	blockMeshDict;
}"""
    fileName = os.path.join(sourcePath, 'blockMeshDict')
    with open(fileName, "w") as file:
            file.write(header)
            file.write('\n')
            file.close()

    for comp in server:
        if comp.name == 'Air':
            
            xmin = round(comp.x  - (0.005 * np.sum(np.abs([comp.x, comp.width]))), ndigits=4)
            xmax = round(comp.width  + (0.005 * np.sum(np.abs([comp.x, comp.width]))), ndigits=4)

            ymin = comp.y  - (0.005 * np.sum(np.abs([comp.y, comp.length])))
            ymax = comp.length  + (0.005 * np.sum(np.abs([comp.y, comp.length])))

            zmin = comp.z  - (0.005 * np.sum(np.abs([comp.z, comp.height])))
            zmax = comp.height  + (0.005 * np.sum(np.abs([comp.z, comp.height])))

            #print(xmin, xmax, ymin, ymax, zmin, zmax)


    vertices = """vertices	(
	({xmin} {ymin} {zmin})
	({xmax} {ymin} {zmin})
	({xmax} {ymax} {zmin})
	({xmin} {ymax} {zmin})
	({xmin} {ymin} {zmax})
	({xmax} {ymin} {zmax})
	({xmax} {ymax} {zmax})
	({xmin} {ymax} {zmax})
);""".format(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax)
    with open(fileName, "a") as file:
            file.write(vertices)
            #file.write('\n')
            file.close()
    block = """
blocks	(
    hex	(0 1 2 3 4 5 6 7) (45 45 15) simpleGrading (1.0 1.0 1.0)
);
edges	();
boundary	(
	boundaries
	{
		type	patch;
		faces	(
			(0 4 7 3)
			(2 6 5 1)
			(1 5 4 0)
			(3 7 6 2)
			(0 3 2 1)
			(4 5 6 7)
		);
	}
);"""
    with open(fileName, "a") as file:
                file.write(block)
                #file.write('\n')
                file.close()
    
    with open(fileName, 'r') as file:
        data = file.read()
    filePath = os.path.join(path, 'system/')
    fileNmae = os.path.join(filePath, 'blockMeshDict') 
    with open(fileNmae, 'w') as file: 
        file.write(data)
        file.close()

def surfaceFeatureExtractDict(server, path):
    """ 
    This function creates the features dictionary.
    """
    
    header = """FoamFile
{
    version	2.0;
	format	ascii;
	class	dictionary;
	location	"system";
	object	surfaceFeatureExtractDict;
}"""
    fileName = os.path.join(sourcePath, 'surfaceFeatureExtractDict')
    with open(fileName, "w") as file:
            file.write(header)
            file.close()

    for comp in server:
        #if comp.name in ['HS1', 'HS2', 'HS3', 'HS4']:
        name = comp.name
        surName = '\n{name}.stl'.format(name=name)

        with open(fileName, "a") as file:
            file.write(surName)
            file.close()
        angle = """
{
    extractionMethod	extractFromSurface;
    includedAngle	120.0;
    geometricTestOnly	false;
}"""
        with open(fileName, "a") as file:
                file.write(angle)
                file.close()
    
    with open(fileName, 'r') as file:
        data = file.read()
    filePath = os.path.join(path, 'system/')
    fileNmae = os.path.join(filePath, 'surfaceFeatureExtractDict') 
    with open(fileNmae, 'w') as file: 
        file.write(data)
        file.close()

def createPatchDict(server, path, boundryConditions):
    """ 
    This function creates the patch dictionary.
    """
    
    CGPU, HS, PD = seperate(server)
    direction = boundryConditions[1]['Direction']
    if direction == 'LR':
        header = """FoamFile
{
    version	2.0;
	format	ascii;
	class	dictionary;
	location	"system";
	object	createPatchDict;
}
pointSync	false;
patches	(
	{
		name	Air;
		patchInfo
		{
			type	wall;
		}
		constructFrom	patches;
		patches	(Air_y_min Air_y_max Air_z_min Air_z_max);
	}

	{
		name	Air_inlet;
		patchInfo
		{
			type	patch;
		}
		constructFrom	patches;
		patches	(Air_x_min);
	}

	{
		name	Air_outlet;
		patchInfo
		{
			type	patch;
		}
		constructFrom	patches;
		patches	(Air_x_max);
	}"""

    elif direction == 'RL':
        header = """FoamFile
{
    version	2.0;
	format	ascii;
	class	dictionary;
	location	"system";
	object	createPatchDict;
}
pointSync	false;
patches	(
	{
		name	Air;
		patchInfo
		{
			type	wall;
		}
		constructFrom	patches;
		patches	(Air_y_min Air_y_max Air_z_min Air_z_max);
	}

	{
		name	Air_inlet;
		patchInfo
		{
			type	patch;
		}
		constructFrom	patches;
		patches	(Air_x_max);
	}

	{
		name	Air_outlet;
		patchInfo
		{
			type	patch;
		}
		constructFrom	patches;
		patches	(Air_x_min);
	}"""

    elif direction == 'BF':
        header = """FoamFile
{
    version	2.0;
	format	ascii;
	class	dictionary;
	location	"system";
	object	createPatchDict;
}
pointSync	false;
patches	(
	{
		name	Air;
		patchInfo
		{
			type	wall;
		}
		constructFrom	patches;
		patches	(Air_x_min Air_x_max Air_z_min Air_z_max);
	}

	{
		name	Air_inlet;
		patchInfo
		{
			type	patch;
		}
		constructFrom	patches;
		patches	(Air_y_max);
	}

	{
		name	Air_outlet;
		patchInfo
		{
			type	patch;
		}
		constructFrom	patches;
		patches	(Air_y_min);
	}"""

    elif direction == 'FB':
         header = """FoamFile
{
    version	2.0;
	format	ascii;
	class	dictionary;
	location	"system";
	object	createPatchDict;
}
pointSync	false;
patches	(
	{
		name	Air;
		patchInfo
		{
			type	wall;
		}
		constructFrom	patches;
		patches	(Air_x_min Air_x_max Air_z_min Air_z_max);
	}

	{
		name	Air_inlet;
		patchInfo
		{
			type	patch;
		}
		constructFrom	patches;
		patches	(Air_y_min);
	}

	{
		name	Air_outlet;
		patchInfo
		{
			type	patch;
		}
		constructFrom	patches;
		patches	(Air_y_max);
	}"""

    
    fileName = os.path.join(sourcePath, 'createPatchDict')
    with open(fileName, "w") as file:
            file.write(header)
            file.close()
    
    for comp in server:
        if comp.name in HS:
            with open(fileName, "a") as file:
                file.write('\n\n\t{')
                file.close()
            
            name = comp.name
            surName = '\n\t\tname\t{name};\n\t\tpatchInfo'.format(name=name)

            with open(fileName, "a") as file:
                file.write(surName)
                file.close()
            patchInfo = """
		{
			type	wall;
		}
		constructFrom	patches;
        """
            with open(fileName, "a") as file:
                    file.write(patchInfo)
                    file.close()
            patches = """patches	({name}__default);""".format(name=name)
            with open(fileName, "a") as file:
                    file.write(patches)
                    file.write('\n\t}')
                    file.close()
        
        elif  comp.name == 'Air':
             pass
        
        else: 
            with open(fileName, "a") as file:
                file.write('\n\n\t{')
                file.close()

            name = comp.name
            surName = '\n\t\tname\t{name};\n\t\tpatchInfo'.format(name=name)

            with open(fileName, "a") as file:
                file.write(surName)
                file.close()
            patchInfo = """
		{
			type	wall;
		}
		constructFrom	patches;
        """
            with open(fileName, "a") as file:
                    file.write(patchInfo)
                    file.close()

            patches = """patches	({name}_x_min {name}_x_max {name}_y_min {name}_y_max {name}_z_min {name}_z_max);""".format(name=name)
            with open(fileName, "a") as file:
                    file.write(patches)
                    file.write('\n\t}')
                    file.close()
    with open(fileName, "a") as file:
                    file.write('\n);')
                    file.close()         

    with open(fileName, 'r') as file:
        data = file.read()
    filePath = os.path.join(path, 'system/')
    fileNmae = os.path.join(filePath, 'createPatchDict') 
    with open(fileNmae, 'w') as file: 
        file.write(data)
        file.close()
        
def creatRegion(server, path, folder):
    """ 
    This function creates the regions and their corresponding dictionary.
    """
    
    CGPU, HS, PD = seperate(server)
    
    if folder == 'system':
    
        for comp in server:
            if comp.name != 'Air':
                regionName = comp.name.lower()
                desPath = os.path.join(path, 'system/', regionName)
                if os.path.exists(desPath):
                    shutil.rmtree(desPath, ignore_errors= True)

                os.makedirs(desPath, exist_ok= True) 
                    
                    # create fvSolution script
                fileName = os.path.join(sourcePath, 'fvSolution')
                with open(fileName, 'r') as file:
                    data = file.read()
                    data = data.replace('name', regionName)

                fileName = os.path.join(desPath, 'fvSolution')
                with open(fileName, 'w') as file: 
                    file.write(data)
                    file.close()

                    # create fvSchemes script
                fileName = os.path.join(sourcePath, 'fvSchemes')
                with open(fileName, 'r') as file:
                    data = file.read()
                    data = data.replace('name', regionName)

                fileName = os.path.join(desPath, 'fvSchemes')
                with open(fileName, 'w') as file: 
                    file.write(data)
                    file.close()

                    # create decomposeParDict
                fileName = os.path.join(sourcePath, 'decomposeParDict')
                with open(fileName, 'r') as file:
                    data = file.read()
                    data = data.replace('name', regionName)

                fileName = os.path.join(desPath, 'decomposeParDict')
                with open(fileName, 'w') as file: 
                    file.write(data)
                    file.close()

                if comp.name in PD:   # CGPU
                        # create fvOptions script
                    fileName = os.path.join(sourcePath, 'fvOptionsC')
                    with open(fileName, 'r') as file:
                        data = file.read()
                        data = data.replace('name', regionName)

                    fileName = os.path.join(desPath, 'fvOptions')
                    with open(fileName, 'w') as file: 
                        file.write(data)
                        file.close()

                else:
                        # create fvOptions script
                    fileName = os.path.join(sourcePath, 'fvOptions')
                    with open(fileName, 'r') as file:
                        data = file.read()
                        data = data.replace('name', regionName)

                    fileName = os.path.join(desPath, 'fvOptions')
                    with open(fileName, 'w') as file: 
                        file.write(data)
                        file.close()

    elif folder == 'constant':
        thermo = {'copper': {'mg': 63.546, 'cp': 390, 'kappa': 401, 'rho': 8940}, 'Al': {'mg': 26.98, 'cp': 910, 'kappa': 205, 'rho': 2712},
        'Si': {'mg': 28.09, 'cp': 705, 'kappa': 148, 'rho': 2330}, 'SiC': {'mg': 40.096, 'cp': 750, 'kappa': 120, 'rho': 3100},
        'FR4': {'mg': 72, 'cp': 1800, 'kappa': 0.13, 'rho': 1250}}  # 'SiC': {'mg': 40.096, 'cp': 508, 'kappa': 490, 'rho': 3217}
        
        for comp in server:
            if comp.name != 'Air':
                regionName = comp.name.lower()
                desPath = os.path.join(path, 'constant/', regionName)
                if os.path.exists(desPath):
                    shutil.rmtree(desPath, ignore_errors= True)

                os.makedirs(desPath, exist_ok= True)

                # create radiationProperties script
                fileName = os.path.join(sourcePath, 'radiationProperties')
                with open(fileName, 'r') as file:
                    data = file.read()
                    data = data.replace('name', regionName)

                fileName = os.path.join(desPath, 'radiationProperties')
                with open(fileName, 'w') as file: 
                    file.write(data)
                    file.close()

                # create turbulenceProperties script
                fileName = os.path.join(sourcePath, 'turbulenceProperties')
                with open(fileName, 'r') as file:
                    data = file.read()
                    data = data.replace('name', regionName)

                fileName = os.path.join(desPath, 'turbulenceProperties')
                with open(fileName, 'w') as file: 
                    file.write(data)
                    file.close()
                
                #if comp.name in PD:
                        # create thermophysicalProperties script
                fileName = os.path.join(sourcePath, 'thermophysicalProperties')
                with open(fileName, 'r') as file:
                    data = file.read()
                    data = data.replace('name', regionName)
                    data = data.replace('mg', str(thermo[comp.material_name]['mg']))
                    data = data.replace('capacity', str(thermo[comp.material_name]['cp']))
                    data = data.replace('conductivity', str(thermo[comp.material_name]['kappa']))
                    data = data.replace('density', str(thermo[comp.material_name]['rho']))
                        
                fileName = os.path.join(desPath, 'thermophysicalProperties')
                with open(fileName, 'w') as file: 
                    file.write(data)
                    file.close()
                     
    elif folder == 'zero':
        i = 0
        j = 0
        for comp in server:
            regionName = comp.name.lower()
            desPath = os.path.join(path, '0/', regionName)
            if os.path.exists(desPath):
                shutil.rmtree(desPath, ignore_errors= True)

            os.makedirs(desPath, exist_ok= True)

            if comp.name == 'Air':
                alphat(server, desPath)
                epsilon(server, desPath)
                k(server, desPath)
                nut(server, desPath)
                p(server, desPath)
                p_rgh(server, desPath)
                T(server, desPath)
                U(server, desPath)

            elif comp.name in CGPU:
                    
                HS = HS
                hs = HS[i].lower()
                    # create p script
                fileName = os.path.join(sourcePath, 'pC')
                with open(fileName, 'r') as file:
                    data = file.read()
                    data = data.replace('name', regionName)
                    data = data.replace('face', hs)

                fileName = os.path.join(desPath, 'p')
                with open(fileName, 'w') as file: 
                    file.write(data)
                    file.close()

                # create T script
                fileName = os.path.join(sourcePath, 'TC')
                with open(fileName, 'r') as file:
                    data = file.read()
                    data = data.replace('name', regionName)
                    data = data.replace('face',hs)

                fileName = os.path.join(desPath, 'T')
                with open(fileName, 'w') as file: 
                    file.write(data)
                    file.close()
                i+=1

            elif comp.name in HS:
                #CG = ['CPU1', 'GPU1']
                cg = CGPU[j].lower()
                    # create p script
                fileName = os.path.join(sourcePath, 'pH')
                with open(fileName, 'r') as file:
                    data = file.read()
                    data = data.replace('name', regionName)
                    data = data.replace('face', cg)

                fileName = os.path.join(desPath, 'p')
                with open(fileName, 'w') as file: 
                    file.write(data)
                    file.close()

                # create T script
                fileName = os.path.join(sourcePath, 'TH')
                with open(fileName, 'r') as file:
                    data = file.read()
                    data = data.replace('name', regionName)
                    data = data.replace('face',cg)

                fileName = os.path.join(desPath, 'T')
                with open(fileName, 'w') as file: 
                    file.write(data)
                    file.close()
                j+=1
                
            else:
                cg = 'pcb'
                    # create p script
                fileName = os.path.join(sourcePath, 'pH')
                with open(fileName, 'r') as file:
                    data = file.read()
                    data = data.replace('name', regionName)
                    data = data.replace('face', cg)

                fileName = os.path.join(desPath, 'p')
                with open(fileName, 'w') as file: 
                    file.write(data)
                    file.close()

                # create T script
                fileName = os.path.join(sourcePath, 'TH')
                with open(fileName, 'r') as file:
                    data = file.read()
                    data = data.replace('name', regionName)
                    data = data.replace('face',cg)

                fileName = os.path.join(desPath, 'T')
                with open(fileName, 'w') as file: 
                    file.write(data)
                    file.close()
            
def regionProperties(server, path):
    regions = []
    for comp in server:
        if comp.name != 'Air':
            regions.append(comp.name.lower())
    regions = ' '.join(regions) 

    header = """FoamFile
{
	version	2.0;
	format	ascii;
	class	dictionary;
	location	"constant";
	object	regionProperties;
}"""
    fileName = os.path.join(sourcePath, 'regionProperties')
    with open(fileName, "w") as file:
            file.write(header)
            file.close()
    tail = """
regions	(
	fluid	(air)
	solid	({regions})
);""".format(regions=regions)
    
    with open(fileName, "a") as file:
            file.write(tail)
            file.close()
    
    
    
    with open(fileName, 'r') as file:
         data = file.read()
    
    filePath = os.path.join(path, 'constant/')
    fileNmae = filePath + 'regionProperties' 
    with open(fileNmae, 'w') as file: 
        file.write(data)
        file.close()
 
def alphat(server, path):
        
    header = """
FoamFile
{
    version     2.0;
    format      binary;
    arch        "LSB;label=32;scalar=64";
    class       volScalarField;
    location    "0/air";
    object      alphat;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [ 1 -1 -1 0 0 0 0 ];

internalField   uniform 0;

boundaryField
{
    """
    fileName = os.path.join(sourcePath, 'alphat')
    with open(fileName, "w") as file:
        file.write(header)
        file.close()
                            
    for comp in server:
        if comp.name == 'Air':
            regionName = comp.name
            airComp = """air_{regionName}""".format(regionName=regionName)
        else:
            regionName = comp.name.lower()
            airComp = """air_to_{regionName}""".format(regionName=regionName)     

        with open(fileName, "a") as file:
            file.write(airComp)
            file.close()

        value = """
    {
        type            compressible::alphatJayatillekeWallFunction;
        value           uniform 0;
        Prt             0.85;
    }
    """                  
        with open(fileName, "a") as file:
            file.write(value)
            file.close()

        if comp.name[0:2] == 'HS':
            regionName = comp.name

            airComp = """air_{regionName}""".format(regionName=regionName)     

            with open(fileName, "a") as file:
                file.write(airComp)
                file.close()

            value = """
    {
        type            compressible::alphatJayatillekeWallFunction;
        value           uniform 0;
        Prt             0.85;
    }
    """         
                
            with open(fileName, "a") as file:
                file.write(value)
                file.close()

    airIO = """air_Air_inlet
    {
        type            calculated;
        value           uniform 0;
    }
    air_Air_outlet
    {
        type            calculated;
        value           uniform 0;
    }"""
                 
    with open(fileName, "a") as file:
                file.write(airIO)
                file.write('\n}')
                file.close()

    with open(fileName, 'r') as file:
         data = file.read()

    fileName = os.path.join(path, 'alphat')
    with open(fileName, 'w') as file: 
        file.write(data)
        file.close()
               
def epsilon(server, path):
        
    header = """
FoamFile
{
    version     2.0;
    format      binary;
    arch        "LSB;label=32;scalar=64";
    class       volScalarField;
    location    "0/air";
    object      epsilon;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [ 0 2 -3 0 0 0 0 ];

internalField   uniform 1;

boundaryField
{
    """
    fileName = os.path.join(sourcePath, 'epsilon')
    with open(fileName, "w") as file:
        file.write(header)
        file.close()
                            
    for comp in server:
        if comp.name == 'Air':
            regionName = comp.name
            airComp = """air_{regionName}""".format(regionName=regionName)
        else:
            regionName = comp.name.lower()
            airComp = """air_to_{regionName}""".format(regionName=regionName)     

        with open(fileName, "a") as file:
            file.write(airComp)
            file.close()

        value = """
    {
        type            epsilonWallFunction;
        value           uniform 1;
    }
    """                  
        with open(fileName, "a") as file:
            file.write(value)
            file.close()

        if comp.name[0:2] == 'HS':
            regionName = comp.name

            airComp = """air_{regionName}""".format(regionName=regionName)     

            with open(fileName, "a") as file:
                file.write(airComp)
                file.close()

            value = """
    {
        type            epsilonWallFunction;
        value           uniform 1;
    }
    """         
                
            with open(fileName, "a") as file:
                file.write(value)
                file.close()

    airIO = """air_Air_inlet
    {
        type            turbulentMixingLengthDissipationRateInlet;
        value           uniform 1;
        mixingLength    0.001;
    }
    air_Air_outlet
    {
        type            zeroGradient;
    }"""
                 
    with open(fileName, "a") as file:
                file.write(airIO)
                file.write('\n}')
                file.close() 

    with open(fileName, 'r') as file:
         data = file.read()

    fileName = os.path.join(path, 'epsilon')
    with open(fileName, 'w') as file: 
        file.write(data)
        file.close()             
               
def k(server, path):
        
    header = """
FoamFile
{
    version     2.0;
    format      binary;
    arch        "LSB;label=32;scalar=64";
    class       volScalarField;
    location    "0/air";
    object      k;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [ 0 2 -2 0 0 0 0 ];

internalField   uniform 0.01;

boundaryField
{
    """
    fileName = os.path.join(sourcePath, 'k')
    with open(fileName, "w") as file:
        file.write(header)
        file.close()
                            
    for comp in server:
        if comp.name == 'Air':
            regionName = comp.name
            airComp = """air_{regionName}""".format(regionName=regionName)
        else:
            regionName = comp.name.lower()
            airComp = """air_to_{regionName}""".format(regionName=regionName)     

        with open(fileName, "a") as file:
            file.write(airComp)
            file.close()

        value = """
    {
        type            kqRWallFunction;
        value           uniform 0.01;
    }
    """                  
        with open(fileName, "a") as file:
            file.write(value)
            file.close()

        if comp.name[0:2] == 'HS':
            regionName = comp.name

            airComp = """air_{regionName}""".format(regionName=regionName)     

            with open(fileName, "a") as file:
                file.write(airComp)
                file.close()

            value = """
    {
        type            kqRWallFunction;
        value           uniform 0.01;
    }
    """         
                
            with open(fileName, "a") as file:
                file.write(value)
                file.close()

    airIO = """air_Air_inlet
    {
        type            turbulentIntensityKineticEnergyInlet;
        value           uniform 0.01;
        intensity       0.05;
    }
    air_Air_outlet
    {
        type            zeroGradient;
    }"""
                 
    with open(fileName, "a") as file:
                file.write(airIO)
                file.write('\n}')
                file.close() 

    with open(fileName, 'r') as file:
         data = file.read()

    fileName = os.path.join(path, 'k')
    with open(fileName, 'w') as file: 
        file.write(data)
        file.close()              

def nut(server, path):
        
    header = """
FoamFile
{
    version     2.0;
    format      binary;
    arch        "LSB;label=32;scalar=64";
    class       volScalarField;
    location    "0/air";
    object      nut;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [ 0 2 -1 0 0 0 0 ];

internalField   uniform 0.11;

boundaryField
{
    """
    fileName = os.path.join(sourcePath, 'nut')
    with open(fileName, "w") as file:
        file.write(header)
        file.close()
                            
    for comp in server:
        if comp.name == 'Air':
            regionName = comp.name
            airComp = """air_{regionName}""".format(regionName=regionName)
        else:
            regionName = comp.name.lower()
            airComp = """air_to_{regionName}""".format(regionName=regionName)     

        with open(fileName, "a") as file:
            file.write(airComp)
            file.close()

        value = """
    {
        type            nutUWallFunction;
        value           uniform 0.11;
    }
    """                  
        with open(fileName, "a") as file:
            file.write(value)
            file.close()

        if comp.name[0:2] == 'HS':
            regionName = comp.name

            airComp = """air_{regionName}""".format(regionName=regionName)     

            with open(fileName, "a") as file:
                file.write(airComp)
                file.close()

            value = """
    {
        type            nutUWallFunction;
        value           uniform 0.11;
    }
    """         
                
            with open(fileName, "a") as file:
                file.write(value)
                file.close()

    airIO = """air_Air_inlet
    {
        type            calculated;
        value           uniform 0.11;
    }
    air_Air_outlet
    {
        type            calculated;
        value           uniform 0.11;
    }"""
                 
    with open(fileName, "a") as file:
                file.write(airIO)
                file.write('\n}')
                file.close()  

    with open(fileName, 'r') as file:
         data = file.read()

    fileName = os.path.join(path, 'nut')
    with open(fileName, 'w') as file: 
        file.write(data)
        file.close()             

def p(server, path):
        
    header = """
FoamFile
{
    version     2.0;
    format      binary;
    arch        "LSB;label=32;scalar=64";
    class       volScalarField;
    location    "0/air";
    object      p;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [ 1 -1 -2 0 0 0 0 ];

internalField   uniform 100000;

boundaryField
{
    """
    fileName = os.path.join(sourcePath, 'p')
    with open(fileName, "w") as file:
        file.write(header)
        file.close()
                            
    for comp in server:
        if comp.name == 'Air':
            regionName = comp.name
            airComp = """air_{regionName}""".format(regionName=regionName)
        else:
            regionName = comp.name.lower()
            airComp = """air_to_{regionName}""".format(regionName=regionName)     

        with open(fileName, "a") as file:
            file.write(airComp)
            file.close()

        value = """
    {
        type            calculated;
        value           uniform 100000;
    }
    """                  
        with open(fileName, "a") as file:
            file.write(value)
            file.close()

        if comp.name[0:2] == 'HS':
            regionName = comp.name

            airComp = """air_{regionName}""".format(regionName=regionName)     

            with open(fileName, "a") as file:
                file.write(airComp)
                file.close()

            value = """
    {
        type            calculated;
        value           uniform 100000;
    }
    """         
                
            with open(fileName, "a") as file:
                file.write(value)
                file.close()

    airIO = """air_Air_inlet
    {
        type            calculated;
        value           uniform 100000;
    }
    air_Air_outlet
    {
        type            calculated;
        value           uniform 100000;
    }"""
                 
    with open(fileName, "a") as file:
                file.write(airIO)
                file.write('\n}')
                file.close()  

    with open(fileName, 'r') as file:
         data = file.read()

    fileName = os.path.join(path, 'p')
    with open(fileName, 'w') as file: 
        file.write(data)
        file.close()             

def p_rgh(server, path):
        
    header = """
FoamFile
{
    version     2.0;
    format      binary;
    arch        "LSB;label=32;scalar=64";
    class       volScalarField;
    location    "0/air";
    object      p_rgh;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [ 1 -1 -2 0 0 0 0 ];

internalField   uniform 100000;

boundaryField
{
    """
    fileName = os.path.join(sourcePath, 'p_rgh')
    with open(fileName, "w") as file:
        file.write(header)
        file.close()
                            
    for comp in server:
        if comp.name == 'Air':
            regionName = comp.name
            airComp = """air_{regionName}""".format(regionName=regionName)
        else:
            regionName = comp.name.lower()
            airComp = """air_to_{regionName}""".format(regionName=regionName)     

        with open(fileName, "a") as file:
            file.write(airComp)
            file.close()

        value = """
    {
        type            fixedFluxPressure;
    }
    """                  
        with open(fileName, "a") as file:
            file.write(value)
            file.close()

        if comp.name[0:2] == 'HS':
            regionName = comp.name

            airComp = """air_{regionName}""".format(regionName=regionName)     

            with open(fileName, "a") as file:
                file.write(airComp)
                file.close()

            value = """
    {
        type            fixedFluxPressure;
    }
    """         
                
            with open(fileName, "a") as file:
                file.write(value)
                file.close()

    airIO = """air_Air_inlet
    {
        type            fixedFluxPressure;
    }
    air_Air_outlet
    {
        type            fixedValue;
        value           uniform 100000;
    }"""
                 
    with open(fileName, "a") as file:
                file.write(airIO)
                file.write('\n}')
                file.close()  

    with open(fileName, 'r') as file:
         data = file.read()

    fileName = os.path.join(path, 'p_rgh')
    with open(fileName, 'w') as file: 
        file.write(data)
        file.close()             

def T(server, path):
        
    header = """
FoamFile
{
    version     2.0;
    format      binary;
    arch        "LSB;label=32;scalar=64";
    class       volScalarField;
    location    "0/air";
    object      T;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#include "./inputs"
dimensions      [ 0 0 0 1 0 0 0 ];

internalField   uniform $tInlet;

boundaryField
{
    """
    fileName = os.path.join(sourcePath, 'T')
    with open(fileName, "w") as file:
        file.write(header)
        file.close()
                            
    for comp in server:
        if comp.name == 'Air':
            regionName = comp.name
            airComp = """air_{regionName}""".format(regionName=regionName)     

            with open(fileName, "a") as file:
                file.write(airComp)
                file.close()

            value = """
    {
        type            zeroGradient;
    }
    """                  
            with open(fileName, "a") as file:
                file.write(value)
                file.close()
            
        else:
            regionName = comp.name.lower()
            airComp = """air_to_{regionName}""".format(regionName=regionName) 
            with open(fileName, "a") as file:
                file.write(airComp)
                file.close()

            value = """
    {
        type            compressible::turbulentTemperatureCoupledBaffleMixed;
        value           uniform $tInlet;
        kappaMethod     fluidThermo;
        kappa           none;
        neighbourFieldName T;
        Tnbr            T;
        thicknessLayers ( );
        kappaLayers     ( );
    }
    """                  
            with open(fileName, "a") as file:
                file.write(value)
                file.close()
        

        if comp.name[0:2] == 'HS':
            regionName = comp.name

            airComp = """air_{regionName}""".format(regionName=regionName)     

            with open(fileName, "a") as file:
                file.write(airComp)
                file.close()

            value = """
    {
        type            zeroGradient;
    }
    """         
                
            with open(fileName, "a") as file:
                file.write(value)
                file.close()

    airIO = """air_Air_inlet
    {
        type            totalTemperature;
        T0              uniform $tInlet;
        gamma           1.396;
    }
    air_Air_outlet
    {
        type            inletOutlet;
        inletValue      uniform $tInlet;
    }"""
                 
    with open(fileName, "a") as file:
                file.write(airIO)
                file.write('\n}')
                file.close() 

    with open(fileName, 'r') as file:
         data = file.read()

    fileName = os.path.join(path, 'T')
    with open(fileName, 'w') as file: 
        file.write(data)
        file.close()   

def U(server, path):
        
    header = """
FoamFile
{
    version     2.0;
    format      binary;
    arch        "LSB;label=32;scalar=64";
    class       volVectorField;
    location    "0/air";
    object      U;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#include "./inputs"
dimensions      [ 0 1 -1 0 0 0 0 ];

internalField   uniform ( 0 0 0 );

boundaryField
{
    """
    fileName = os.path.join(sourcePath, 'U')
    with open(fileName, "w") as file:
        file.write(header)
        file.close()
                            
    for comp in server:
        if comp.name == 'Air':
            regionName = comp.name
            airComp = """air_{regionName}""".format(regionName=regionName)  
        else:
            regionName = comp.name.lower()
            airComp = """air_to_{regionName}""".format(regionName=regionName)     

        with open(fileName, "a") as file:
            file.write(airComp)
            file.close()

        value = """
    {
        type            noSlip;
    }
    """                  
        with open(fileName, "a") as file:
            file.write(value)
            file.close()

        if comp.name[0:2] == 'HS':
            regionName = comp.name

            airComp = """air_{regionName}""".format(regionName=regionName)     

            with open(fileName, "a") as file:
                file.write(airComp)
                file.close()

            value = """
    {
        type            noSlip;
    }
    """         
                
            with open(fileName, "a") as file:
                file.write(value)
                file.close()

    airIO = """air_Air_inlet
    {
        type            surfaceNormalFixedValue;
        refValue        uniform - $u;
    }
    air_Air_outlet
    {
        type            pressureInletOutletVelocity;
        value           uniform ( 0 0 0 );
    }"""
                 
    with open(fileName, "a") as file:
                file.write(airIO)
                file.write('\n}')
                file.close() 

    with open(fileName, 'r') as file:
         data = file.read()

    fileName = os.path.join(path, 'U')
    with open(fileName, 'w') as file: 
        file.write(data)
        file.close()                    

def TP(server, path):
        
    header = """
FoamFile
{
    version     2.0;
    format      binary;
    arch        "LSB;label=32;scalar=64";
    class       volScalarField;
    location    "0/pcb";
    object      T;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#include "./inputs"
dimensions	[0 0 0 1 0 0 0];
internalField	uniform $tInlet;
boundaryField
{
    """
    fileName = os.path.join(sourcePath, 'TP')
    with open(fileName, "w") as file:
        file.write(header)
        file.close()
                            
    for comp in server:
        if comp.name[0:2] != 'HS':
            if comp.name != 'PCB':
                regionName = comp.name.lower()
                airComp = """pcb_to_{regionName}""".format(regionName=regionName)     

                with open(fileName, "a") as file:
                    file.write(airComp)
                    file.close()
                if comp.name == 'Air':
                    value = """
    {
		type	compressible::turbulentTemperatureCoupledBaffleMixed;
		value	uniform $tInlet;
		kappaMethod	solidThermo;
		kappa	none;
		neighbourFieldName	T;
		Tnbr	T;
	}
    """                  
                else:
                    value = """
    {
		type	compressible::turbulentTemperatureCoupledBaffleMixed;
		value	uniform $tInlet;
		kappaMethod	solidThermo;
		kappa	none;
		neighbourFieldName	T;
		Tnbr	T;
		thicknessLayers	();
		kappaLayers	();
	}
    """
            
           
                with open(fileName, "a") as file:
                    file.write(value)
                    file.close()
        
    with open(fileName, "a") as file:
        file.write('\n}')
        file.close()

    desPath = os.path.join(path, '0/', 'pcb')
    # create T script
    with open(fileName, 'r') as file:
        data = file.read()

    fileName = os.path.join(desPath, 'T')
    with open(fileName, 'w') as file: 
        file.write(data)
        file.close()

def pP(server, path):
        
    header = """
FoamFile
{
    version     2.0;
    format      binary;
    arch        "LSB;label=32;scalar=64";
    class       volScalarField;
    location    "0/pcb";
    object      p;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions	[1 -1 -2 0 0 0 0];
internalField	uniform 0.0;
boundaryField
{
    """
    fileName = os.path.join(sourcePath, 'pP')
    with open(fileName, "w") as file:
        file.write(header)
        file.close()
                            
    for comp in server:
        if comp.name[0:2] != 'HS':
            if comp.name != 'PCB':
                regionName = comp.name.lower()
                airComp = """pcb_to_{regionName}""".format(regionName=regionName)     

                with open(fileName, "a") as file:
                    file.write(airComp)
                    file.close()

                value = """
    {
		type	zeroGradient;
	}
    """                  
                with open(fileName, "a") as file:
                    file.write(value)
                    file.close()
        
    with open(fileName, "a") as file:
        file.write('\n}')
        file.close()

    desPath = os.path.join(path, '0/', 'pcb')
    # create T script
    with open(fileName, 'r') as file:
        data = file.read()

    fileName = os.path.join(desPath, 'p')
    with open(fileName, 'w') as file: 
        file.write(data)
        file.close()
        
def BCs(server, boundryConditions, desPath):    # inputs script
    """ 
    This function creates input scripts that uses in dictionaries.
    """
    
    CGPU, HS, PD = seperate(server)
    fileName = os.path.join(desPath, 'inputs')

    ambientTemp = boundryConditions[0]['ambient_temperature']
    velocity = int(boundryConditions[1]['Velocity'])
    TimThicknes = boundryConditions[1]['TIM_Thickness']
    TimKappa = int(boundryConditions[1]['TIM_Kappa'])
    nCore = int(boundryConditions[1]['Number_Core'])
    iteration = int(boundryConditions[1]['Iteration'])

    bcs = """u {velocity};
timThikness {TimThicknes};
timKappa {TimKappa};
nCore {nCore};
tInlet {ambientTemp};
endTime {iteration};
""".format(velocity=velocity, TimThicknes=TimThicknes, TimKappa=TimKappa, nCore=nCore, ambientTemp=ambientTemp, iteration=iteration)
    
    with open(fileName, "w") as file:
        file.write(bcs)
        file.close() 

    for comp in server:
        if comp.name in PD:
            regionName = comp.name.lower()
            power = """p{regionName} {power};""".format(regionName=regionName, power=float(comp.power))  

            with open(fileName, "a") as file:
                file.write(power)
                file.write('\n')
                file.close() 

def seperate(server):
    HS = []
    CGPU = []
    PD = [] # Power Devices
    for comp in server:
        if comp.name[0:2] == 'HS':
            HS.append(comp.name)
            CGPU.append(comp.h_val)
            
        #elif comp.name[1:3] == 'PU':
            #CGPU.append(comp.name)
         
        #elif comp.name in ['MOSFET', 'rectifier']:
            #CGPU.append(comp.name)
        
        if comp.name not in ['Air', 'PCB'] and comp.name[0:2] != 'HS':
            PD.append(comp.name)
    #print(PD)        
    return CGPU, HS, PD
    
def solutionExport(sourcePath, desPath, boundryConditions, designInfo, server):
    """ 
    This function exports openFoam results as a json file for post processing.
    """
    
    CGPU, HS, PD = seperate(server)
    #print(boundryConditions[2])
    for file in os.listdir(sourcePath):
        if file  in ['constant', 'postProcessing', str(int(boundryConditions[1]['Iteration']))]:
            targetFolder = os.path.join(desPath, 'Solutions','Initial_Layout', 'Layout0', file)
            shutil.copytree(file, targetFolder, dirs_exist_ok= True)
    fileName = os.path.join(desPath, 'Solutions', 'Initial_Layout', 'Layout0', 'case.foam')
    open(fileName, 'a').close()
    
    path = os.path.join(desPath, 'Solutions', 'Initial_Layout', 'Layout0')
    latestTime = str(int(boundryConditions[1]['Iteration']))
    regions = os.listdir(os.path.join(path, latestTime))

    air = {}
    results = {}
    maxTemp = {}
    minTemp = {}
    X = {}
    Y = {}
    Z = {}
    T = {}
    i = 0
    for region in regions:
        if region == 'air': 
            x, y, z = ff.readmesh(path, region=region, structured=False, verbose=False)
            air['Coord'] = [x.tolist(), y.tolist(), z.tolist()]
            air['T'] =  ff.readscalar(path, time_name = latestTime, region=region, name='T', verbose=False).tolist()
            air['U'] = ff.readvector(path, time_name = latestTime, region=region, name='U', verbose=False).tolist()
            air['p'] = ff.readscalar(path, time_name = latestTime, region=region, name='p', verbose=False).tolist()
            results[region] = air
            
        elif region == 'uniform':
            pass
        
        else:
            x, y, z = ff.readmesh(path, region=region, structured=False, verbose=False)
            temp = ff.readscalar(path, time_name = latestTime, region=region, name='T', verbose=False)
            maxTemp[region] = max(temp)
            minTemp[region] = min(temp)
            locals()[region] = {'Coord': [x.tolist(), y.tolist(), z.tolist()], 'T': temp.tolist()}
            results[region] = locals()[region]

            if i == 0:
                X_total = x
                Y_total = y
                Z_total = z
                T_total = temp     
            else:
                X_total = np.concatenate((X_total, x))
                Y_total = np.concatenate((Y_total, y))
                Z_total = np.concatenate((Z_total, z))
                T_total = np.concatenate((T_total, temp))
            i+=1 
            X[region] = x
            Y[region] = y
            Z[region] = z
            T[region] = temp

    with open(os.path.join(desPath, 'Solutions', 'Initial_Layout', 'Layout0', 'results.json'), 'w') as f:
        json.dump(results, f)
    
    # Reliabilty Calculation
    if boundryConditions[3] == 1:   # Mode1
        k = 8.63*10e-5
        tStress = boundryConditions[1]['Test_Temperature'] # 150 C
        
        i = 1
        with open(os.path.join(desPath, 'Solutions', 'Initial_Layout', 'Layout0', 'reliability.csv'), 'w') as file:
            file.write('ID,Component,Max_Temp(C),Acc_Factor\n')
            for key, value in maxTemp.items():
                #print(key)
                if key[0:2] != 'hs' and key != 'pcb':
                    if designInfo['designType'] == 'Converter':
                        if key[0] == 'r':
                            Ea = boundryConditions[2][key]
                        elif key =='mosfet':
                            Ea = boundryConditions[2][key.upper()]
                        else:
                            Ea = boundryConditions[2][key.capitalize()]
                    else: 
                        Ea = boundryConditions[2][key.upper()]
                    AF = np.exp((Ea/k)*((1/value) - (1/tStress)))
                    #.write(f'Acceleration Factor For {key} is {round(AF, ndigits=3)} and maximum temperature is {round(value - 273.15, ndigits=3)} C.\n')
                    file.write(f'{i},{key},{round(value - 273.15, ndigits=3)},{round(AF, ndigits=3)}\n')
                    i+=1
            file.close()
    elif boundryConditions[3] == 0: # Mode0
        i = 1
        with open(os.path.join(desPath, 'Solutions', 'Initial_Layout', 'Layout0', 'reliability.csv'), 'w') as file:
            file.write('ID,Component,Max_Temp(C),Acc_Factor\n')
            for key, value in maxTemp.items():
                #print(key)
                if key[0:2] != 'hs' and key != 'pcb':         
                    file.write(f'{i},{key},{round(value - 273.15, ndigits=3)}\n')
                    i+=1
            file.close()
    else:   # Mode2
        i = 1
        with open(os.path.join(desPath, 'Solutions', 'Initial_Layout', 'Layout0', 'reliability.csv'), 'w') as file:
            file.write('ID,Component,Max_Temp(C),Acc_Factor\n')
            for key, value in maxTemp.items():
                #print(key)
                if key[0:2] != 'hs' and key != 'pcb':         
                    file.write(f'{i},{key},{round(value - 273.15, ndigits=3)}\n')
                    i+=1
            file.close()