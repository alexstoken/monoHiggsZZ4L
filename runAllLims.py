#!/usr/bin/env python

"""
This is a quick scrip to run makeLimitPlots on all interesting variations, so that they do not need to be run by hand

To run: ./runAllLimits.py

Created by Alex Stoken 10 Jun 2017 Bari, IT
"""
import os, sys, re

def main():
    models = ['ZpBary', 'Zprime']
    limit_var = ['SR_met', 'SR_pt4l', 'SR_bnn1', 'SR_bnn2', 'SR_bnn3']
    baryMA = [1,10,50,150, 500, 1000]
    primeMA = [300]
    

    
    count = 0
    for model in models:
        if model == 'ZpBary':massMA = baryMA
        if model == 'Zprime':massMA = primeMA
            
        for var in limit_var:
            for MA in massMA:

                filename = "lim"+ model+str(MA)+var
                print filename
                cmd_runLim = "./makeLimitPlots.py %s %s %s %s" %(model, var, str(MA), filename)
                os.system(cmd_runLim)
                count +=1

    print count
try:
    main()
except KeyboardInterrupt:
    print("Keyboard Interrupt")
