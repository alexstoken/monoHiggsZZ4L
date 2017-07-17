#!/usr/bin/env python
#--------------------------------
"""
this program will create TChains, run a MakeClass macro on those TChains, and then produce a TStack from the histograms output from the MakeClass
"""

import os, sys, re
from ROOT import *
from string import *
from time import sleep 


#runs makeClass called muAnalsis.C on the Tchain features, passes in the chain and the chain's title
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

def main():
    
#-------------------------------------------------------STEP 1: create TChains for the different typed of background and signal we will be plotting, pick variables to plot ----------------------------

    #create a list of the different variables you want to plot (see muAnalysis to see which variables have been filled)

    #list is in the format (variable, n_rebins desired)
    variable_list = [ ("massjj", 2), ("deltajj", 2), ("D", 2), ("mass4l", 2),("pt4l", 2), ("pfmet", 2)]
    """TODO: create a way to send to makeClass which variables to plot from python script"""


    #create list of all the types of physics objects (data, types of backgrounds, models, etc) you intend to plot

    #this list has tuples in the format (chain title, files chain is produced from, color for plotting)

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
        ("WH", "output_*_*HWJ*", kOrange +2, "WH, m_{H} =125 GeV/c^2"),
        ("ZH", "output_*_*HZJ*", kOrange -1 , "ZH, m_{H} =125 GeV/c^2"),
        ("VBF","output_*_VBF*" , kOrange -6, "VBF, m_{H} =125 GeV/c^2"),
        ("ttH","output_*_ttH*" , kOrange, "ttH"),
        ("ggH", "output_*_GluGluHToZZTo4L*", kOrange -3, "ggH, m_{H} =125 GeV/c^2"),
        ("mzChi1", "output_*_MChi-1_*", kBlue+2, "Z_p to m_{Chi}"),
        ("ZZ", "output_*_ZZTo*", kCyan -7, "ZZ"),
        ("ggToZZ", "output_*_GluGluToContinToZZT*", kCyan -5, "ggToZZ"),
        ("mz600","output_*_Zprime*600*" , kGreen -4, "m_{z} = 600 GeV/c^2, m_{A_{0}} = 300 GeV/c^2"),
        ("mz800","output_*_Zprime*800*" , kBlue -4, "m_{z} = 800 GeV/c^2, m_{A_{0}} = 300 GeV/c^2"),
        ("mz1","output_*_Zprime*1000*" , kRed -4 , "m_{z} = 1 TeV/c^2, m_{A_{0}} = 300 GeV/c^2"),
        ("mz12","output_*_Zprime*1200*" , kOrange -3, "m_{z} = 1.2 TeV/c^2, m_{A_{0}} = 300 GeV/c^2"),
        ("mz14","output_*_Zprime*1400*" , kBlack, "m_{z} = 1.4 TeV/c^2, m_{A_{0}} = 300 GeV/c^2"),
        ("mz17","output_*_Zprime*1700*" , kCyan, "m_{z} = 1.7 TeV/c^2, m_{A_{0}} = 300 GeV/c^2")
        ]

    #note treename, same for all files (MUST BE CHANGED FOR A DIFFERENT ANALYSIS)
    treename = "HZZ4LeptonsAnalysisReduced"

    number_of_events = open("event_counts.txt", "w+")
    number_of_events.write("Bkg/Signal Type       # of Entries \n")
    number_of_events.close()
    
    #loop over the list of objects and create an empty TChain with that object name
    #add the proper trees to the chains using their file names and then run the makeClass on the chains to fill histograms for the variables in question
    for chain, file_name, color, title in chain_list:
        cmd_newChain = "%s = TChain(treename, \"%s\")" % (chain, chain)
       
        cmd_addChain = "x = %s.Add(\"%s\")" % (chain, file_name)
      
        cmd_run = "run(%s)" %chain
        
        exec(cmd_newChain)
        exec(cmd_addChain)
        exec(cmd_run)
#----------------------------------------------------------------STEP 2: Count the events in each physics object for each plot, print out to a file -------------------------------------------------
        #Move to working in the file
        number_of_events = open("event_counts.txt", "a")
        
        entries = eval("%s.GetEntries()" %chain)
        number_of_events.write("%s = %s  \n" % (chain, str(entries)))
        
        
        #print "Number of files in" + chain + " chain = " + str(x)       OPTIONAL STATEMENT TO PRINT THE NUMBER OF FILES ADDED TO THE CHAIN

 
        
#-------------------------------------------------------STEP 3: retrieve all histograms created by makeClass and put them in one file with hadd-------------------------------------

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
        


 #-----------------------------------------------------------------------------STEP 4: Style the histograms --------------------------------------------------------------------------

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

              #BE CAREFUL THAT FIND COMMAND WILL FIND THE CORRECT, UNIQUE MATCH

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

                  elif chain_title.find("VBF")!= -1 and (hist_name.find("massjj") != -1 or hist_name.find("deltajj") != -1 or hist_name.find("D") != -1):
                      h.SetLineWidth(2)
                      exec(cmd_Linecolor)

                  else:
                      #backgrounds are drawn as filled histograms
                      h.SetFillStyle(1001)
                      #h.SetLineColor(kBlack)
                      exec(cmd_Linecolor)
                      exec(cmd_Fillcolor)
                      
    
    
#--------------------------STEP 5: Add histos to stacks, Draw the histograms into canvases and modift histogram properties (axis titles, axis limits, rebin etc) ----------

    #loop over each variable you want to plot, so that a stack can be made for each variable independently
    for variable, nrebin in variable_list:
        #create a canvas to plot all the variable info 
        c = TCanvas()
       

        #initialize legend here so that you can add entries to it as you add entries to the canvas
        legend = TLegend(0.901,0.1,1,.9, "","brNDC")
       

        #initialize THStacks for each of the variabels you've plotted so each variable has it's own stack, of name "variable_stack"
        cmd_stack  = "%s = THStack(\"%s\", \"%s\")" %(variable +"_stack", variable + "_stack", variable + "_stack")
        exec(cmd_stack)


        all_histos.cd()
       
        #check for rebin request and complete if necessary
        if nrebin != 0:
            for hist_name in h_list:
                if hist_name.find(variable) != -1:
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

     
        #must draw stacks to the canvas before models
        c.cd()             
        cmd_drawS = "%s_stack.Draw(\"hist\")" %variable   #use option hist in draw to draw in histogram mode 
        exec(cmd_drawS)

        #set axis titles
        cmd_Xaxis = "%s_stack.GetXaxis().SetTitle(\"%s\")" % (variable, variable)
        cmd_Yaxis = "%s_stack.GetYaxis().SetTitle(\"Events\")" % (variable)
        #cmd_Yaxis = "%s_stack.GetYaxis().SetTitle(\"Events/%s GeV\")" % (variable, str(10))
        exec(cmd_Xaxis)
        exec(cmd_Yaxis)

        
        #for loop to draw the data and models to the same canvas as the THStack
        for hist_name in h_list:
            if hist_name.find(variable) != -1:

                for chain, file_name, color, title in chain_list:
                        if hist_name.find(chain) != -1:
                            legend_name = title


                            
                all_histos.cd()
                h = all_histos.Get(hist_name)

                

                if (variable  == "massjj" or variable == "deltajj" or variable == "D" or variable == "mass4l"):
                    if hist_name.find("data_2016") != -1:
                        cmd_drawD = "%s.Draw(\"hist same E1PX0\")" % (hist_name)
                        exec(cmd_drawD)
                        cmd_addLegend = "legend.AddEntry(h, \"%s\")" %legend_name
                        exec(cmd_addLegend)
                        
                        #draws VBF data
                    if hist_name.find("VBF") != -1:
                            cmd_drawVBF = "%s.Draw(\"hist same\")" % (hist_name)
                            exec(cmd_drawVBF)
                            cmd_addLegend = "legend.AddEntry(h, \"%s\")" %legend_name
                            exec(cmd_addLegend)
                            

                    
                if (variable == "pfmet" or variable == "pt4l"):
                    #draws the data
                    if hist_name.find("data_2016") != -1:
                        cmd_drawD = "%s.Draw(\"hist same PX0\")" % (hist_name)
                        exec(cmd_drawD)
                        cmd_addLegend = "legend.AddEntry(h, \"%s\")" %legend_name
                        exec(cmd_addLegend)

                    #draws every model (marked with mz in the title)
                    if hist_name.find("mz") != -1:
                        cmd_drawM = "%s.Draw(\"hist same\")" % (hist_name)
                        exec(cmd_drawM)
                        cmd_addLegend = "legend.AddEntry(h, \"%s\")" %legend_name
                        exec(cmd_addLegend)



        #run the getYmax function and store the max value in global_max
        cmd_getYmax = "global_max = getYmax(\"%s\", h_list, all_histos)" % variable
        exec(cmd_getYmax)

        #set the maximum Y value to global_max
        cmd_setYmax = "%s_stack.SetMaximum(global_max *1.10)" %variable
        exec(cmd_setYmax)



#----------------------------------------------------------------STEP 6: Format the canvas (create legend, text, etc), save to file --------------------------------------------------

        #change back to working with the canvas
        c.cd()
       
        #set canvas to log scale on the Y axis and set useful tick markings
        c.SetLogy(1)
        c.SetTicks(1,1)
       
        
 
        #add the text information to the canvas, such as experiement information (L_int, sqrt(s), CMS, etc)
        cms_name = TPaveText(0.15, 0.901, 0.95, 0.99, "NDC")
        cms_name.SetTextSize(0.03)
        cms_name.SetTextFont(42)
        cms_name.SetFillColor(0)
        cms_name.SetBorderSize(0)
        cms_name.SetMargin(0.01)
        cms_name.SetTextAlign(12) #align left
        cms_prelim_txt = "CMS Preliminary"
        cms_name.AddText(0.01,0.5,cms_prelim_txt)
        data_set_info = "#sqrt{s} = 13 TeV, L = 35,867 fb^{-1}" 
        cms_name.AddText(0.65, 0.6, data_set_info);
        cms_name.Draw()


        #automatically builds legend based on all the histograms in the class, difficult to change format of legend but is decent 
        #c.BuildLegend(.750, .5, .90, .90, "Legend")

    
        #for a more advanced and professionally formatted legend, adjust here
      
        legend.SetTextSize(0.040)
        legend.SetLineColor(0)
        legend.SetLineWidth(1)
        legend.SetFillColor(kWhite)
        legend.SetBorderSize(0)

        legend.Draw("FLP")
        
        
        #prints the histograms to the screen, optional if you do not want to see the histos
        c.SetCanvasSize(700, 700)
        c.SetWindowSize(800, 800)
        c.Update()    
        gSystem.ProcessEvents()
        sleep(1)


        #save the final plots (on their canvas) as both .root and .pdf files 
        cmd_saveRoot = "c.SaveAs(\"%s_plot.root\")" %( variable)
        exec(cmd_saveRoot)
        cmd_savePDF = "c.SaveAs(\"%s_plot.pdf\")" %( variable)
        exec(cmd_savePDF)
try:
    main()
except KeyboardInterrupt:
    print("Keyboard Interrupt")


