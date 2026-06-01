import numpy as np
import pandas as pd 

class radarEmitter: 
    def __init__(self, classLabel , pri , rf , pw , behavior = "stable"):
        self.classLabel = classLabel
        self.pri = pri
        self.rf = rf
        self.pw = pw
        self.behavior = behavior
    
    def genaratePulses (self , duration , jitterSigma = 2.0):
        duration = duration * 1000 
        numPulses = int(duration // self.pri)
        
        idealToa = np.arange(1 , numPulses + 1) * self.pri
        
        pulses = []
        
        for i in range(numPulses):

            jitter = np.random.normal(0, jitterSigma)
            actualToa = max(0, idealToa[i] + jitter)
            
            if self.behavior == "hopper":
                actualRf = np.random.uniform(self.rf - 0.5 , self.rf + 0.5)
            else: 
                actualRf = self.rf + np.random.normal(0, 0.01)
                
            pulses.append({
                "ToA": round(actualToa, 3),
                "RF": round(actualRf, 4),
                "PW": round(self.pw + np.random.normal(0, 0.02), 2),
                "True_Label": self.classLabel  
            })
        return pulses       
    
    


if __name__ == "__main__":
        
        allPulses = []
        
        emitters = [
        radarEmitter(classLabel="Civilian_Nav", pri=1000.0, rf=9.4, pw=0.8, behavior="stable"),
        radarEmitter(classLabel="Early_Warning", pri=3000.0, rf=3.2, pw=2.5, behavior="stable"),
        radarEmitter(classLabel="Target_Tracker", pri=250.0, rf=12.5, pw=0.2, behavior="stable"),
        radarEmitter(classLabel="Freq_Hopper", pri=850.0, rf=9.5, pw=0.5, behavior="hopper")
    ]
        
        simulationDuration = 62000
        
        for emitter in emitters:
            pulses = emitter.genaratePulses(simulationDuration)
            allPulses.extend(emitter.genaratePulses(duration = simulationDuration))
            
        df = pd.DataFrame(allPulses)
        df = df.sort_values(by="ToA").reset_index(drop=True)
        
        df.to_csv("interleaved_signals_40k.csv", index=False)