#!/usr/local/bin/python
# -----------------------------------------------------------------------------
#  File:        gen_cards.py
#  Usage:       python gen_cards.py '4muchannel'
#  Description: Generates data cards used by the combine tool based on the 
#               template cards hhxx_*_Spring16_card_template.txt.
#  Created:     5-May-2017 Dustin Burns
# -----------------------------------------------------------------------------
import sys
import math

# Run parameters
model = 'MZp' 
datarun = 'Run2016'
channel = sys.argv[1]

# Parse yields.txt to fill label and yields lists
sig_labels = []
sig_yields = []
sig_e2 = []
WH = 0
e2WH = 0
ZH = 0
e2ZH = 0
ggH = 0
e2ggH = 0
qqH = 0
e2qqH = 0
ttH = 0
e2ttH = 0
ggZZ = 0
e2ggZZ = 0
qqZZ = 0
e2qqZZ = 0
VVV = 0
e2VVV = 0
TTV = 0
e2TTV = 0
ZX = 0
e2ZX = 0
data = 0
e2data = 0
for l in open('yields.txt'):
  if 'Yield' in l and channel in l:
    Name  = l.split('histos_all/')[1].split('.root')[0]
    Yield = l.split('Yield: ')[1].split(' Error:')[0]
    Err   = float(l.split('Error: ')[1])
    if model in l:
      sig_labels.append(Name)
      sig_yields.append(Yield)
      sig_e2.append(Err)
    elif datarun in l:
      data += float(Yield)
      e2data += Err*Err
    elif 'WminusH' in l or 'WplusH' in l:
      WH += float(Yield)
      e2WH += Err*Err
    elif 'ZH' in l:
      ZH += float(Yield)
      e2ZH += Err*Err
    elif 'GluGluHToZZTo4L' in l:
      ggH += float(Yield)
      e2ggH += Err*Err
    elif 'VBF_HToZZTo4L' in l:
      qqH += float(Yield)
      e2qqH += Err*Err
    elif 'ttH' in l:
      ttH += float(Yield)
      e2ttH += Err*Err
    elif 'GluGluToZZ' in l or 'GluGluToContin' in l:
      ggZZ += float(Yield)
      e2ggZZ += Err*Err
    elif '_ZZTo4L' in l or '_ZZTo2L2Nu' in l:
      qqZZ += float(Yield)
      e2qqZZ += Err*Err
    elif 'ZZZ' in l or 'WZZ' in l or 'WWZ' in l:
      VVV += float(Yield)
      e2VVV += Err*Err
    elif 'TTW' in l or 'TTZ' in l:
      TTV += float(Yield)
      e2TTV += Err*Err
    #else:
    elif 'WZ' in l or 'WW' in l or 'WJets' in l or 'TT' in l or 'QCD' in l or 'DYJets' in l:
      #print 'test  ' + l
      ZX += float(Yield)
      e2ZX += Err*Err

# Print total signal and background yields and uncertainties
print 'Channel ' + channel.split('channel')[0]
for i, n in enumerate(sig_labels): print str(i) + ' ' + n + ' ' + str(sig_yields[i]) + ' +/- ' + str(math.sqrt(sig_e2[i]))
print 'WH  ZH  ggH  qqH  ttH  ggZZ  qqZZ  VVV  TTV  ZX'
print str(WH) + ' ' + str(ZH) + ' ' + str(ggH) + ' ' + str(qqH) + ' ' + str(ttH) + ' ' + str(ggZZ) + ' ' + str(qqZZ) + ' ' + str(VVV) + ' ' + str(TTV) + ' ' + str(ZX)
print str(e2WH) + ' ' + str(e2ZH) + ' ' + str(e2ggH) + ' ' + str(e2qqH) + ' ' + str(e2ttH) + ' ' + str(e2ggZZ) + ' ' + str(e2qqZZ) + ' ' + str(e2VVV) + ' ' + str(e2TTV) + ' ' + str(e2ZX)
print 'H BKG: ' + str(WH + ZH + ggH + qqH + ttH)
print 'Other BKG: ' + str(ggZZ + qqZZ + VVV + TTV + ZX)
print 'Total BKG: ' + str(WH + ZH + ggH + qqH + ttH + ggZZ + qqZZ + VVV + TTV + ZX)
print 'Data: ' + str(data)

# Generate cards for different signals, adding systematics to relevant samples
for i in range(0, len(sig_labels)):
  cardin = open('hhxx_' + channel.split('channel')[0] + '_' + 'Spring16_card_template.txt')
  cardout = open('datacards_' + channel.split('channel')[0] + '/hhxx_Spring16_card_' + channel.split('channel')[0] + sig_labels[i].split('output')[1] + '.txt','w')
  for line in cardin:
    if 'OBS' in line:
      line = 'observation ' + str(data) + '\n'
    if 'sig' in line:
      line = 'process ' + sig_labels[i] + ' WH ZH ggH qqH ttH ggZZ qqZZ VVV TTV ZX ' + '\n'
    if 'YIELDS' in line:
      #if '2500' in sig_labels[i] or '2000' in sig_labels[i] or '1700' in sig_labels[i] or '1400' in sig_labels[i]:
      #  line = 'rate ' + str(1000*float(sig_yields[i])) + ' ' + str(WH) + ' ' + str(ZH) + ' ' + str(ggH) + ' ' + str(qqH) + ' ' + str(ttH) + ' ' + str(ggZZ) + ' ' + str(qqZZ) + ' ' + str(ZX) + '\n'
      #else:
        line = 'rate ' + sig_yields[i] + ' ' + str(WH) + ' ' + str(ZH) + ' ' + str(ggH) + ' ' + str(qqH) + ' ' + str(ttH) + ' ' + str(ggZZ) + ' ' + str(qqZZ) + ' ' + str(VVV) + ' ' + str(TTV) + ' ' + str(ZX) + '\n'
    cardout.write(line)
  cardin.close()
  cardout.close()

