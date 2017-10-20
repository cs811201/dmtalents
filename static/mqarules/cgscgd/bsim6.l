.model nmos nmos

*** Flag Parameters ***
+LEVEL = 77              VERSION = 0.7            
+GEOMOD = 0              RGEOMOD = 0              COVMOD = 0
+RDSMOD = 0              GIDLMOD = 0              RGATEMOD = 0 
+RBODYMOD = 0            IGCMOD = 0               IGBMOD = 0  
+TNOIMOD = 0                                      
                                                  
*** Geometry Parameters ***
+XL = 0                  XW = 0                   LINT = 0 
+LL = 0                  LW = 0                   LWL = 0 
+LLN = 1.0               LWN = 1.0                WINT = 0  
+WL = 0                  WW = 0                   WWL = 0 
+WLN = 1.0               WWN = 1.0                DLC = 0 
+LLC = 0                 LWC = 0                  LWLC = 0
+DWC = 0                 WLC = 0                  WWC = 0 
+WWLC = 0                DWJ = 0                          

*** Process Parameters ***
+TOXE = 3.0e-9           TOXP = 3.0e-9            DTOX = 0 
+NDEP = 1e24             NGATE = 5e25             EASUB = 4.05
+NI0SUB = 1.1e16         BG0SUB = 1.17            EPSRSUB = 11.9
+EPSROX = 3.9            XJ = 1.5e-7              VFB = -1.0 
+NDEPCV = 1e24           ANDEPCV = 0.0
+BNDEPCV = 1.0           VFBCV = -1.0             AVFBCV = 0.0
+BVFBCV = 1.0

*** Short Channel Effects ***
+NSD = 1e26              DVT0 = 0.2               DVT1 = 1.0
+DVT2 = -0.0002          DVT0W = 0                DVT1W = 5.3e+6
+DVT2W = -0.032          K3 = 0                   K3B = 0 
+W0 = 0.5e-6             DVTP0 = 1.0e-010         DVTP1 = 0.0
+PHIN = 0.045            ETA0 = 0.08              ETAB = -0.07
+DSUB = 0.375            LPE0 = 8.2e-9            LPEB = 10.0e-9
+K1 = 0                  K2 = 0                   LPE0EXP = 1.25
+LPEBEXP = 1.25

*** Quantum Mechanical Effects ***
+ADOS = 0.0              BDOS = 1.0               QM0 = 1.0e-3
+ETAQM = 0.54            

*** Subthreshold Swing Factor ***
+CIT = 1.0e-8            CDSC = 0                 CDSCD = 0
+CDSCB = 0               NFACTOR = 0 

*** Drain Saturation Voltage ***
+VSAT = 1e5              AVSAT = 0                BVSAT = 100.0e-9
+DELTA = 0.125           ADELTA = 0               BDELTA = 1.0     
+VSATCV = 1e5            AVSATCV = 0              BVSATCV = 100.0e-9       

*** Mobility Degradation ***
+U0 = 67.0e-3            ETAMOB = 1.0             UP = 0.0 
+LPA = 5e-9              UA = 0.001               AUA = 0.0 
+BUA = 100.0e-9          EU = 1.5                 AEU = 0.0
+BEU = 100.0e-9          UD = 0.001               AUD = 0.0
+BUD = 100.0e-9          UCS = 2.0                UC = 0.0
+AUC = 0.0               BUC = 100.0e-9

*** Channel Length Modulation ***
+PCLM = 0.0              APCLM = 0.0              BPCLM = 100.0e-9
+PCLMCV = 0.0            APCLMCV = 0.0            BPCLMCV = 100.0e-9
+PCLMG = 0.0             PSCBE1 = 4.24e8          PSCBE2 = 1e-8
+PDITS = 0.0             PDITSL = 0.0             PPDITSD = 0.0

*** S/D Series Resistance ***
+RSH = 0.0               PRWG = 1.0               PRWB = 0.0 
+WR = 1.0                RSWMIN = 0.0             RSW = 10.0 
+ARSW = 0.0              BRSW = 100.0e-9          RDWMIN = 0.0
+RDW = 10.0              ARDW = 0.0               BRDW = 100.0e-9
+RDSWMIN = 0.0           RDSW = 20.0              ARDSW = 0.0 
+BRDSW = 100.0e-9

*** Velocity Saturation ***
+PTWG = 0.0              APTWG = 0.0              BPTWG = 100.0e-9
+PSAT = 2.0              PSATB = 0                PSATX = 1.0      
+APSAT = 0.0             BPSAT = 100.0e-9

*** Output Conductance ***
+PDIBLC1 = 1.3           PDIBLC2 = 2e-4           PDIBLCB = 0
+DROUT = 1.06            PVAG = 1.0               FPROUT = 0

*** Impact Ionization Current ***
+ALPHA0 = 0.0            ALPHA1 = 0.0             BETA0 = 0.0 

*** Gate Dielectric Tunneling Current Model Parameters ***
+AIGBACC = 1.36e-2       BIGBACC = 1.71e-3        CIGBACC = 0.075
+NIGBACC = 1.0           AIGBINV = 1.11e-2        BIGBINV = 9.49e-4
+CIGBINV = 0.006         EIGBINV = 1.1            NIGBINV = 3.0 
+AIGC = 1.36e-2          BIGC = 1.71e-3           CIGC = 0.075
+AIGS = 1.36e-2          BIGS = 1.71e-3           CIGS = 0.075
+AIGD = 1.36e-2          BIGD = 1.71e-3           CIGD = 0.075
+DLCIG = 0               NIGC = 1.0               POXEDGE = 1.0
+NTOX = 1.0              TOXREF = 3.0e-9          DLCIGD = 0
+PIGCD = 1.0

*** GIDL/GISL Current ***
+AGIDL = 0               BGIDL = 2.3e9            CGIDL = 0.5
+EGIDL = 0.8             AGISL = 0                BGISL = 2.3e9
+CGISL = 0.5             EGISL = 0.8        
      
*** Overlap Cap and Fringing Cap ***
+CF = 0.0                CFRCOEFF = 1.0           
+CGSO = 0                CGDO = 0                 CGBO = 0 
+CGSL = 0                CGDL = 0                 CKAPPAS = 0.6 
+CKAPPAD = 0.6           

*** Layout-Dependent Parasitics Model Parameters ***
+DMCG = 0.0              DMCI = 0.0               DMDG = 0.0
+DMCGT = 0.0             XGW = 0.0                XGL = 0.0 
+NGCON = 1               RSHG = 0.1

*** Junction current and capacitance ***
+CJS = 5.0e-4            CJD = 5.0e-4             CJSWS = 5.0e-10
+CJSWD = 5.0e-10         CJSWGS = 0.0             CJSWGD = 0.0
+PBS = 1.0               PBD = 1.0                PBSWS = 1.0
+PBSWD = 1.0             PBSWGS = 1.0             PBSWGD = 1.0
+MJS = 0.5               MJD = 0.5                MJSWS = 0.33
+MJSWD = 0.33            MJSWGS = 0.33            MJSWGD = 0.33
+JSS = 1.0e-4            JSD = 1.0e-4             JSWS = 0.0 
+JSWD = 0.0              JSWGS = 0.0              JSWGD = 0.0
+NJS = 1.0               NJD = 1.0                IJTHSFWD = 0.1
+IJTHDFWD = 0.1          IJTHSREV = 0.1           IJTHDREV = 0.1
+BVS = 10.0              BVD = 10.0               XJBVS = 1.0
+XJBVD = 1.0             JTSS = 0.0               JTSD = 0.0
+JTSSWS = 0.0            JTSSWD = 0.0             JTSSWGS = 0.0
+JTSSWGD = 0.0           JTWEFF = 0.0             NJTS = 20.0 
+NJTSD = 20.0            NJTSSW = 20.0            NJTSSWD = 20.0
+NJTSSWG = 20.0          NJTSSWGD = 20.0          VTSS = 10.0
+VTSD = 10.0             VTSSWS = 10.0            VTSSWD = 10.0
+VTSSWGS = 10.0          VTSSWGD = 10.0           

*** High-Speed/RF Model Parameters ***
+XRCRG1 = 12.0           XRCRG2 = 1.0             RBPB = 50.0
+RBDB = 50.0             RBSB = 50.0              RBPS = 50.0
+RBPD = 50.0             GBMIN = 1.0e-12          RBPS0 = 50.0 
+RBPSL = 0.0             RBPSW = 0.0              RBPSNF = 0.0
+RBPD0 = 50.0            RBPDL = 0.0              RBPDW = 0.0
+RBPDNF = 0.0            RBPBX0 = 100.0           RBPBXL = 0.0
+RBPBXW = 0.0            RBPBXNF = 0.0            RBPBY0 = 100.0
+RBPBYL = 0.0            RBPBYW = 0.0             RBPBYNF = 0.0
+RBSBX0 = 100.0          RBSBY0 = 100.0           RBDBX0 = 100.0
+RBDBY0 = 100.0          RBSDBXL = 0.0            RBSDBXW = 0.0
+RBSDBXNF = 0.0          RBSDBYL = 0.0            RBSDBYW = 0.0
+RBSDBYNF = 0.0 

*** Flicker Noise ***
+EF = 1.0                EM = 4.1e7               NOIA = 6.250e+40
+NOIB = 3.125e+25        NOIC = 8.750e+8          LINTNOI = 0

***Thermal Noise ***
+NTNOI = 1.0             RNOIA = 0.577            RNOIB = 0.5164
+RNOIC = 0.395           TNOIA = 0.0              TNOIB = 0.0
+TNOIC = 0.0

*** Temperature Dependence Parameters ***
+TNOM = 27.0             TBGASUB = 4.73e-4        TBGBSUB = 636.0
+UTE = -1.5              UA1 = 1.0e-3             UC1 = 0.056e-9
+UD1 = 0.0               UCSTE = -4.775e-3        PRT = 0.0
+AT = -1.56e-3           TDELTA = 0.0             PTWGT = 0.0
+KT1 = -0.11             KT1L = 0.0               KT2 = 0.022
+IIT = 0.0               IGT = 2.5                TGIDL = 0.0
+TCJ = 0.0               TCJSW = 0.0              TCJSWG = 0.0 
+TPB = 0.0               TPBSW = 0.0              TPBSWG = 0.0
+XTIS = 3.0              XTID = 3.0               XTSS = 0.02
+XTSD = 0.02             XTSSWS = 0.02            XTSSWD = 0.02
+XTSSWGS = 0.02          XTSSWGD = 0.02           TNJTS = 0.0
+TNJTSD = 0.0            TNJTSSW = 0.0            TNJTSSWD = 0.0
+TNJTSSWG = 0.0          TNJTSSWGD = 0.0

*** Stress related Parameter ***
+SA = 0                  SB = 0                   SD = 0
+SAREF = 1.0e-6          SBREF = 1.0e-6           WLOD = 0
+KU0 = 0                 KVSAT = 0                TKU0 = 0 
+LLODKU0 = 0             WLODKU0 = 0              KVTH0 = 0 
+LLODVTH = 0             WLODVTH = 0              STK2 = 0  
+LODK2 = 0               STETA0 = 0               LODETA0 = 0 

*** Well Proximity Parameters ***
+SCA = 0                 SCB = 0                  SCC = 0 
+SC = 0                  WEB = 0                  WEC = 0 
+KVTH0WE = 0.0           K2WE = 0                 KU0WE = 0 
+SCREF = 1.0e-6           

*** GMIN - added for convergence ***
+GMIN = 1.0e-15 