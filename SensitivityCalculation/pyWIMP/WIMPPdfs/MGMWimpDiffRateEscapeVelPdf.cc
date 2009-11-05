 /***************************************************************************** 
  * Project: RooFit                                                           * 
  *                                                                           * 
  * This code was autogenerated by RooClassFactory                            * 
  *****************************************************************************/ 


 #include "MGMWimpDiffRateEscapeVelPdf.hh" 
 #include "RooAbsReal.h" 
 #include "TMath.h" 

 ClassImp(MGMWimpDiffRateEscapeVelPdf) 

 MGMWimpDiffRateEscapeVelPdf::MGMWimpDiffRateEscapeVelPdf(const char *name, const char *title, 
                        RooAbsReal& _v_sub_0,
                        RooAbsReal& _v_sub_min,
                        RooAbsReal& _v_sub_E,
                        RooAbsReal& _R_sub_0,
                        RooAbsReal& _E_sub_0,
                        RooAbsReal& _r, 
	                RooAbsReal& _v_sub_esc,
	                MGMVWimpFormFactor& _form_factor) :
   MGMWimpDiffRatePdf(name, title,
                      _v_sub_0, _v_sub_min, _v_sub_E,
                      _R_sub_0, _E_sub_0, _r, _form_factor), 
   v_sub_esc("v_sub_esc","v_sub_esc",this,_v_sub_esc)
   
 { 
 } 


 MGMWimpDiffRateEscapeVelPdf::MGMWimpDiffRateEscapeVelPdf(const MGMWimpDiffRateEscapeVelPdf& other, const char* name) :  
   MGMWimpDiffRatePdf(other,name), 
   v_sub_esc("v_sub_esc",this,other.v_sub_esc)
 { 
 } 



 Double_t MGMWimpDiffRateEscapeVelPdf::EvaluatePDF() const 
 { 
   Double_t temp = 
          getK0OverK1()*( MGMWimpDiffRatePdf::EvaluatePDF() - 
          (R_sub_0/(E_sub_0*r))*
          TMath::Exp(-TMath::Power(v_sub_esc/v_sub_0,2)) );
   return (temp > 0) ? temp : 0.0;
 } 

 Double_t MGMWimpDiffRateEscapeVelPdf::getK0OverK1() const 
 { 
   return 1./(TMath::Erf(v_sub_esc/v_sub_0) - (2./TMath::Sqrt(TMath::Pi()))*
          (v_sub_esc/v_sub_0)*TMath::Exp(-TMath::Power(v_sub_esc/v_sub_0,2))); 
 } 



