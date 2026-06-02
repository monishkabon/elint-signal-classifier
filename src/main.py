import os 
import pandas as pd
import numpy as np

from deinterleaver import masterSdiff
from wvdClassifier import classifyTrack

def pipeline(dataPath):
    df = pd.read_csv(dataPath)
    df['allocated'] = False
    
    targetPris = [250, 850, 1000, 3000]
    tolerance = 10.0
    trackCounter = 1 
    
    for targetPri in targetPris:
        while True:
            unallocated = df[df['allocated'] == False]
            if unallocated.empty:
                break
                
            indices = unallocated.index.values
            toas = unallocated['ToA'].values
            foundTrackIndices = []
            
            for startIdx in range(len(toas)):
                currentIdx = startIdx
                currentChain = [indices[currentIdx]]
                
                while True:
                    expectedToA = toas[currentIdx] + targetPri
                    
                    
                    insertPos = np.searchsorted(toas, expectedToA - tolerance, side='left')
                    
                    matchFound = False
                    for j in range(insertPos, min(insertPos + 20, len(toas))):
                        if j <= currentIdx:
                            continue
                        if abs(toas[j] - expectedToA) <= tolerance:
                            currentChain.append(indices[j])
                            currentIdx = j
                            matchFound = True
                            break
                        if toas[j] > expectedToA + tolerance:
                            break
                    
                    if not matchFound:
                        break
                
                if len(currentChain) >= 50:
                    foundTrackIndices = currentChain
                    break
            
            if not foundTrackIndices:
                break
                
            trackDf = df.loc[foundTrackIndices]
            trackPulses = trackDf[['ToA', 'RF', 'PW']].to_dict('records')
            
            df.loc[foundTrackIndices, 'allocated'] = True
            
            classifyTrack(trackPulses, trackName=f"Extracted Track #{trackCounter} (Size: {len(trackPulses)})")
            trackCounter += 1

if __name__ == "__main__":
    dataPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/interleaved_signals_40k.csv")
    pipeline(dataPath)