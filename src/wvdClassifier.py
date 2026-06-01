import numpy as np 

threatLibrary = { "civilianNav" : {"PRI": 1000.0, "RF": 9.4, "PW": 0.8},
                "EarlyWarning":  {"PRI": 3000.0, "RF": 3.2,  "PW": 2.5},
                "TargetTracker": {"PRI": 250.0,  "RF": 12.5, "PW": 0.2},
                "FreqHopper":    {"PRI": 850.0,  "RF": 9.5,  "PW": 0.5}}


def classifyTrack (trackPulses , trackName = "unknown"):
    
    pris = np.diff([p['ToA'] for p in trackPulses])
    rf = np.array([p['RF'] for p in trackPulses])
    pw = np.array([p['PW'] for p in trackPulses])
    
    meanPRI = np.mean(pris) if len(pris) > 0 else 0
    meanRF = np.mean(rf) 
    meanPW = np.mean(pw)
    
    print(f"    Calculated Vector: PRI={meanPRI:.1f}µs | RF={meanRF:.2f}GHz | PW={meanPW:.2f}µs")
    
    
    rf_spread = np.max(rf) - np.min(rf)
    
    wPri = 1.0
    wRf = 100.0
    wPw = 1000.0
    
    if rf_spread > 0.4:
        wRf *= 2

        w_rf = 0.0

    bestMatch = "unknown"
    shortestDistance = float('inf')
    
    for threatName , threatVector in threatLibrary.items():
        
        dPri = wPri * (meanPRI - threatVector['PRI'])**2
        dRf = wRf * (meanRF - threatVector['RF'])**2
        dPw = wPw * (meanPW - threatVector['PW'])**2
        
        distance = np.sqrt(dPri + dRf + dPw)
        
        print(f"Distance to {threatName}: {distance:.2f}")
        
        if distance < shortestDistance:
            shortestDistance = distance
            bestMatch = threatName
            
            
        print(f"Result: {bestMatch} (Proximity Score: {shortestDistance:.2f})")
        
        return bestMatch
    

if __name__ == "__main__":
    
    mock_stable_track = [
        {"ToA": 1000.1, "RF": 9.41, "PW": 0.81},
        {"ToA": 2000.2, "RF": 9.40, "PW": 0.79},
        {"ToA": 3000.0, "RF": 9.39, "PW": 0.80},
        {"ToA": 4000.1, "RF": 9.41, "PW": 0.82}
    ]
    
    
    mock_evasive_track = [
        {"ToA": 850.5,  "RF": 9.10, "PW": 0.51},
        {"ToA": 1700.2, "RF": 9.85, "PW": 0.49},
        {"ToA": 2550.8, "RF": 9.30, "PW": 0.50},
        {"ToA": 3400.1, "RF": 9.95, "PW": 0.52}
    ]
    
    classifyTrack(mock_stable_track, "Intercept Alpha")
    classifyTrack(mock_evasive_track, "Intercept Beta")
    
    
    