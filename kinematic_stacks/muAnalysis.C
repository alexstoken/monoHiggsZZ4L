#define muAnalysis_cxx
#include "muAnalysis.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>

void muAnalysis::Loop()
{
//   In a ROOT session, you can do:
//      root> .L muAnalysis.C
//      root> muAnalysis t
//      root> t.GetEntry(12); // Fill t data members with entry number 12
//      root> t.Show();       // Show values of entry 12
//      root> t.Show(16);     // Read and show values of entry 16
//      root> t.Loop();       // Loop on all entries
//

//     This is the loop skeleton where:
//    jentry is the global entry number in the chain
//    ientry is the entry number in the current Tree
//  Note that the argument to GetEntry must be:
//    jentry for TChain::GetEntry
//    ientry for TTree::GetEntry and TBranch::GetEntry
//
//       To read only selected branches, Insert statements like:
// METHOD1:
//    fChain->SetBranchStatus("*",0);  // disable all branches
//    fChain->SetBranchStatus("branchname",1);  // activate branchname
// METHOD2: replace line
//    fChain->GetEntry(jentry);       //read all branches
//by  b_branchname->GetEntry(ientry); //read only this branch
  if (fChain == 0) return;

   Long64_t nentries = fChain->GetEntriesFast();

   
    int bin_massjj = 100;
    int ub_massjj = 1000;

    int bin_mass4l = 100;
    int ub_mass4l = 400;

    int bin_D = 100;
    float ub_D = 3.2;
    
    int bin_deltajj = 100;
    int ub_deltajj = 9;

    int bin_pt4l = 100;
    int ub_pt4l = 900;

    int bin_pfmet = 100;
    int ub_pfmet = 700;

 

    std::stringstream fn1ss; fn1ss << physics_type << "_massjj"; std::string massjj_name = fn1ss.str();
    std::stringstream fn2ss; fn2ss << physics_type << "_histos.root"; std::string file_name = fn2ss.str();
    std::stringstream fn3ss; fn3ss << physics_type << "_mass4l"; std::string mass4l_name = fn3ss.str();
    std::stringstream fn4ss; fn4ss << physics_type << "_D"; std::string D_name = fn4ss.str();
    std::stringstream fn5ss; fn5ss << physics_type << "_deltajj"; std::string deltajj_name = fn5ss.str();
    std::stringstream fn6ss; fn6ss << physics_type << "_pt4l"; std::string pt4l_name = fn6ss.str();
    std::stringstream fn7ss; fn7ss << physics_type << "_pfmet"; std::string pfmet_name = fn7ss.str();
      
    TH1F *massjj = new TH1F(massjj_name.c_str() , massjj_name.c_str(), bin_massjj, 0 ,ub_massjj );
    TH1F *mass4l = new TH1F(mass4l_name.c_str(), mass4l_name.c_str(), bin_mass4l, 80, ub_mass4l);
    TH1F *D      = new TH1F(D_name.c_str() , D_name.c_str(), bin_D, 0, ub_D);
    TH1F *deltajj = new TH1F(deltajj_name.c_str(), deltajj_name.c_str(), bin_deltajj, 0, ub_deltajj);
    TH1F *pt4l = new TH1F( pt4l_name.c_str(), pt4l_name.c_str(), bin_pt4l, 0, ub_pt4l);
    TH1F *pfmet = new TH1F( pfmet_name.c_str(), pfmet_name.c_str(), bin_pfmet, 0, ub_pfmet);  
 
   
   Long64_t nbytes = 0, nb = 0;
   for (Long64_t jentry=0; jentry<nentries;jentry++) {
      Long64_t ientry = LoadTree(jentry);
      if (ientry < 0) break;
      nb = fChain->GetEntry(jentry);   nbytes += nb;
      //if (Cut(ientry) < 0) continue;


      

      massjj->Fill(f_massjj, f_weight);
      mass4l->Fill(f_mass4l, f_weight);
      D ->Fill(f_D_jet, f_weight);
      deltajj ->Fill(f_deltajj, f_weight);
      pt4l ->Fill(f_pt4l, f_weight);
      pfmet ->Fill(f_pfmet, f_weight);


      
	
   }
   

   //to write each backgound type to it's own file use this
   TFile *f = new TFile(file_name.c_str(), "RECREATE");

   //to write all the histograms produced to one file use this
   //TFile *f = new TFile("analysis_histos.root", "RECREATE");
   
   massjj->Write();
   mass4l->Write();
   D ->Write();
   deltajj->Write();
   pt4l->Write();
   pfmet->Write();
   f->Close();
   


//   ofstream list;
// list.open("list_of_files.txt", ios::app);
// list << file_name.c_str() << "\n" ;
// list.close();

     
}
