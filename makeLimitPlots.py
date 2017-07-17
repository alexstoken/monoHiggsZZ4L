#!/usr/bin/env python
#----------------------
"""
This program works with data output from computeLimits.py (HBProsper, 2017) to plot limits for various models. 

This program takes 1 argument as input and creates a .pdf(or .root, depending on preference) of a TGraph with the limits desired as output. 

INPUTS AS ARGUMENTS: model{ZpBary, Zprime} limit_var{SR_met, SR_pt4l, SR_bnn1, SR_bnn2, SR_bnn3} mass_MA file_name [-sf] scale_factor

Where specific modifications should be made to accomodate various models, comments will be made in CAPITALS. All other comments only explain the code.

To run: ./makeLimitPlots.py

Created by Alex Stoken 29 June 2017 Bari, IT

"""

import os, sys, re, fnmatch, argparse, subprocess
from ROOT import *
from string import *
from time import sleep
import numpy as np
import array as ar
from copy import copy, deepcopy


def main():

#-----------------------------------------STEP 1: create configuration files for all limits of interest ---------------------------------------------------------------------------

    #set up argument parser to take in the model, limit variable, file name, and scale factor from the command line

    parser = argparse.ArgumentParser()
    parser.add_argument("model", type= str, choices = ["ZpBary", "Zprime"], help = "Choose a model to generate limits for")
    parser.add_argument("limit_variable", type = str, choices = ["SR_bnn1", "SR_bnn2", "SR_bnn3", "SR_met", "SR_pt4l"], help = "choose a variable to run the limit using")
    parser.add_argument("mass_MA", type = str, help = "choose a mass of MA to make the limits for")
    parser.add_argument("-sf", "--scale_factor", type = float, help ="uncertaintly scaling factor, 1 by default")
    parser.add_argument("file_name", type = str, help = "Designate the name (without extension) of the output plot files")

    args = parser.parse_args()
   
    model = args.model
    limit_var = args.limit_variable
    plot_filename = args.file_name
    mass_MA = args.mass_MA

    while len(mass_MA) < 5:
        mass_MA = "0"+mass_MA
    mass_MA = "*MA"+mass_MA+"*"


    if args.scale_factor:
        scale_f = float(args.scale_factor)
        
    else:
        scale_f = 1.


    #now we want to grab all the files matching the argument characteristics
                 
    if model == "ZpBary":
            logX = 1
            xsec_leg ="Z'Baryonic x BR (fb) "
         
    elif model == "Zprime":
            logX = 0
            xsec_leg ="Z'2HDM x BR (fb) "



    #start my moving to the directory with all of our files in it 
    rootDir = "/Users/alexstoken/projects/monoHiggs/monoHZZ4LRun2016/histos"

    list_of_limits = []

    #loop to get the mass from each of the files that match the characteristics from the arguments
    for fname in os.listdir(rootDir):
             if fnmatch.fnmatch(fname, "histos*") and fnmatch.fnmatch(fname, '*'+model+'*') and fnmatch.fnmatch(fname, mass_MA):
                     pattern_MZ = re.compile('(?<=MZp)[0-9]+(?=_)')
                     MZp = pattern_MZ.findall(fname)
                     list_of_limits.append(MZp[0])

  
    bin_num = 200                            #ok to be large, since if there are less bins the program will use the lesser value
    obs_file = "histos/histos_data.root"     #insert your data histogram
    sample_num = 1
    bkg_file = "histos/histos_SM.root"       #insert your background, SM for DM finding, Higgs for VBF finding
    logY = 1
    y_max = 1e5
    y_min = 1e-4

    
    #numpy arrays are used for ease of element by element multiplication
    
    mZ = np.array([])                                                 
    obs_limit = np.array([])
    minus_2sig = np.array([])
    minus_sig =np.array([])
    expect_limit = np.array([])
    plus_sig = np.array([])
    plus_2sig = np.array([])
    
    #just to be sure that computeLimits.py will work, we will source setup.sh
    os.system("source setup.sh")  

    scale_str = str(scale_f)
    scale_str = scale_str.replace(".", "")
    cmd_openFile = "event_file = open(\"events_%s%s%s_%s.txt\", \"w+\")" %(model,args.mass_MA,limit_var, scale_str)
    exec(cmd_openFile)
    event_file.write("File\t\t\t\t\t\t\tVariable\tEntries\t\t\tUpperLimit\t\tNum of Limits\n")
    for file_ in [obs_file, bkg_file]:
            
            f = TFile.Open(file_)
            h = f.Get(limit_var)
            entries = h.GetEntries()
            event_file.write("%s\t\t\t\t\t%s\t\t%s\n" %(f.GetName(), limit_var, entries))

    event_file.close()
    iter_list_of_limits = copy(list_of_limits)

   
    
    #make a config file for each limit requested in list_of_limits
    for mass in iter_list_of_limits:
    
        for dirName, subdirList, fileList in os.walk(rootDir):

            for fname in fileList:
                if fnmatch.fnmatch(fname, "histos*") and fnmatch.fnmatch(fname, '*'+model+'*') and fnmatch.fnmatch(fname, '*MZp'+mass+'*') and fnmatch.fnmatch(fname, mass_MA):
                    signal_file = fname


        if scale_f != 1 and limit_var == "SR_met":

            #adjust signal
            cmd_getFile = "sig_file = TFile(\'histos/%s\', \"READ\")" %signal_file
            exec(cmd_getFile)
            cmd_getHist = "h = sig_file.Get(\'%s\')" % (limit_var)
            exec(cmd_getHist)

            #adjust background
            cmd_getFile = "bkg_adjust = TFile(\'%s\', \"READ\")" %bkg_file
            exec(cmd_getFile)
            cmd_getHist = "h2 = bkg_adjust.Get(\'%s\')" % (limit_var)
            exec(cmd_getHist)
            
         
            
            h_up = h.Clone("h_up")
            h_down = h.Clone("h_down")
            h_up.Scale(scale_f)
            h_down.Scale(1/scale_f)

            h2_up = h2.Clone("h2_up")
            h2_down = h2.Clone("h2_down")
            h2_up.Scale( scale_f)
            h2_down.Scale(1/scale_f)

            scaled_hists = TFile("histos/scaled_hists.root", "RECREATE")
            h_up.Write()
            h_down.Write()
            h2_up.Write()
            h2_down.Write()
            scaled_hists.Close()


            
            filename_up = "up" + model + mass + "_" +args.mass_MA 
            filename_down = "down" + model + mass + "_" +args.mass_MA
            
            cfg_filename_up = filename_up + ".cfg"
            cfg_filename_down = filename_down + ".cfg"

            cmd_newFile_up = "cfg_file_up = open(\"%s\", \"w+\")" %cfg_filename_up
            exec(cmd_newFile_up)

            cfg_file_up.write(
            "#bin_num \n%s \n#obs_count \n%s %s \n#sample_num \n%s \n#signal \nhistos/scaled_hists.root h_up \n#bkg \nhistos/scaled_hists.root h2_up" % (str(bin_num), obs_file, limit_var, str(sample_num)))

            cfg_file_up.close()

            cmd_newFile_down = "cfg_file_down = open(\"%s\", \"w+\")" %cfg_filename_down
            exec(cmd_newFile_down)

            cfg_file_down.write(
            "#bin_num \n%s \n#obs_count \n%s %s \n#sample_num \n%s \n#signal \nhistos/scaled_hists.root h_down \n#bkg \nhistos/scaled_hists.root h2_down" % (str(bin_num), obs_file, limit_var, str(sample_num)))

            cfg_file_down.close()

         

            cmd_runcompLim_up = "auto_computeLimit.py %s" %cfg_filename_up
            os.system(cmd_runcompLim_up)

            cmd_runcompLim_down = "auto_computeLimit.py %s" %cfg_filename_down
            os.system(cmd_runcompLim_down)


            results_name_up = "auto_%s.txt" %(filename_up)
            results_name_down = "auto_%s.txt" %(filename_down)

            if os.stat(results_name_up).st_size == 0 and os.stat(results_name_down).st_size == 0:
                
                list_of_limits.remove(mass)

            else:
                with open(results_name_up) as f:
                    results_data = f.read().splitlines()
                    
                results_data = map(atof, results_data)
        
 
                mZ_up = np.append(mZ, float(mass))
                obs_limit_up = np.append(obs_limit, results_data[0])
                minus_2sig_up = np.append(minus_2sig, results_data[1])
                minus_sig_up = np.append(minus_sig, results_data[2])
                expect_limit_up = np.append(expect_limit, results_data[3])
                plus_sig_up = np.append(plus_sig, results_data[4])
                plus_2sig_up = np.append(plus_2sig, results_data[5])

                with open(results_name_down) as f:
                    results_data = f.read().splitlines()
                    
                results_data = map(atof, results_data)
        
 
                mZ_down = np.append(mZ, float(mass))
                obs_limit_down = np.append(obs_limit, results_data[0])
                minus_2sig_down = np.append(minus_2sig, results_data[1])
                minus_sig_down = np.append(minus_sig, results_data[2])
                expect_limit_down = np.append(expect_limit, results_data[3])
                plus_sig_down = np.append(plus_sig, results_data[4])
                plus_2sig_down = np.append(plus_2sig, results_data[5])


                mZ = (mZ_up + mZ_down) / 2
                obs_limit = (obs_limit_up + obs_limit_down) / 2
                minus_2sig = (minus_2sig_up +  minus_2sig_down) / 2
                minus_sig = (minus_sig_up + minus_sig_down) / 2
                expect_limit = (expect_limit_up + expect_limit_down) / 2
                plus_sig =(plus_sig_up + plus_sig_down) / 2
                plus_2sig = (plus_2sig_up + plus_2sig_down) / 2

                f = TFile.Open("histos/"+signal_file)
                h = f.Get(limit_var)
                entries = h.GetEntries()
                cmd_append = "event_file = open(\"events_%s%s%s_%s.txt\", \"a\")" %(model,args.mass_MA, limit_var, scale_str)
                exec(cmd_append)
                event_file.write("%s\t\t%s\t\t%s\t\t\t%s\t\t\t%s\n" %(f.GetName(), limit_var, entries,str(results_data[0]), len(mZ)))
                                     
                event_file.close()


            cmd_rmAuto = "rm -f auto_*.txt"
            os.system(cmd_rmAuto)
            
        else:          
            filename = model + mass + "_" +args.mass_MA
            cfg_filename = filename + ".cfg"
            cmd_newFile = "cfg_file = open(\"%s\", \"w+\")" %cfg_filename
            exec(cmd_newFile)
            cfg_file.write(
            "#bin_num \n%s \n#obs_count \n%s %s \n#sample_num \n%s \n#signal \nhistos/%s %s %s\n#bkg \n%s %s" % (str(bin_num), obs_file, limit_var, str(sample_num), signal_file, limit_var, str(scale_f), bkg_file, limit_var))
            cfg_file.close()


        

#--------------------------------------STEP 2: call computeLimits.py on all configuration files ----------------------------------------------------------------------

            cmd_runcompLim = "auto_computeLimit.py %s" %cfg_filename
            os.system(cmd_runcompLim)

    
#-------------------------------------STEP 3: take data from .txt file (output from computeLimits.py) and add it to numpy arrays for use ------------------------------------------


            results_name = "auto_%s.txt" %(filename)
            
            if os.stat(results_name).st_size == 0:
                
                list_of_limits.remove(mass)
            
            else:
                with open(results_name) as f:
                    results_data = f.read().splitlines()
                
                results_data = map(atof, results_data)
        
 
                mZ = np.append(mZ, float(mass))
                obs_limit = np.append(obs_limit, results_data[0])
                minus_2sig = np.append(minus_2sig, results_data[1])
                minus_sig = np.append(minus_sig, results_data[2])
                expect_limit = np.append(expect_limit, results_data[3])
                plus_sig = np.append(plus_sig, results_data[4])
                plus_2sig = np.append(plus_2sig, results_data[5])
                
                f = TFile.Open("histos/"+signal_file)
                h = f.Get(limit_var)
                entries = h.GetEntries()
                cmd_append = "event_file = open(\"events_%s%s%s_%s.txt\", \"a\")" %(model,args.mass_MA, limit_var, scale_str)
                exec(cmd_append)
                event_file.write("%s\t\t%s\t\t%s\t\t\t%s\t\t\t%s\n" %(f.GetName(), limit_var, entries,str(results_data[0]), len(mZ)))
                                     
                event_file.close()

            cmd_rmAuto = "rm -f auto_%s.txt" % filename
            os.system(cmd_rmAuto)

    
    
#------------------------------------STEP 4: set cross section values and scale the data--------------------------------------------------------------    
    #SET CROSS SECTION VALUES 
    #dependent on specific analysis used


    xsec_file = open("cross_sections.txt",'r')
    xsec_lines = xsec_file.read().splitlines()

    xsec_original = np.array([])
    xsec_re = re.compile('\s(.*)')

    for mass in mZ:
        for line in xsec_lines:
           
            if line.find(model)!= -1 and line.find("_MZp-"+str(int(mass))+"_") != -1 and line.find("-"+args.mass_MA+"_13TeV") != -1:
         
                xsec = xsec_re.findall(line)
                xsec_original = np.append(xsec_original, float(xsec[0]))



    #xsec is in pb, but all other values are in fb, so must convert xsec
    PBtoFB = 1E3

    #scale cross section by conversion factor
    xsec_scale = PBtoFB * xsec_original

    #write all the data into a file while it's still in mu form
    cmd_append = "event_file = open(\"events_%s%s%s_%s.txt\", \"a\")" %(model,args.mass_MA, limit_var, scale_str)
    exec(cmd_append)
    event_file.write("\n\n\nThe following are the values of mu:")
    event_file.write("\nMass Z':\t" + str(list_of_limits))
    event_file.write("\nObserved Limit:\t" + str(obs_limit) + "\nExpected Limit:\t" + str(expect_limit) + "\n-2sigma:\t" + str(minus_2sig) + "\n-sigma:\t\t" + str(minus_sig) + "\n+sigma:\t\t" + str(plus_sig) + "\n+2sigma:\t" + str(plus_2sig))
    event_file.close()
    
    #scale all limits by by the cross section
    obs_limit = xsec_scale * obs_limit
    expect_limit = xsec_scale *expect_limit
    plus_sig = xsec_scale *plus_sig
    plus_2sig = xsec_scale *plus_2sig
    minus_sig =xsec_scale * minus_sig
    minus_2sig = xsec_scale *minus_2sig


    #write all this data back into the events file now that it's set as a limit
    cmd_append = "event_file = open(\"events_%s%s%s_%s.txt\", \"a\")" %(model,args.mass_MA, limit_var, scale_str)
    exec(cmd_append)
    event_file.write("\n\n\nThe following are the values of the upper limit")
    event_file.write("\nMass Z':\t" + str(list_of_limits))
    event_file.write("\nObserved Limit:\t" + str(obs_limit) + "\nExpected Limit:\t" + str(expect_limit) + "\n-2sigma:\t" + str(minus_2sig) + "\n-sigma:\t\t" + str(minus_sig) + "\n+sigma:\t\t" + str(plus_sig) + "\n+2sigma:\t" + str(plus_2sig))
    event_file.close()
    

#-----------------------------------STEP 5: make the limits plots----------------------------------------------

    #TGraph can only take 'C' style arrays, so must convery numpy arrays to 'C' style using Python array module 
    mZ = ar.array('d', mZ)
    obs_limit = ar.array('d', obs_limit)
    expect_limit = ar.array('d', expect_limit)
    xsec_final = ar.array('d', xsec_scale)



    #number of data points (aka number of masses), needed to give a size to the graphs
    n = len(list_of_limits)
    
    #initialize graphs for all the lines, in the format TGraph(num of points, x vals, y vals)
    g_obs_lim = TGraph(n, mZ, obs_limit)
    g_expect_lim = TGraph(n, mZ, expect_limit)
    g_xsec = TGraph(n, mZ, xsec_final)


    
    #make two new graphs to draw the sigma bands
    g_1sig = TGraph(2*n)
    g_2sig = TGraph(2*n)


    #add points to sigma bands so that each point is followed by it's additive inverse (+sigma @i -> -sigma @(i+1)-> +sigma @(i+2))
    #this ensures that the graph will be shaded in the correct region
    for i in xrange(0,n):
        g_1sig.SetPoint(i, mZ[i], plus_sig[i])
        g_1sig.SetPoint(n+i , mZ[n-i-1], minus_sig[n-i-1])
        
        g_2sig.SetPoint(i, mZ[i], plus_2sig[i])
        g_2sig.SetPoint(n+i , mZ[n-i-1], minus_2sig[n-i-1])

    #graph formatting (color, width, fill,style)
    g_2sig.SetFillColor(5)
    g_1sig.SetFillColor(3)
    g_expect_lim.SetLineWidth(2)
    g_expect_lim.SetLineStyle(2)
    g_obs_lim.SetLineWidth(2)
    g_xsec.SetLineWidth(2)
    g_xsec.SetLineStyle(2)
    g_xsec.SetLineColor(kBlue)
    
    #initialize and format canvas
    c = TCanvas()
    c.cd()

    #when using TGraph best to have a frame to manipulate
    #AXIS LIMITS ON FRAME ARE ADJUSTABLE BASED ON LIMITS
    last_lim = len(list_of_limits)
    frame = c.DrawFrame(float(list_of_limits[0]), y_min, float(list_of_limits[last_lim - 1]), y_max)
    
    #CHOOSE LOG SCALE FOR AXIS, ADDING TICKS AND GRID OPTIONAL
    c.SetLogy(logY)
    c.SetLogx(logX)
    c.SetTicks()
    c.SetGrid()
    
    #draw graphs in the order you want to see them with the one to be in the "background" drawn first
    #will automatically add them to the frame
    g_2sig.Draw("F")
    g_1sig.Draw("F")
    g_expect_lim.Draw("L")
    g_obs_lim.Draw("L")
    g_xsec.Draw("L")

  
    #set frame properties (ALL ADJUSTABLE)  
    frame.SetTitle("")
    frame.GetYaxis().SetTitleOffset(1.0)
    frame.GetYaxis().SetTitleSize(.04)
    frame.GetXaxis().SetTitle("m_{Z'} (GeV)")
    frame.GetYaxis().SetTitle("95% C.L. #sigma(pp #rightarrow Z' #rightarrow A_{0}H #rightarrow #chi #chi llll) (fb)")

    #create and format legend(ALL ADJUSTABLE)
    legend = TLegend(0.15, 0.65, 0.5, 0.85)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.SetTextSize(.032)

    #SET YOUR LEGEND ENTRIES
    legend.AddEntry(g_xsec, xsec_leg , "L")
    legend.AddEntry(g_expect_lim, "Expected Limit", "L")
    legend.AddEntry(g_1sig, "#pm 1 #sigma", "F")
    legend.AddEntry(g_2sig, "#pm 2 #sigma", "F")
    legend.AddEntry(g_obs_lim, "Observed Limit", "L")
    #add legend entries here

    #draw legend
    c.cd()
    legend.Draw()
    
    
    #create and format text boxes (ALL ADJUSTABLE)
    graph_info = TPaveText(.095, .902, 0.92, .94, "NDC")
    graph_info.SetTextSize(.032)
    graph_info.SetFillColor(0)
    graph_info.SetBorderSize(0)
    graph_info.SetTextAlign(12)
    cms_prelim = "#font[22]{CMS} #font[12]{Preliminary}"
    graph_info.AddText(.01, .5, cms_prelim)
    run_info = "#sqrt{s} = 13 TeV, L = 35.9 fb^{-1} "
    graph_info.AddText(.65, .6, run_info)
    
    #draw pave
    c.cd()
    graph_info.Draw()

    limit_producer = TPaveText(.7, .75, .8, .85, "NDC")
    limit_producer.SetTextSize(.07)
    limit_producer.SetFillStyle(0)
    limit_producer.SetBorderSize(0)

    if limit_var =="SR_bnn1":
        limit_info = "#font[22]{#it{D}(#it{E}_{T}^{miss})}"

    if limit_var =="SR_bnn2":
        limit_info = "#font[22]{#it{D}(#it{m}_{4l}, #it{D}_{bkg}^{kin})}"

        
    if limit_var =="SR_bnn3":
        limit_info = "#font[22]{#it{D}(#it{m}_{4l}, #it{D}_{bkg}^{kin}, #it{E}_{T}^{miss})}"
        
    if limit_var =="SR_met":
        limit_info = "#font[22]{#it{E}_{T}^{miss}}"
        
    if limit_var =="SR_pt4l":
        limit_info ="#font[22]{#it{p}_{T(4l)}}"


    
    limit_producer.AddText(.01, .5, limit_info)
    c.cd()
    limit_producer.Draw()
   

    
    c.Update()
    gSystem.ProcessEvents()
    
    #ONLY SLEEP IF YOU WANT GRAPH TO POP UP ON SCREEN
    sleep(0)
    
    
    #SAVE CANVAS TO LOCATION AND WITH EXTENSION OF YOUR CHOOSING
    c.SaveAs( plot_filename +".pdf")
    c.SaveAs( plot_filename +".root")



    #Clean up directory system
    os.system("mkdir -p event_yields")
    
    os.system("mv -f events_%s%s%s_%s.txt event_yields/" %(model,args.mass_MA,limit_var, scale_str))
    os.system("mkdir -p limplots_pdf")
    os.system("mkdir -p limplots_root")
    os.system("mv -f *.cfg cfg_files")

    os.system("mv %s.pdf limplots_pdf/" %plot_filename)
    os.system("mv %s.root limplots_root/" %plot_filename)

    
try:
    main()
except KeyboardInterrupt:
    print("Keyboard Interrupt")
