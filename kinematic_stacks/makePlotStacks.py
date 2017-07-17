#!/usr/bin/env python
#--------------------------------
"""
this program will create TChains, run a MakeClass macro on those TChains, and then produce a TStack from the histograms output from the MakeClass. 

To run: ./makeChains.py

MUST HAVE muAnalysis.C and muAnalysis.h in the same directory to successfully run the script


Program build for trees in a format similar to "HZZ4LeptonsAnalysisReduced", but can be modified to support other tree formats

Outline: 1. Create TChains to loop over and variables of interest to plot
         2. Generate yield for each chain (each chain is a different bkg/signal/model
         3. Collect all histograms made by the makeClass running on the chain and put them in one file using hadd
         4. Loop over each histogram individually and set its style properties
         5. Add histograms to the THStacks, add the THStacks to the canvas, and modify histogram properties (axis labels, rebinning, etc).
            *NOTE WHEN MODIFYING HISTOGRAM PROPERTIES: modify the property of the THStack since it is the base plot that the other plots are 
                                                       drawn on top of. So modifications to THStack will persist. 
         6. Format the canvas with such things as legend, log scale, text boxes
         7. Save the canvas/histogram as both root and pdf files
"""

import os, sys, re
from ROOT import *
from string import *
from time import sleep 


#runs makeClass called muAnalsis.C on the TChain features, passes in the chain and the chain's title
def run(chain):
    gROOT.ProcessLine(".L muAnalysis.C")
    
    chain_title = chain.GetTitle()
 
    m = muAnalysis(chain, chain_title)
    m.Init(chain)
    m.Loop()


#function to loop through all the histos in a particular plot (for a certain varioable) and return the maximum value
def getYmax(var, list_of_histos, file_with_histos):
        #Goal is to set ymax to be 10% higher than the highest bin, remembering that the THStack is the base plot
        global_max = 0

        
        for hist_name in list_of_histos:
                if hist_name.find(var) != -1:
                    cmd_getObj = "h = file_with_histos.Get(\'%s\')" % hist_name
                    exec(cmd_getObj)
                    temp_max = h.GetMaximum()
                    
                    if temp_max > global_max:
                        global_max = temp_max
                
        return global_max

#compute number of events per given unit on the x axis
def getPerBin(stack, num_rebin):
    x_max = stack.GetXaxis().GetXmax()
    nbins = stack.GetHistogram().GetNbinsX()
    
    #to find per bin number
    per_bin = x_max / nbins
    
    if num_rebin != 0:
            per_bin = per_bin * num_rebin   
            
    return per_bin          

def main():

#---------------------------------------------------------------------------STEP 0: set variable properties for plots--------------------------------------------------
    sleep_time = 5
    log_setY = 1        #1 for log, 0 for nonlog plot
    log_setX = 0
    data_draw_options = "hist same E1PX0"
    model_draw_options = "hist same"
    stack_draw_options = "hist"
    bkg_fillStyle = 1001
    treename = "HZZ4LeptonsAnalysisReduced"   #note treename must be the same for all files (MUST BE CHANGED FOR A DIFFERENT ANALYSIS)
    yield_file_name = "event_counts.txt"
    data_set_info = "#sqrt{s} = 13 TeV, L = 35.867 fb^{-1}" 
    cms_prelim_txt = "#font[22]{CMS} #font[12]{Preliminary}"
    Right_margin = .2
    Left_margin = .072
    


    
#--------------------------------------STEP 1: create TChains for the different typed of background and signal we will be plotting, pick variables to plot ----------------------------

    #create a list of the different variables you want to plot (see muAnalysis to see which variables have been filled)

    #list is in the format (variable, n_rebins desired, X axis title with Latex support, units with latex support, y min (0 if autoset) )
    variable_list = [
        ("massjj", 2, "Mass_{jj}", "GeV", 0),
        ("deltajj", 2, "#Delta#eta_{jj}", "units", 0),
        ("D", 2, "Discriminant", "units", 1e-4 ),
        ("mass4l", 2, "Mass_{4l}", "GeV", 0),
        ("pt4l", 2, "PT_{4l}", "GeV", 0),
        ("pfmet", 2,"PF_{MET}", "GeV", 1e-3)
        ]
    """TODO: create a way to send to makeClass which variables to plot from python script"""


    #create list of all the types of physics objects (data, types of backgrounds, models, etc) you intend to plot

    #this list has tuples in the format (chain title, files chain is produced from, color for plotting, title for legend)

    #CAERFULLY SELECT WILDCARDS
    chain_list = [
        ("data_2016","*Run2016*" , kBlack, "2016 Data"),
        ("TTT", "output_*_*TTT*", kTeal -6, "TTT"),
        ("TTV","*LNu*amcatnlo*" , kAzure +4, "TTV"), 
        ("VVV","output_*_*Z_TuneCUETP8M1_13TeV-amcatnlo-*.root" , kAzure -4, "VVV"),
        ("WZ", "*WZTo3LNu*", kCyan -2, "WZ"),
        ("WW", "*WWTo*", kCyan +3, "WW"),
        ("Zplusjets","output_*_DYJ*" , kAzure +2, "Z+jets"), 
        ("ttbar","output_*_TTTo2L2Nu*" , kGreen +3, "t#bar{t}"), 
        ("WH", "output_*_*HWJ*", kOrange +2, "WH, m_{H} =125 GeV"),
        ("ZH", "output_*_*HZJ*", kOrange -1 , "ZH, m_{H} =125 GeV"),
        ("VBF","output_*_VBF*" , kOrange -6, "VBF, m_{H} =125 GeV"),
        ("ttH","output_*_ttH*" , kOrange, "ttH"),
        ("ggH", "output_*_GluGluHToZZTo4L*", kOrange -3, "ggH, m_{H} =125 GeV"),
        ("mzChi1", "output_*_*_MChi-1_*", kBlue+2, "Z_{p} to m_{#Chi}"),
        ("ZZ", "output_*_ZZTo*", kCyan -7, "ZZ"),
        ("ggToZZ", "output_*_GluGluToContinToZZT*", kCyan -5, "ggToZZ"),
        ("mz600","output_*_Zprime*600*" , kGreen -4, "m_{z} = 600 GeV, m_{A_{0}} = 300 GeV"),
        ("mz800","output_*_Zprime*800*" , kBlue -4, "m_{z} = 800 GeV, m_{A_{0}} = 300 GeV"),
        ("mz1","output_*_Zprime*1000*" , kRed -4 , "m_{z} = 1 TeV, m_{A_{0}} = 300 GeV"),
        ("mz12","output_*_Zprime*1200*" , kOrange -3, "m_{z} = 1.2 TeV, m_{A_{0}} = 300 GeV"),
        ("mz14","output_*_Zprime*1400*" , kBlack, "m_{z} = 1.4 TeV, m_{A_{0}} = 300 GeV"),
        ("mz17","output_*_Zprime*1700*" , kCyan, "m_{z} = 1.7 TeV, m_{A_{0}} = 300 GeV")
        ]

    #set up file to track event yields, open in write+ mode to rewrite previous yield file 
    cmd_newYieldfile = "num_events = open(\"%s\", \"w+\")" %(yield_file_name)
    exec(cmd_newYieldfile)
    num_events.write("Bkg/ Signal Type\t# of Entries \n")
    num_events.close()


    #loop over the list of objects and create an empty TChain with that object name
    #add the proper trees to the chains using their file names and then run the makeClass on the chains to fill histograms for the variables in question
    for chain, file_name, color, title in chain_list:
        cmd_newChain = "%s = TChain(treename, \"%s\")" % (chain, chain)
       
        cmd_addChain = "x = %s.Add(\"%s\")" % (chain, file_name)
      
        cmd_run = "run(%s)" %chain
        
        exec(cmd_newChain)
        exec(cmd_addChain)
        exec(cmd_run)
#-----------------------------------------------------STEP 2: Count the events in each physics object for each plot, print out to a file ------------------------------
        

        #Move to working in the file in append mode, so you just add a line for each chain
        cmd_openYield_append = "num_events = open(\"%s\", \"a\")" %(yield_file_name)
        exec(cmd_openYield_append)
        entries = eval("%s.GetEntries()" %chain)
        num_events.write("%s\t\t\t%s\n" % (chain, str(entries)))
        
        
        #print "Number of files in" + chain + " chain = " + str(x)       OPTIONAL STATEMENT TO PRINT THE NUMBER OF FILES ADDED TO THE CHAIN

 
        
#---------------------------------------------STEP 3: retrieve all histograms created by makeClass and put them in one file with hadd-------------------------------------

    #now, after the run function has been called (line 90), a variaty of historgrams have been made by the makeClass muAnalysis.C
    #The histograms are in files of the type "<<physics object>>_histos.root, and these files contain histograms named in the format <<physics object>>_<<variable>>

    #put all the histograms in one file, so that they can all be manipulated without having to do too much file management
    os.system("hadd -f muAnalysisHistos.root *_histos.root ")

    #open the file containing all the histograms
    all_histos = TFile("muAnalysisHistos.root", "READ")

    #get a list of all the keys for all the histograms
    key_list = all_histos.GetListOfKeys()

    #empty list that is ready for the names of the histograms which were from the hadd file which are from the makeClass
    h_list = []    #list of histogram names

    #loop over all the keys (where each key points to a histogram in the hadd file) that reads the object from the key and then appends the name of the object to the end of the name list  
    for key in key_list:
        h = key.ReadObj()
        h_list.append( h.GetName())
        


 #-----------------------------------------------------------------------------STEP 4: Style the histograms individually----------------------------------------

    #loop over all the chains of histos created
    for chain, file_, color, title in chain_list:

        #for every individual histogram created from the chains
        for hist_name in h_list:

              #this grabs the histogram object so that it can be modified
              cmd_getObj = "h = all_histos.Get(\'%s\')" % hist_name
              exec(cmd_getObj)
              #h.SetDirectory(0)  ONLY ACTIVATE IF YOU WANT TO TAKE CONTROL OF THE HISTOGRAM'S POSITION IN MEMORY INSTEAD OF LEAVING IT IN THE all_histos FILE

              
              #get title of chain to be used in a "file" algorithm later
              cmd_chainTitle = "chain_title = %s.GetTitle()" %chain
              exec(cmd_chainTitle)

              #general commands to set line and fill color for the histo, places here so they are in scope everywhere they are called 
              cmd_Linecolor = "h.SetLineColor(%s)" % color
              cmd_Fillcolor = "h.SetFillColor(%s)" % color
              cmd_Markercolor = "h.SetMarkerColor(%s)" %color

              #BE CAREFUL THAT "FIND" COMMAND WILL FIND THE CORRECT, UNIQUE MATCH

              #this if statement only runs if the histogram name matches the physics object of interest
              if hist_name.find(chain_title) != -1 :
                  
                  if chain_title == "data_2016":

                      #data will be black dots
                      h.SetMarkerStyle(20)
                      h.SetMarkerColor(kBlack)
                      h.SetLineColor(kBlack)

                  elif chain_title.find("mz") != -1:

                      #models will be drawn as lines 
                      h.SetLineWidth(2)
                      exec(cmd_Linecolor)
                      exec(cmd_Markercolor)

                  elif chain_title.find("VBF")!= -1 and (hist_name.find("massjj") != -1 or hist_name.find("deltajj") != -1 or hist_name.find("D") != -1):
                      h.SetLineWidth(2)
                      exec(cmd_Markercolor)
                      exec(cmd_Linecolor)

                  else:
                      #backgrounds are drawn as filled histograms
                      h.SetFillStyle(bkg_fillStyle)
                      #h.SetLineColor(kBlack)
                      exec(cmd_Linecolor)
                      exec(cmd_Markercolor)
                      exec(cmd_Fillcolor)
                      
    
    
#--------------------------STEP 5: Add histos to stacks, Draw the histograms into canvases and modift histogram properties (axis titles, axis limits, rebin etc) ----------

    #loop over each variable you want to plot, so that a stack can be made for each variable independently
    for variable, nrebin, axis, unit, y_min in variable_list:
        #create a canvas for plotting
        #since we want a kinetic histo and a ratio plot, make 2 pads
        c = TCanvas("c", "c", 800, 900)
        histoPad = TPad("histoPad", "histoPad", 0, .25, 1, 1) #name, title, x low, y low, x high, y high
        ratioPad = TPad("ratioPad", "ratioPad", 0, .05, 1, .25)

        #set left and right margins of the pads so that the legend will fit properly (MUST DO FOR EACH PAD)
        """
        maybe make a for loop over all the pads in canvas to do this better
        """
        histoPad.SetRightMargin(Right_margin)
        histoPad.SetLeftMargin(Left_margin)

        ratioPad.SetTopMargin(0.05)
        ratioPad.SetRightMargin(Right_margin)
        ratioPad.SetLeftMargin(Left_margin)
        #ratioPad.SetBottomMargin(.01)

        histoPad.Draw()
        ratioPad.Draw()

        #we want to draw the histogram and all associated objects to histoPad, so make sure you are in the right pad
        histoPad.cd()

        
        #initialize legend here so that you can add entries to it as you add entries to the canvas
        legend = TLegend(.801, .1, .999, .9 ,"","brNDC")  #.901, .1, .999, .9  or 0.62,0.5,.87,.88,
       

        #initialize THStacks for each of the variabels you've plotted so each variable has it's own stack, of name "variable_stack"
        cmd_stack  = "%s = THStack(\"%s\", \" \")" %(variable +"_stack", variable + "_stack")
        exec(cmd_stack)


        
       
        #check for rebin request and complete if necessary
        if nrebin != 0:
            for hist_name in h_list:
                if hist_name.find(variable) != -1:
                    all_histos.cd()
                    h = all_histos.Get(hist_name)
                    h.Rebin(nrebin)
                   
        
        
        
        #for loop to fill THStack and draw it to the canvas
        for hist_name in h_list:
            all_histos.cd()
            h = all_histos.Get(hist_name)
            
            
            #this loop "grabs" the proper title from the chain_list so that it can be given to the addLegend command and show up as expected in the legend
            if hist_name.find(variable) != -1:

                for chain, file_name, color, title in chain_list:
                        if hist_name.find(chain) != -1:
                            legend_name = title

        
                #since different variables are used to differentiate for different things, the stacks are compose differently 
                if (variable  == "massjj" or variable == "deltajj" or variable == "D" or variable == "mass4l"):
                    if hist_name.find("data_2016") == -1 and hist_name.find("mz") == -1 and hist_name.find("VBF") == -1:
                        all_histos.cd()
                        cmd_add = "%s_stack.Add(%s)" % (variable, hist_name)
                        exec(cmd_add)
                        cmd_addLegend = "legend.AddEntry(h, \"%s\")" %legend_name
                        exec(cmd_addLegend)
              
                    
                   

                if (variable == "pfmet" or variable == "pt4l"):
                    #this if statement chooses all histograms EXCEPT the data and models, and then stacks the remaining histos together
                    if hist_name.find("data_2016") == -1 and hist_name.find("mz") == -1:
                        all_histos.cd()
                        cmd_add = "%s_stack.Add(%s)" % (variable, hist_name)
                        exec(cmd_add)
                        cmd_addLegend = "legend.AddEntry(h, \"%s\")" %legend_name
                        exec(cmd_addLegend)

     
        #must draw stacks to the canvas before the models and data are drawn
        histoPad.cd()
        cmd_drawS = "%s_stack.Draw(\"%s\")" %(variable, stack_draw_options)   #use option hist in Drraw() to draw in histogram mode 
        exec(cmd_drawS)

        #for loop to draw the data and models to the same canvas as the THStack
        for hist_name in h_list:
            if hist_name.find(variable) != -1:

                #additional loop through the chain list (which contains the legend titles), assigning the "legend_name" variable to the desired value        
                for chain, file_name, color, title in chain_list:
                        if hist_name.find(chain) != -1:
                            legend_name = title
                            
                all_histos.cd()
                h = all_histos.Get(hist_name)

                #draws the data
                if hist_name.find("data_2016") != -1:
                        cmd_drawDot = "%s.Draw(\"%s\")" % (hist_name, data_draw_options)
                        exec(cmd_drawDot)
                        cmd_addLegend = "legend.AddEntry(h, \"%s\")" %legend_name
                        exec(cmd_addLegend)

                #for massjj, deltajj, D, mass4l, want to differentiate between VBF and bkg
                if (variable  == "massjj" or variable == "deltajj" or variable == "D" or variable == "mass4l"):
                       
                     #draws VBF data
                    if hist_name.find("VBF") != -1:
                            cmd_drawLine = "%s.Draw(\"%s\")" % (hist_name, model_draw_options)
                            exec(cmd_drawLine)
                            cmd_addLegend = "legend.AddEntry(h, \"%s\")" %legend_name
                            exec(cmd_addLegend)
                         
                            

                #for pfmet and pt4l, want to differentialte between all bkg and models    
                if (variable == "pfmet" or variable == "pt4l"):
                
                    #draws every model (marked with mz in the title)
                    if hist_name.find("mz") != -1:
                        cmd_drawLine = "%s.Draw(\"%s\")" % (hist_name, model_draw_options)
                        exec(cmd_drawLine)
                        cmd_addLegend = "legend.AddEntry(h, \"%s\")" %legend_name
                        exec(cmd_addLegend)
                         


       
        #set axis titles
        cmd_Xaxis = "%s_stack.GetXaxis().SetTitle(\"%s (%s)\")" % (variable, axis, unit)
        exec(cmd_Xaxis)
        
        events_per_bin = eval("getPerBin(%s, nrebin)" % (variable+ "_stack"))

        cmd_Yaxis = "%s_stack.GetYaxis().SetTitle(\"Events/ %s %s\")" % (variable, str(events_per_bin), unit)
        exec(cmd_Yaxis)

        #run the getYmax function and store the max value in global_max
        cmd_getYmax = "global_max = getYmax(\"%s\", h_list, all_histos)" % variable
        exec(cmd_getYmax)

        #set the maximum Y value to global_max
        cmd_setYmax = "%s_stack.SetMaximum(global_max *1.10)" %variable
        exec(cmd_setYmax)

        if bool(y_min) == True:
            cmd_setYmin = "%s_stack.SetMinimum(%s)" %(variable, str(y_min))
            exec(cmd_setYmin)


#----------------------------------------------------------------STEP 6: Make ratio plots of Data/MC ----------------------------------------------------------------

        #move into working in the ratio pad
        ratioPad.cd()
        ratioPad.SetTicks(1,1)
        

        
        all_histos.cd()
        cmd_getHdata = "h_data = all_histos.Get(\"data_2016_%s\")" %variable
        exec(cmd_getHdata)

        hSum_xmin = h_data.GetXaxis().GetXmin()
        hSum_xmax = h_data.GetXaxis().GetXmax()
        hSum_bins = h_data.GetNbinsX()
        
        h_sum= TH1F("h_sum ", "h_sum ", hSum_bins, hSum_xmin, hSum_xmax)
        cmd_merge = "h_sum.Merge(%s_stack.GetHists())"%variable
        exec(cmd_merge)

        h_ratio = h_data.Clone()
        
        h_ratio.Divide(h_sum)
        h_ratio.SetMarkerStyle(20)
        h_ratio.SetMarkerColor(kBlack)
        h_ratio.SetStats(0)
        h_ratio.SetMaximum(4)
        h_ratio.GetXaxis().SetTitleOffset(.2)
        h_ratio.GetYaxis().SetTitleOffset(.2)
        h_ratio.GetXaxis().SetLabelSize(.07)
        h_ratio.GetYaxis().SetLabelSize(.07)
        h_ratio.GetXaxis().SetTitleSize(.13)
        h_ratio.GetYaxis().SetTitleSize(.15)
        h_ratio.SetTitle("; ; Data/MC")
        h_ratio.Draw(data_draw_options)

        h_sum.Delete()

#----------------------------------------------------------------STEP 7: Format the canvas and pads (create legend, text, etc), save to file ---------------------------

        #change back to working with the histoPad 
        histoPad.cd()
        
        #set canvas to log scale on the Y axis and set useful tick markings
        histoPad.SetLogy(log_setY)
        histoPad.SetLogx(log_setX)
        histoPad.SetTicks(1,1)
 
        #add the text information to the canvas, such as experiement information (L_int, sqrt(s), CMS, etc)
        cms_name = TPaveText(0.08, 0.902, 0.80, 0.95, "NDC")
        cms_name.SetTextSize(0.03)
        cms_name.SetTextFont(42)
        cms_name.SetFillColor(0)
        cms_name.SetBorderSize(0)
        cms_name.SetMargin(0.001)
        cms_name.SetTextAlign(12) #align left
        cms_name.AddText(0.01,0.5,cms_prelim_txt)
        cms_name.AddText(0.65, 0.6, data_set_info);
        cms_name.Draw()


        #automatically builds legend based on all the histograms in the class, difficult to change format of legend but is decent 
        #c.BuildLegend(.750, .5, .90, .90, "Legend")

    
        #for a more advanced and professionally formatted legend, adjust here
      
        legend.SetTextSize(0.02)
        legend.SetLineColor(0)
        legend.SetLineWidth(1)
        legend.SetFillColor(kWhite)
        legend.SetBorderSize(0)

        legend.Draw("FLP")
        
        
        #prints the histograms to the screen, optional if you do not want to see the histos
 
        c.Update()    
        gSystem.ProcessEvents()
        sleep(sleep_time)


        #save the final plots (on their canvas) as both .root and .pdf files 
        cmd_saveRoot = "c.SaveAs(\"%s_plot.root\")" %( variable)
        exec(cmd_saveRoot)
        cmd_savePDF = "c.SaveAs(\"%s_plot.pdf\")" %( variable)
        exec(cmd_savePDF)
try:
    main()
except KeyboardInterrupt:
    print("Keyboard Interrupt")


