#!/usr/bin/env python
#------------------------------------------------------------------------------
"""
program to read in data from a file
"""

import os, sys, re
from string import *
from ROOT import *

#function to split the text file into individual strings and then transform those into floats 
def convert_(x):
    t= split(x)
    t=map(atof, t)
    return t
    

def main():
    if len(sys.argv)< 2:
        sys.exit('''
        usage:
        ./read.py <file_name>
        ''')

    file_name = sys.argv[1]
    if not os.path.exists(file_name):
        sys.exit("file %s not found" % file_name)

        
    f =open(file_name, "r")

   
    records= f.readlines()

    header= split(records[0])

    records= records[1:]
    print("Number of Entries: %10d" %len(records)) 

    records= map(convert_, records)

  #  print(records[0])
   # print(records[-1])


    
    vmap= {}

    for i in xrange(len(header)):
        vmap[header[i]]= i

    sample_counter_VBF=0
    sample_counter_nVBF=0
    
   # print(len(records[-1]))

    VBF_analysis = open("v3_VBF_mass_delta_train.txt", "w")
    VBF_analysis.write("deltajj     massjj\n")

    nVBF_analysis = open("v3_nVBF_mass_delta_jj_train.txt", "w")
    nVBF_analysis.write("deltajj     massjj\n")
    
    
    for ii, records in enumerate(records):
        massjj_col= vmap["f_massjj"]
        sample_col= vmap["f_sample"]
        deltajj_col = vmap["f_deltajj"]

        if records[sample_col] == 1:

            if records[massjj_col] > 0:
              sample_counter_VBF += 1
              VBF_analysis.write("%f     %f\n" % (records[deltajj_col], records[massjj_col]))
            else:
                continue;
                
        if records[sample_col] != 1:
            
            if records[massjj_col] > 0:
                sample_counter_nVBF += 1
                nVBF_analysis.write("%f     %f\n" % (records[deltajj_col], records[massjj_col]))

            else:
                continue;
            
    print("The number of VBF samples is %10d" % sample_counter_VBF)
    print("The number of non-VBF samples is %10d" % sample_counter_nVBF)
               
try:
    main()
except KeyboardInterrupt:
    print("ciao")


