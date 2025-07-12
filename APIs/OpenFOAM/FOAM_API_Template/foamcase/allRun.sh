#!/bin/bash
#cd "${0%/*}" || exit                                # Run from this directory

# Detect OpenFOAM.com install
OpenFOAM_COM_DIR=$(ls -1d /usr/lib/openfoam/openfoam???? 2> /dev/null | tail -1)
: "${WM_PROJECT_DIR:=${OpenFOAM_COM_DIR}}"

# Load the environment if not already loaded
source "${WM_PROJECT_DIR}/etc/bashrc"
source "${WM_PROJECT_DIR}/bin/tools/RunFunctions"       

# Run OpenFOAM Applications
runApplication surfaceFeatureExtract
runApplication blockMesh -noFunctionObjects
runApplication decomposePar
runParallel snappyHexMesh -overwrite
runApplication reconstructParMesh -constant
mv -v log.decomposePar log.decomposePar.old
mv -v log.reconstructParMesh log.reconstructParMesh.old
#runApplication snappyHexMesh -overwrite
runApplication createPatch -overwrite
runApplication splitMeshRegions -overwrite -prefixRegion -cellZones

runApplication decomposePar -noFunctionObjects -force -latestTime -allRegions
# Run OpenFOAM
runParallel $(getApplication)
runApplication reconstructPar -noFunctionObjects -newTimes -allRegions