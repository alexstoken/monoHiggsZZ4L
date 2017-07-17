#!/usr/bin/env python
#--------------------------------------------------------------------
"""
This program plots the results of a NN to differentiate signal v bkg for Higgs from VBF.
Program will plot the calcualted Determinant and the results produced from the NN on the same plot, as well as plots for each individually.

Created by Alex Stoken Jun 8 2017 Bari, IT

To Run: ./plot_VBF.py

This program takes 0 arguments and produces many plots
"""
from ROOT import *
import os, sys, re
from string import *
from time import sleep
import numpy as np

def convert_(x):
    t= split(x)
    t=map(atof, t)
    return t
    

def main():
    #initialize all 2d histograms, files, constants-------------------------------------------

    xbins = 35
    ybins = 35
    bins = 35
    off_set = 1.5

    sec=0

    gROOT.ProcessLine(".L v3_VBF_2jet.cpp")
    
    hVBF = TH2F("hVBF", "Mass_{jj} vs #Delta#eta_{jj} for VBF events", xbins, 0, 10, ybins, 0, 2000)
    h_nVBF = TH2F("h_nVBF", "Mass_{jj} vs #Delta#eta_{jj} for non-VBF events", xbins, 0, 10, ybins, 0, 2000)
    hD = TH2F("hD", "Determinant", xbins, 0, 10, ybins, 0, 2000)
    hVBF_BNN = TH2F("hVBF_BNN", "VBF BNN Results", xbins, 0, 10, ybins, 0, 2000)
    

    #create some 1d test histograms----------------------------------------------------

    #hist of distributions
    h1_massV = TH1F("h1_massV", "Mass_{jj} Distribution for VBF and non-VBF Higgs Events", ybins, 0, 2000)
    h1_deltaV = TH1F("h1_deltaV","#Delta#eta_{jj} Distribution for VBF and non-VBF Higgs Events", xbins, 0, 10)
    h1_mass_nV = TH1F("h1_mass_nV", "mass nVBF", ybins, 0, 2000)
    h1_delta_nV = TH1F("h1_delta_nV","delta nVBF", xbins, 0, 10)

    #hist of prob distrib from NN
    h1_test_VBF_BNN = TH1F("h1_mass_testBNN_V", "Test of BNN Seperation of VBF and non-VBF Higgs Events", bins, 0, 1)
    h1_test_nVBF_BNN =TH1F("h1_mass_testBNN_nV", "test BNN nVBF", bins, 0, 1)
  

    
    #Hist style section. Set color for hist fill. Blue is signal and red is bkg---------------------------

    #mass and delta VBF histos
    h1_massV.SetFillStyle(3001)
    h1_massV.SetFillColor(kBlue)
    h1_deltaV.SetFillStyle(3001)
    h1_deltaV.SetFillColor(kBlue)

    #NN histo
    h1_test_VBF_BNN.SetFillStyle(3001)
    h1_test_VBF_BNN.SetFillColor(kBlue)

    #mass and delta nVBF histos
    h1_mass_nV.SetFillStyle(3001)
    h1_mass_nV.SetFillColor(kRed)
    h1_delta_nV.SetFillStyle(3001)
    h1_delta_nV.SetFillColor(kRed)

    #NN histo
    h1_test_nVBF_BNN.SetFillStyle(3001)
    h1_test_nVBF_BNN.SetFillColor(kRed)
    
    #open data file and convert data to useful format------------------------------
    VBF_file = open("v3_VBF_mass_delta_test.txt")
    
    VBF_data = VBF_file.readlines()
    
    VBF_data = VBF_data[1:]
      
    VBF_data = map(convert_, VBF_data)

    #fill historgram for VBF events ----------------------------------------------
    for delta, mass in VBF_data:
        hVBF.Fill(delta, mass)
        h1_massV.Fill(mass)
        h1_deltaV.Fill(delta)
        h1_test_VBF_BNN.Fill(v3_VBF_2jet(delta, mass))

        
    #normalize
    hVBF.Scale(1./hVBF.Integral())
    h1_massV.Scale(1./h1_massV.Integral())
    h1_deltaV.Scale(1./h1_deltaV.Integral())


    #draw and save VBF 2d histo
        
    cVBF = TCanvas("fig_VBF", "VBF", 10,10, 500, 500)
    cVBF.cd()

    hVBF.GetXaxis().SetTitle("#Delta#eta_{jj}")
    hVBF.GetXaxis().SetTitleOffset(off_set)
    hVBF.GetYaxis().SetTitle("mass_{jj}")
    hVBF.GetYaxis().SetTitleOffset(off_set)
    
    hVBF.Draw("col")
    cVBF.Update()
    gSystem.ProcessEvents()

    sleep(sec)
    cVBF.SaveAs("VBF.pdf")
    
    #fill hists for nonVBF (bkg) events--------------------------------------------
    nVBF_file = open("v3_nVBF_mass_delta_jj_test.txt")
    
    nVBF_data = nVBF_file.readlines()
    
    nVBF_data = nVBF_data[1:]
      
    nVBF_data = map(convert_, nVBF_data)

    
    for delta, mass in nVBF_data:
        h_nVBF.Fill(delta, mass)
        h1_mass_nV.Fill(mass)
        h1_delta_nV.Fill(delta)
        h1_test_nVBF_BNN.Fill(v3_VBF_2jet(delta, mass))
        
    h_nVBF.Scale(1./h_nVBF.Integral())
    h1_mass_nV.Scale(1./h1_mass_nV.Integral())
    h1_delta_nV.Scale(1./h1_delta_nV.Integral())

    #draw and save nVBF 2d histo
        
    c_nVBF = TCanvas("fig_nVBF", "nVBF", 10,10, 500, 500)
    c_nVBF.cd()

    #setting axis labels
    h_nVBF.GetXaxis().SetTitle("#Delta#eta_{jj}")
    h_nVBF.GetXaxis().SetTitleOffset(off_set)
    h_nVBF.GetYaxis().SetTitle("mass_{jj}")
    h_nVBF.GetYaxis().SetTitleOffset(off_set)
    
    h_nVBF.Draw("col")
    c_nVBF.Update()
    gSystem.ProcessEvents()

    sleep(sec)
    c_nVBF.SaveAs("nVBF.pdf")

    #plot 1d histos-------------------------------------------------------------

    #mass
    c_1d_mass = TCanvas("fig_1d_mass_compare", "mass VBF v nVBF", 10, 10, 500, 500)
    c_1d_mass.cd()

    #set ymax
    y_max_mass = max(h1_massV.GetMaximum(), h1_mass_nV.GetMaximum())
    y_max_mass = 1.2 * y_max_mass
    h1_massV.SetMaximum(y_max_mass)
    h1_mass_nV.SetMaximum(y_max_mass)

    #draw hist and save to pdf
    h1_massV.GetYaxis().SetTitle("Events")
    h1_massV.GetYaxis().SetTitleOffset(1.4)
    h1_massV.GetXaxis().SetTitle("mass_{jj}")
    h1_massV.GetXaxis().SetTitleOffset(1.4)
    
    h1_massV.Draw("hist")
    h1_mass_nV.Draw("hist same")
    c_1d_mass.Update()
    gSystem.ProcessEvents()

    sleep(sec)
    c_1d_mass.SaveAs("mass_VBF_v_nVBF.pdf")

   

    #set y macx

    y_max_delta = max(h1_deltaV.GetMaximum(), h1_delta_nV.GetMaximum())
    y_max_delta = 1.2 * y_max_delta
    h1_deltaV.SetMaximum(y_max_delta)
    h1_delta_nV.SetMaximum(y_max_delta)

    #draw hist and save to file
    #delta
    
    c_1d_delta = TCanvas("fig_1d_delta_compare", "delta VBF v nVBF", 10, 10, 500, 500)
    

    h1_deltaV.GetYaxis().SetTitle("Events")
    h1_deltaV.GetYaxis().SetTitleOffset(1.4)
    h1_deltaV.GetXaxis().SetTitle("#Delta#eta_{jj}")
    h1_deltaV.GetXaxis().SetTitleOffset(1.4)

    c_1d_delta.cd()
    h1_deltaV.Draw("hist")
    h1_delta_nV.Draw("hist same")
    c_1d_delta.Update()
    gSystem.ProcessEvents()


    sleep(sec)
    c_1d_delta.SaveAs("delta_VBF_v_nVBF.pdf")

    #NN test
    c_test_NN = TCanvas("fig_1d_delta_compare", "delta VBF v nVBF", 10, 10, 500, 500)
    c_test_NN.cd()

    #set y macx

    y_max_NN = max(h1_test_VBF_BNN.GetMaximum(), h1_test_nVBF_BNN.GetMaximum())
    y_max_NN = 1.2 * y_max_NN
    h1_test_VBF_BNN.SetMaximum(y_max_NN)
    h1_test_nVBF_BNN.SetMaximum(y_max_NN)

    #draw hist and save to file
    h1_test_VBF_BNN.GetXaxis().SetTitle("Probability of being VBF")
    h1_test_VBF_BNN.GetXaxis().SetTitleOffset(off_set)
    h1_test_VBF_BNN.GetYaxis().SetTitle("Events")
    h1_test_VBF_BNN.GetYaxis().SetTitleOffset(off_set)
    
    h1_test_VBF_BNN.Draw("hist")
    h1_test_nVBF_BNN.Draw("hist same")
    c_test_NN.Update()
    gSystem.ProcessEvents()

    sleep(sec)
    
    c_test_NN.SaveAs("NN_test.pdf")

    #find best cut for the data----------------------------------------------------------------

    overall_max = 0
    cut_bin = 0
    count = 0
    count2 = 0 

    for i in xrange(1,bins
                        +1):
        Vbin_tot = 0
        nVbin_tot = 0
        Vbin_cont = 0
        nVbin_cont = 0
        count += 1
    
        for j in xrange(i,bins+1):
            
            Vbin_cont += h1_test_VBF_BNN.GetBinContent(j)
            nVbin_cont += h1_test_nVBF_BNN.GetBinContent(j)
  
            count2 += 1
            if nVbin_cont != 0:
                ratio = Vbin_cont / nVbin_cont
                #print(ratio)
            else:
                continue
            max_funct = nVbin_cont * ( ( 1 + ratio)*np.log( 1 + ratio) - ratio)

           
            if max_funct > overall_max:
                overall_max = max_funct
                cut_bin = i
                #print(overall_max)
            else:
                continue;
        
    cut_location = (1. / bins) * cut_bin
    print(count , count2, cut_bin, cut_location)
 
    
    
    #create and plot determinant hist----------------------------------------------

    h_nVBF.Add(hVBF)

    hVBF.Divide(h_nVBF)

    hD = hVBF

    #setting axis labels
    hD.GetXaxis().SetTitle("#Delta#eta_{jj}")
    hD.GetXaxis().SetTitleOffset(off_set)
    hD.GetYaxis().SetTitle("mass_{jj}")
    hD.GetYaxis().SetTitleOffset(off_set)
    hD.SetTitle("Comparison of VBF test events to BNN Output")
    
    hD.Scale(1./hD.Integral())
    c_D = TCanvas("fig_D", "D", 10,10, 500, 500)
    c_D.cd()
  
    """
    hD.Draw("col")
    c_D.Update()
    gSystem.ProcessEvents()
    sleep(sec)  
    c_D.SaveAs("D.pdf")
    """
     
    #fill 2d hist for VBF_BNN--------------------------------------------

    xmin = 0.
    xmax = 10.
    ymin = 0.
    ymax = 2000.
    xstep = (xmax - xmin)/xbins
    ystep = (ymax -ymin)/ybins

   
    for i in xrange(0,xbins):
        x= (i+.5) * xstep
        #print("x = ", x)
        
        for j in xrange(0,ybins):
            y = (j+.5) * ystep

            #print("y = ", y)
            P= v3_VBF_2jet(x,y)
            #print(P)
            hVBF_BNN.SetBinContent(i+1, j+1, P)


 
    c_NN = TCanvas("fig_NNcompare", "NN v D")
    c_NN.cd()

    
    hD.Draw("col")


    hVBF_BNN.Draw("cont1 same")
    
    c_NN.Update()
    gSystem.ProcessEvents()
    sleep(sec)
    c_NN.SaveAs("NNvD.pdf")
    

try:
    main()
except KeyboardInterrupt:
    print("Keyboard Interrupt")


            
