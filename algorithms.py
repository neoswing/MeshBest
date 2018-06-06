#!/usr/bin/env python

import numpy
import sys
import os
import json
import time
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt




from meshbest.methods import dvanalysis, scoring, ellipticfit, sizecorr, plotting

try:
    from workflow_lib import workflow_logging
    logger = workflow_logging.getLogger()
except:
    import logging
    logger = logging.getLogger("MeshBest")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)

# numpy.set_printoptions(threshold='nan')

start_time = time.time()





def classic(jsonFilePath, resultsPath=None):
    
    if resultsPath!=None:
        os.chdir(resultsPath)
    
    difminpar = 0.2
    
    logger.debug('Checkpoint0: Start - {0}s'.format('%0.3f') % (time.time() - start_time))

    json_file = open(jsonFilePath, 'r')
    jsondata = json.load(json_file)
    json_file.close()
    
    row, col = jsondata['grid_info']['steps_y'], jsondata['grid_info']['steps_x']
    Dtable = numpy.zeros((row, col))

    for item in jsondata['meshPositions']:
        i = item['indexY']
        j = item['indexZ']
        Dtable[j, i] = item['dozor_score']
    
    
    jsondata['MeshBest'] = {'type': 'classic'}
    jsondata['MeshBest']['Dtable'] = Dtable
    numpy.savetxt('Dtable.txt', Dtable, fmt='%0.2f')
    plt.imshow(Dtable, cmap='hot', interpolation='nearest', origin='upper', extent=[0.5, (col + 0.5), (row + 0.5), 0.5])
    plt.colorbar()
    plt.savefig('Dtable.png', dpi=300, transparent=True, bbox_inches='tight')  # , pad_inches=0)
    plt.close()
    

    jsondata['MeshBest']['difminpar'] = difminpar
    Ztable = numpy.zeros((row, col))
    Ztable[Dtable<difminpar] = -1
    
    jsondata['MeshBest']['Ztable'] = Ztable
    logger.debug('Checkpoint1: Initial data acquired - {0}s'.format('%0.3f') % (time.time() - start_time))
    
    dvanalysis.EliminateSaltRings(jsondata)
    logger.debug('Checkpoint2: SaltRing Analysis - {0}s'.format('%0.3f') % (time.time() - start_time))

    dvanalysis.DetermineMCdiffraction(jsondata)
    logger.debug('Checkpoint3: DV Analysis - {0}s'.format('%0.3f') % (time.time() - start_time))

    scoring.PerformCrystalRecognition(jsondata)
    logger.debug('Checkpoint4: Crystal recognition - {0}s'.format('%0.3f') % (time.time() - start_time))
    
    if numpy.all(Ztable < 0):
        logger.debug('MeshBest terminated with no valuable signal detected')
        numpy.savetxt('Result_BestPositions.txt', [])
        
        jsondata['MeshBest']['Dtable'] = base64.b64encode(jsondata['MeshBest']['Dtable'])
        jsondata['MeshBest']['Ztable'] = base64.b64encode(jsondata['MeshBest']['Ztable'])
        
        jsondata['MeshBest']['BestPositions'] = base64.b64encode(numpy.empty())

    else:
        if numpy.size(numpy.unique(Ztable))<=4:
            ellipticfit.DoEllipseFit(jsondata)
        else:
            sizecorr.GetAllPositions(jsondata)
        
        logger.debug('Checkpoint5: Shape Fit {0}s'.format('%0.3f') % (time.time() - start_time))

        jsondata['MeshBest']['Dtable'] = base64.b64encode(jsondata['MeshBest']['Dtable'])
        jsondata['MeshBest']['Ztable'] = base64.b64encode(jsondata['MeshBest']['Ztable'])

        
        fig = plt.figure()
        ax = fig.add_subplot(111)
        
        plotting.MainPlot(jsondata, ax)
        plt.savefig('CrystalMesh.png', dpi=150, transparent=True, bbox_inches='tight')  # , pad_inches=0)
        
    with open('MeshResults.json', 'w') as outfile:
        json.dump(jsondata, outfile, sort_keys=True, indent=4, ensure_ascii=False)
    logger.debug('Checkpoint6: Finish {0}s'.format('%0.3f') % (time.time() - start_time))
    
    return jsondata



def hamburg(jsonFilePath, process_data=False, resultsPath=None):
    
    if resultsPath!=None:
        os.chdir(resultsPath)
    
    difminpar = 0.2
    
    logger.debug('Checkpoint0: Start - {0}s'.format('%0.3f') % (time.time() - start_time))

    json_file = open(jsonFilePath, 'r')
    jsondata = json.load(json_file)
    json_file.close()
    
    row, col = jsondata['grid_info']['steps_y'], jsondata['grid_info']['steps_x']
    Dtable = numpy.zeros((row, col))

    for item in jsondata['meshPositions']:
        i = item['indexY']
        j = item['indexZ']
        Dtable[j, i] = item['dozor_score']
        
    jsondata['MeshBest'] = {'type': 'hamburg'}
    jsondata['MeshBest']['Dtable'] = Dtable

    plt.imshow(Dtable, cmap='hot', interpolation='nearest', origin='upper', extent=[0.5, (col + 0.5), (row + 0.5), 0.5])
    plt.colorbar()
    plt.savefig('Dtable.png', dpi=300, transparent=True, bbox_inches='tight')  # , pad_inches=0)
    plt.close()
    
    jsondata['MeshBest']['difminpar'] = difminpar
    Ztable = numpy.zeros((row, col))
    Ztable[Dtable<difminpar] = -1
    
    jsondata['MeshBest']['Ztable'] = Ztable
    logger.debug('Checkpoint1: Initial data acquired - {0}s'.format('%0.3f') % (time.time() - start_time))
    
    dvanalysis.EliminateSaltRings(jsondata)
    logger.debug('Checkpoint2: SaltRing Analysis - {0}s'.format('%0.3f') % (time.time() - start_time))

    dvanalysis.DetermineMCdiffraction(jsondata)
    logger.debug('Checkpoint3: DV Analysis - {0}s'.format('%0.3f') % (time.time() - start_time))

    scoring.PerformCrystalRecognition(jsondata)
    logger.debug('Checkpoint4: Crystal recognition - {0}s'.format('%0.3f') % (time.time() - start_time))

    jsondata['MeshBest']['Dtable'] = base64.b64encode(jsondata['MeshBest']['Dtable'])
    jsondata['MeshBest']['Ztable'] = base64.b64encode(jsondata['MeshBest']['Ztable'])

    if numpy.all(Ztable < 0):
        logger.debug('MeshBest terminated with no valuable signal detected')
        with open('MeshResults.json', 'w') as outfile:
            json.dump(jsondata, outfile, sort_keys=True, indent=4, ensure_ascii=False)

        
    else:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plotting.MainPlot(jsondata, ax, addPositions=False)
        plt.savefig('HambMesh.png', dpi=150, transparent=True, bbox_inches='tight')  # , pad_inches=0)
        plt.close()
        
        

        
        
        positionReference = numpy.empty((row, col), dtype='int')
        for i in jsondata['meshPositions']:
            positionReference[i['indexZ'], i['indexY']] = i['index']

        
        listOfEdges = []

        #Omega check
        if round(jsondata['meshPositions'][1]['omega']-jsondata['meshPositions'][0]['omega'], 2)==0:
            logger.debug('Omega is not changed during the mesh scan')
            with open('MeshResults.json', 'w') as outfile:
                json.dump(jsondata, outfile, sort_keys=True, indent=4, ensure_ascii=False)
            sys.exit()
        

        Z = 0
        first = -1
        last = -1
        for line in xrange(row):
            for element in xrange(col):
                if Ztable[line, element]==Z:
                    last = positionReference[line, element]
                else:
                    Z = 0
                    if last!=-1:
                        listOfEdges.append((first, last))
                        first = -1
                        last = -1
                    if Ztable[line, element]>0:
                        first = positionReference[line, element]
                        last = positionReference[line, element]
                        Z = Ztable[line, element]
            Z = 0
            first = -1
            last = -1
        
        
        
        with open('MeshResults.json', 'w') as outfile:
            json.dump(jsondata, outfile, sort_keys=True, indent=4, ensure_ascii=False)

        logger.debug('Checkpoint6: Finish {0}s'.format('%0.3f') % (time.time() - start_time))
        
        return listOfEdges
        



