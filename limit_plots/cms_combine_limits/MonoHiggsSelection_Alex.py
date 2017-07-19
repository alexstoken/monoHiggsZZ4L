#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  File:        MonoHiggsSelection.py
#  Usage:       python MonoHiggsSelection.py --channel 4mu
#  Description: Apply optimized event selection, including various machine learning
#               algorithm testing, printing out event yields and writing shape histograms
#               to a file for limit setting.
#  Created:     9-Feb-2017 Dustin Burns
# -----------------------------------------------------------------------------
from ROOT import *
import numpy as np
import math
import argparse

# Convert ROOT TNtuple data structure to Python arrays
def get_data(f):
  f = TFile.Open(f)
  t = f.Get("HZZ4LeptonsAnalysisReduced")
  weight = []
  pfmet  = []
  mass4l = []
  mT     = []
  dphi   = []
  Dkin   = []
  cat    = []
  Ngood  = []
  Nbjets = []
  dphi_min    = []
  dphi_min_pt = []
  dphi_max    = []
  dphi_max_pt = []
  lept1_pt = []
  lept2_pt = []
  lept3_pt = []
  lept4_pt = []
  lept1_eta = []
  lept2_eta = []
  lept3_eta = []
  lept4_eta = []
  lept1_phi = []
  lept2_phi = []
  lept3_phi = []
  lept4_phi = []
  Z1mass = []
  Z2mass = []
  pt4l = []
  eta4l = []
  for evt in t:
    weight.append(evt.f_weight)
    pfmet .append(evt.f_pfmet)
    mass4l.append(evt.f_mass4l)
    mT    .append(evt.f_mT)
    dphi  .append(evt.f_dphi)
    Dkin  .append(evt.f_D_bkg_kin)
    cat   .append(evt.f_category)
    Ngood .append(evt.f_Ngood)
    Nbjets.append(evt.f_Nbjets)
    #dphi_min.append(evt.f_min_dphi_jet_met)
    #dphi_min_pt.append(evt.f_min_dphi_jet_pt)
    #dphi_max.append(evt.f_max_dphi_jet_met)
    #dphi_max_pt.append(evt.f_max_dphi_jet_pt)
    lept1_pt.append(evt.f_lept1_pt)
    lept2_pt.append(evt.f_lept2_pt)
    lept3_pt.append(evt.f_lept3_pt)
    lept4_pt.append(evt.f_lept4_pt)
    lept1_eta.append(evt.f_lept1_eta)
    lept2_eta.append(evt.f_lept2_eta)
    lept3_eta.append(evt.f_lept3_eta)
    lept4_eta.append(evt.f_lept4_eta)
    lept1_phi.append(evt.f_lept1_phi)
    lept2_phi.append(evt.f_lept2_phi)
    lept3_phi.append(evt.f_lept3_phi)
    lept4_phi.append(evt.f_lept4_phi)
    Z1mass.append(evt.f_Z1mass)
    Z2mass.append(evt.f_Z2mass)
    pt4l.append(evt.f_pt4l)
    eta4l.append(evt.f_eta4l)
  f.Close()
  return (weight, pfmet, mass4l, mT, dphi, Dkin, cat, Ngood, Nbjets, dphi_min, dphi_min_pt, dphi_max, dphi_max_pt, lept1_pt, lept2_pt, lept3_pt, lept4_pt, lept1_eta, lept2_eta, lept3_eta, lept4_eta, lept1_phi, lept2_phi, lept3_phi, lept4_phi, Z1mass, Z2mass, pt4l, eta4l)

if __name__ == "__main__":
 
  # Parse command line arguments
  parser = argparse.ArgumentParser()
  parser.add_argument('--channel', required=True, help='Decay channel: 4mu, 4e, or 2e2mu')
  args = parser.parse_args()

  # Read in list of data and simulation files
  flist = map(lambda x: x.split()[-1], open('filelist_' + args.channel + '_2016_Spring16_AN_Bari_miniaod.txt').readlines())

  
  ''' 
  w = 0
  w2 = 0
  N = 0
  # calculate average and std of event weights
  for f in flist:
    # Get Data
    ft = TFile.Open(f)
    t = ft.Get("HZZ4LeptonsAnalysisReduced")
    weight, pfmet, mass4l, mT, dphi, Dkin, cat, Ngood, Nbjets, dphi_min, dphi_min_pt, dphi_max, dphi_max_pt, lept1_pt, lept2_pt, lept3_pt, lept4_pt, lept1_eta, lept2_eta, lept3_eta, lept4_eta, lept1_phi, lept2_phi, lept3_phi, lept4_phi, Z1mass, Z2mass, pt4l, eta4l = get_data(f)
    ft.Close()

    if 'MZp' not in f and 'Run2016' not in f:
      N += len(weight)
      w += sum(weight)
      w2 += sum(x**2 for x in weight)

  w = w/N
  w2 = w2/N
  w2 = math.sqrt(w2-w**2)
  print N
  print str(w) + ' +/- ' + str(w2)
  '''

  # Load machine learning algorithm to test on events     
  #record = open('Dmass4l.cpp').read() # Neural network, inputs: mass4l, Dkin
  #record = open('Dm4lmet.cpp').read() # Neural network, inputs: mass4l, pfmet
  #record = open('m4lmelamet_BNN.cc').read() # Neural network, inputs: mass4l, Dkin, pfmet
  record = open('m4lmelamet_BDT.cc').read() # Boosted decision tree, inputs: mass4l, Dkin, pfmet
  #record = open('m4lmelametngoodnbjets.cc').read() # Boosted decision tree, inputs: mass4l, Dkin, pfmet, Ngood, Nbjets
  #record = open('m4lmelamet_MLP.cc').read() # Multilayer perceptron, inputs: mass4l, Dkin, pfmet
  #record = open('m4lmelamet_JETNET.cc').read() # JETNET algorithm, inputs: mass4l, Dkin, pfmet
  gROOT.ProcessLine(record)

  # Book histograms for shape analysis
  h0pfmet_D    = TH1F("h0pfmet_D", "", 1000, 0, 1600)
  h1pfmet_D    = TH1F("h1pfmet_D", "", 1000, 0, 1600)
  h1D_D        = TH1F("h1D_D", "", 1000, -1.1, 1.1)
  h0pfmet_D.Sumw2()
  h1pfmet_D.Sumw2()
  h1D_D.Sumw2()
  h1pfmet_WH   = TH1F("WH", "WH", 1000, 0, 1600)
  h1D_WH       = TH1F("WH", "WH", 1000, -1.1, 1.1)
  h1pfmet_WH.Sumw2()
  h1D_WH.Sumw2()
  h1pfmet_ZH   = TH1F("ZH", "ZH", 1000, 0, 1600)
  h1D_ZH       = TH1F("ZH", "ZH", 1000, -1.1, 1.1)
  h1pfmet_ZH.Sumw2()
  h1D_ZH.Sumw2()
  h1pfmet_ggH  = TH1F("ggH", "ggH", 1000, 0, 1600)
  h1D_ggH      = TH1F("ggH", "ggH", 1000, -1.1, 1.1)
  h1pfmet_ggH.Sumw2()
  h1D_ggH.Sumw2()
  h1pfmet_qqH  = TH1F("qqH", "qqH", 1000, 0, 1600)
  h1D_qqH      = TH1F("qqH", "qqH", 1000, -1.1, 1.1)
  h1pfmet_qqH.Sumw2()
  h1D_qqH.Sumw2()
  h1pfmet_ttH  = TH1F("ttH", "ttH", 1000, 0, 1600)
  h1D_ttH      = TH1F("ttH", "ttH", 1000, -1.1, 1.1)
  h1pfmet_ttH.Sumw2()
  h1D_ttH.Sumw2()
  h1pfmet_ggZZ = TH1F("ggZZ", "ggZZ", 1000, 0, 1600)
  h1D_ggZZ     = TH1F("ggZZ", "ggZZ", 1000, -1.1, 1.1)
  h1pfmet_ggZZ.Sumw2()
  h1D_ggZZ.Sumw2()
  h1pfmet_qqZZ = TH1F("qqZZ", "qqZZ", 1000, 0, 1600)
  h1D_qqZZ     = TH1F("qqZZ", "qqZZ", 1000, -1.1, 1.1)
  h1pfmet_qqZZ.Sumw2()
  h1D_qqZZ.Sumw2()
  h1pfmet_VVV = TH1F("VVV", "VVV", 1000, 0, 1600)
  h1D_VVV     = TH1F("VVV", "VVV", 1000, -1.1, 1.1)
  h1pfmet_VVV.Sumw2()
  h1D_VVV.Sumw2()
  h1pfmet_TTV = TH1F("TTV", "TTV", 1000, 0, 1600)
  h1D_TTV     = TH1F("TTV", "TTV", 1000, -1.1, 1.1)
  h1pfmet_TTV.Sumw2()
  h1D_TTV.Sumw2()
  h1pfmet_ZX   = TH1F("ZX", "ZX", 1000, 0, 1600)
  h1D_ZX       = TH1F("ZX", "ZX", 1000, -1.1, 1.1)
  h1pfmet_ZX.Sumw2()
  h1D_ZX.Sumw2()

  # Loop through input files, testing machine learning algorithm and applying signal region selection
  for f in flist:
    print f
    # Get Data
    weight, pfmet, mass4l, mT, dphi, Dkin, cat, Ngood, Nbjets, dphi_min, dphi_min_pt, dphi_max, dphi_max_pt, lept1_pt, lept2_pt, lept3_pt, lept4_pt, lept1_eta, lept2_eta, lept3_eta, lept4_eta, lept1_phi, lept2_phi, lept3_phi, lept4_phi, Z1mass, Z2mass, pt4l, eta4l = get_data(f)

    # Book histograms for Monte Carlo simulation samples
    h0pfmet = TH1F("h0pfmet", "", 1000, 0, 1000)
    h1pfmet = TH1F("h1pfmet", "", 1000, 0, 1000)
    h1D     = TH1F("h1D", "", 1000, -1.1, 1.1)
    h0pfmet.Sumw2()
    h1pfmet.Sumw2()
    h1D.Sumw2()
    h1lept1_pt = TH1F("h1lept1_pt", "", 1000, 0, 1000)
    h1lept2_pt = TH1F("h1lept2_pt", "", 1000, 0, 1000)
    h1lept3_pt = TH1F("h1lept3_pt", "", 1000, 0, 1000)
    h1lept4_pt = TH1F("h1lept4_pt", "", 1000, 0, 1000)
    h1lept1_eta = TH1F("h1lept1_pt", "", 100, -5, 5)
    h1lept2_eta = TH1F("h1lept2_pt", "", 100, -5, 5)
    h1lept3_eta = TH1F("h1lept3_pt", "", 100, -5, 5)
    h1lept4_eta = TH1F("h1lept4_pt", "", 100, -5, 5)
    h1lept1_phi = TH1F("h1lept1_phi", "", 100, -5, 5)
    h1lept2_phi = TH1F("h1lept2_phi", "", 100, -5, 5)
    h1lept3_phi = TH1F("h1lept3_phi", "", 100, -5, 5)
    h1lept4_phi = TH1F("h1lept4_phi", "", 100, -5, 5)
    h1Z1mass = TH1F("h1Z1mass", "", 1000, 0, 1000)
    h1Z2mass = TH1F("h1Z2mass", "", 1000, 0, 1000)
    h1pt4l = TH1F("h1pt4l", "", 1000, 0, 1000)
    h1eta4l = TH1F("h1eta4l", "", 100, -5, 5)
    h1Ngood = TH1F("h1Ngood", "", 10, 0, 10)
    h1Nbjets = TH1F("h1Nbjets", "", 10, 0, 10)
    h1mass4l = TH1F("h1mass4l", "", 1000, 0, 1000)
    
    # Apply selection, filling histograms before and after
    for i in range(0, len(weight)):

      # Weight cleaning
      #if weight[i] > w + 4*w2 and 'Run2016' not in f: continue
      #if weight[i] > 0.0010696932315 + 4*0.0163535896171 and 'Run2016' not in f: continue
      # 0.0010696932315 +/- 0.0163535896171
     
      # Step 0: Standard Model Higgs search selection
      h0pfmet.Fill(pfmet[i], weight[i])
      if 'Run2016' in f: 
        h0pfmet_D.Fill(pfmet[i], weight[i])
      
      # Step 1: MonoHiggs selection
      if Ngood[i] != 4: continue
      if Nbjets[i] > 1: continue
      if pfmet[i] < 60: continue
      if np.abs(mass4l[i] - 125) > 10: continue
      #if mass4l[i] < 118: continue
      #if mass4l[i] > 130: continue
      #print m4lmelamet(mass4l[i], Dkin[i], pfmet[i])
      #if m4lmelamet(mass4l[i], Dkin[i], pfmet[i]) < -0.9: continue
      #if Dm4lmet(mass4l[i], pfmet[i], 0, 199) < 0.999: continue
      #if dphi_min_pt[i] > 50 and dphi_min[i] < 0.5: continue
      #if dphi_max_pt[i] > 50 and dphi_max[i] > 2.7: continue

      D = m4lmelamet(mass4l[i], Dkin[i], pfmet[i])
      h1pfmet.Fill(pfmet[i], weight[i])
      h1D.Fill(D)
      #h1D.Fill(m4lmelametngoodnbjets(mass4l[i], Dkin[i], pfmet[i], Ngood[i], Nbjets[i]), weight[i])
      h1lept1_pt.Fill(lept1_pt[i], weight[i]) 
      h1lept2_pt .Fill(lept2_pt[i], weight[i])
      h1lept3_pt .Fill(lept3_pt[i], weight[i])
      h1lept4_pt .Fill(lept4_pt[i], weight[i])
      h1lept1_eta .Fill(lept1_eta[i], weight[i])
      h1lept2_eta .Fill(lept2_eta[i], weight[i])
      h1lept3_eta .Fill(lept3_eta[i], weight[i])
      h1lept4_eta .Fill(lept4_eta[i], weight[i])
      h1lept1_phi .Fill(lept1_phi[i], weight[i])
      h1lept2_phi .Fill(lept2_phi[i], weight[i])
      h1lept3_phi .Fill(lept3_phi[i], weight[i])
      h1lept4_phi .Fill(lept4_phi[i], weight[i])
      h1Z1mass .Fill(Z1mass[i], weight[i])
      h1Z2mass .Fill(Z2mass[i], weight[i])
      h1pt4l .Fill(pt4l[i], weight[i])
      h1eta4l .Fill(eta4l[i], weight[i])
      h1Ngood .Fill(Ngood[i], weight[i])
      h1Nbjets .Fill(Nbjets[i], weight[i])
      h1mass4l.Fill(mass4l[i], weight[i])


      if 'Run2016' in f: 
        h1pfmet_D.Fill(pfmet[i], weight[i])
        h1D_D.Fill(D, weight[i])
        #h1D_D.Fill(m4lmelametngoodnbjets(mass4l[i], Dkin[i], pfmet[i], Ngood[i], Nbjets[i]), weight[i])
      elif 'WminusH' in f or 'WplusH' in f:
        h1pfmet_WH.Fill(pfmet[i], weight[i])
        h1D_WH.Fill(D, weight[i])
      elif 'ZH' in f:
        h1pfmet_ZH.Fill(pfmet[i], weight[i])
        h1D_ZH.Fill(D, weight[i])
      elif 'GluGluHToZZTo4L' in f:
        h1pfmet_ggH.Fill(pfmet[i], weight[i])
        h1D_ggH.Fill(D, weight[i])
      elif 'VBF_HToZZTo4L' in f:
        h1pfmet_qqH.Fill(pfmet[i], weight[i])
        h1D_qqH.Fill(D, weight[i])
      elif 'ttH' in f:
        h1pfmet_ttH.Fill(pfmet[i], weight[i])
        h1D_ttH.Fill(D, weight[i])
      elif 'GluGluToZZ' in f or 'GluGluToContin' in f:
        h1pfmet_ggZZ.Fill(pfmet[i], weight[i])
        h1D_ggZZ.Fill(D, weight[i])
      elif '_ZZTo4L' in f:
        h1pfmet_qqZZ.Fill(pfmet[i], weight[i])
        h1D_qqZZ.Fill(D, weight[i])
      elif 'ZZZ' in f or 'WZZ' in f or 'WWZ' in f:
        h1pfmet_VVV.Fill(pfmet[i], weight[i])
        h1D_VVV.Fill(D, weight[i])
      elif 'TTW' in f or 'TTZ' in f:
        h1pfmet_TTV.Fill(pfmet[i], weight[i])
        h1D_TTV.Fill(D, weight[i])
      elif 'WZ' in f or 'WW' in f or 'WJets' in f or 'TT' in f or 'QCD' in f or 'DYJets' in f:
        #print f
        h1pfmet_ZX.Fill(pfmet[i], weight[i])
        h1D_ZX.Fill(D, weight[i])

    # Print yields  
    err2 = 0;
    for i in range(0, h1pfmet.GetXaxis().GetNbins()):
      err2 += h1pfmet.GetBinError(i)**2;
    #print 'Sample name ' + args.channel + 'channel: ' + f + ' N Entries: ' + str(h1D.GetEntries()) + ' Yield: ' + str(h1D.Integral()) + ' Error: ' + str(math.sqrt(err2))
    print 'Sample name ' + args.channel + 'channel: ' + f + ' N Entries: ' + str(h1pfmet.GetEntries()) + ' Yield: ' + str(h1pfmet.Integral()) + ' Error: ' + str(math.sqrt(err2))
  
    # Write shape histogram to file for Monte Carlo samples
    nRebin = 1
    fs = TFile('datacards_' + args.channel + '/f' + args.channel + '.root', 'UPDATE')
    if (not fs.FindKey('bin' + args.channel)):  d = fs.mkdir('bin' + args.channel)
    #hs = h1D
    hs = h1pfmet
    name = f.split('histos_all/')[1].split('.root')[0]
    print name
    #name = f.split('_25ns/')[1].split('.root')[0]
    hs.SetName(name)
    hs_rebin = hs.Rebin(nRebin, name)
    #for k in range(0, hs_rebin.GetNbinsX()):
    #  if (hs_rebin.GetBinContent(k) == 0): hs_rebin.SetBinContent(k, 1E-8)
    fs.cd('bin' + args.channel)
    hs_rebin.Write(name)
    fs.Close()

    # Write "re-reduced" files for plotting after monoH selection
    fout = TFile('plots/AN/rereduced_total/plots_' + f.split('histos_all/')[1], 'recreate')
    h1pfmet.Write('hmet_CR')
    h1D.Write('hD_CR')
    h1lept1_pt .Write('hlept1_pt_CR')
    h1lept2_pt .Write('hlept2_pt_CR')
    h1lept3_pt .Write('hlept3_pt_CR')
    h1lept4_pt .Write('hlept4_pt_CR')
    h1lept1_eta .Write('hlept1_eta_CR')
    h1lept2_eta .Write('hlept2_eta_CR')
    h1lept3_eta .Write('hlept3_eta_CR')
    h1lept4_eta .Write('hlept4_eta_CR')
    h1lept1_phi .Write('hlept1_phi_CR')
    h1lept2_phi .Write('hlept2_phi_CR')
    h1lept3_phi .Write('hlept3_phi_CR')
    h1lept4_phi .Write('hlept4_phi_CR')
    h1Z1mass .Write('hZ1mass_CR')
    h1Z2mass .Write('hZ2mass_CR')
    h1pt4l .Write('hpt4l_CR')
    h1eta4l.Write('heta4l_CR')
    h1Ngood.Write('hNgood_CR')
    h1Nbjets.Write('hNbjets_CR')
    h1mass4l.Write('hmass4l_CR')
    fout.Close()

  # Write data shape histogram to file
  fs = TFile('datacards_' + args.channel + '/f' + args.channel + '.root', 'UPDATE')
  #hs = h1D_D
  hs = h1pfmet_D
  hs.SetName('data_obs')
  hs_rebin = hs.Rebin(nRebin, 'data_obs')
  fs.cd('bin' + args.channel)
  hs_rebin.Write('data_obs')

  #hs = h1D_WH
  hs = h1pfmet_WH
  fs.cd('bin' + args.channel)
  hs.Write()
  #hs = h1D_ZH
  hs = h1pfmet_ZH
  fs.cd('bin' + args.channel)
  hs.Write()
  #hs = h1D_ggH
  hs = h1pfmet_ggH
  fs.cd('bin' + args.channel)
  hs.Write()
  #hs = h1D_qqH
  hs = h1pfmet_qqH
  fs.cd('bin' + args.channel)
  hs.Write()
  #hs = h1D_ttH
  hs = h1pfmet_ttH
  fs.cd('bin' + args.channel)
  hs.Write()
  #hs = h1D_ggZZ
  hs = h1pfmet_ggZZ
  fs.cd('bin' + args.channel)
  hs.Write()
  #hs = h1D_qqZZ
  hs = h1pfmet_qqZZ
  fs.cd('bin' + args.channel)
  hs.Write()
  #hs = h1D_VVV
  hs = h1pfmet_VVV
  fs.cd('bin' + args.channel)
  hs.Write()
  #hs = h1D_TTV
  hs = h1pfmet_TTV
  fs.cd('bin' + args.channel)
  hs.Write()
  #hs = h1D_ZX
  hs = h1pfmet_ZX
  fs.cd('bin' + args.channel)
  hs.Write()

  fs.Close()
   
