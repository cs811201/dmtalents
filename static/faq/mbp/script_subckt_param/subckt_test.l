.param
+rds = 1                       xwc = 0                       wr = 1                        
+pp1 = 1e-12                   pp2 = 1e-12                   pp3 = 1e-12                   
+pp4 = 1e-12                   pp5 = 1e-12                   pp6 = 1e-12                   
+pp7 = 1e-12                   pp8 = 1e-12                   pp9 = 1e-12                   
+pp10 = 1e-12                  tr1 = 0                       tr2 = 0                       
+tex1 = 0                      tex2 = 0                      trx1 = 0                      
+trx2 = 0                      
.subckt mac d g s b w = 1.0E-6 l = 1.0E-6 dtemp = 0.0 count = 1.0 as = 0.0 ad = 0.0 ps = 0.0 pd = 0.0 
rdnoiseless d n1 'rds*(1+tr1*dtemp+tr2*dtemp*dtemp)' m='count/(20e-6-XWC)*(w-XWC)'
rsnoiseless n2 s 'rds/20*(1+tr1*dtemp+tr2*dtemp*dtemp)' m='count/(20e-6-XWC)*(w-XWC)'
mcore n1 g n2 b nmos w=w l=l m=count dtemp=dtemp as=as ad=ad ps=ps pd=pd
mpara n1 g n2 b ParaNMOS w=w l=l m=count dtemp=dtemp
fjfet n2 n1 cccs poly(1) vsense1 scale='count*((w-XWC)/(20e-6-XWC))**wr' 0 1
ex1 n101 n2 poly(1) d n1 scale='1+tex1*dtemp+tex2*dtemp*dtemp' m=1 0 pp1 pp2 pp3 pp4 pp5 pp6 pp7 pp8 pp9 pp10
rx1 n101 n102 1 m=1 dtemp=dtemp tc1=trx1 tc2=trx2
vsense1 n102 n2 0v

.model nmos nmos
*** Flag Parameter ***
+level = 49                    version = 3.3                 binunit = 2                   
+mobmod = 1                    capmod = 3                    nqsmod = 0                    
+igcmod = 0                    igbmod = 0                    
*** Geometry Range Parameter ***
+lmin = 0                      lmax = 1                      wmin = 0                      
+wmax = 1                      
*** Process Parameter ***
+tox = 1.5E-8                  xj = 1.5E-7                   nch = 1.7E17                  
*** dW and dL Parameter ***
+wint = 0                      wl = 0                        wln = 1                       
+ww = 0                        wwn = 1                       wwl = 0                       
+lint = 0                      ll = 0                        lln = 1                       
+lw = 0                        lwn = 1                       lwl = 0                       
+dwg = 0                       dwb = 0                       xl = 0                        
+xw = 0                        
*** Vth Related  Parameter ***
+vth0 = 0.7                    k1 = 0.53                     k2 = -0.0186                  
+k3 = 0                        k3b = 0                       w0 = 2.5E-6                   
+nlx = 1.74E-7                 dvt0 = 2.2                    dvt1 = 0.53                   
+dvt2 = -0.032                 dvt0w = 0                     dvt1w = 5.3E6                 
+dvt2w = -0.032                ngate = 1E30                  
*** Mobility Related Parameter ***
+u0 = 0.067                    ua = 2.25E-9                  ub = 5.87E-19                 
+uc = -4.65E-11                vsat = 8E4                    a0 = 1                        
+ags = 0                       b0 = 0                        b1 = 0                        
+keta = 0                      a1 = 0                        a2 = 1                        
+rdsw = 0                      prwb = 0                      prwg = 0                      
+wr = 1                        
*** Subthreshold Related Parameter ***
+voff = -0.08                  nfactor = 1                   eta0 = 0.08                   
+etab = -0.07                  dsub = 0.56                   cit = 0                       
+cdsc = 2.4E-4                 cdscb = 0                     cdscd = 0                     
*** Output Resistance Related Parameter ***
+pclm = 1.3                    pdiblc1 = 0.39                pdiblc2 = 8.6E-3              
+pdiblcb = 0                   drout = 0.56                  pscbe1 = 4.24E8               
+pscbe2 = 1E-5                 pvag = 0                      delta = 0.01                  
+alpha0 = 0                    beta0 = 0                     
*** Gate Dielectric Tunneling Current ***
+nigc = 1                      aigc = 0.012                  bigc = 2.8E-3                 
+cigc = 2E-3                   aigbacc = 0.012               bigbacc = 2.8E-3              
+cigbacc = 2E-3                nigbacc = 1                   aigbinv = 0.014               
+bigbinv = 4E-3                cigbinv = 4E-3                eigbinv = 1.1                 
+nigbinv = 3                   ntox = 1                      toxref = 1.5E-8               
+pigcd = 1                     poxedge = 1                   dlcig = 0                     
+aigsd = 0.012                 bigsd = 2.8E-3                cigsd = 2E-3                  
*** NQS Parameter ***
+elm = 0                       
*** Capacitance Parameter ***
+xpart = 0                     cgso = 0                      cgdo = 0                      
+cgbo = 0                      ckappa = 0.6                  cf = 0                        
+clc = 1E-7                    cle = 0.6                     dlc = 0                       
+dwc = 0                       vfbcv = -1                    cgsl = 0                      
+cgdl = 0                      
*** Souce/Drain Junction Diode Model Parameter ***
+acm = 12                      ldif = 0                      hdif = 0                      
+rsh = 0                       rd = 0                        rs = 0                        
+rsc = 0                       rdc = 0                       cj = 5E-4                     
+mj = 0.5                      mjsw = 0.33                   cjsw = 5E-10                  
+cjswg = 5E-10                 mjswg = 0.33                  js = 1E-4                     
+jsw = 0                       n = 1                         pbsw = 1                      
+pb = 1                        pbswg = 1                     
*** Temperature Coeffient ***
+tnom = 25                     ute = -1.5                    kt1 = -0.11                   
+kt1l = 0                      kt2 = 0.022                   ua1 = 4.31E-9                 
+ub1 = -7.61E-18               uc1 = -5.6E-11                at = 3.3E4                    
+prt = 0                       xti = 3                       
*** Stress Effect Related Parameter ***
+saref = 5E-6                  sbref = 5E-6                  wlod = 0                      
+ku0 = 0                       kvsat = 0                     kvth0 = 0                     
+tku0 = 0                      llodku0 = 0                   wlodku0 = 0                   
+llodvth = 0                   wlodvth = 0                   lku0 = 0                      
+wku0 = 0                      pku0 = 0                      lkvth0 = 0                    
+wkvth0 = 0                    pkvth0 = 0                    stk2 = 0                      
+lodk2 = 1                     steta0 = 0                    lodeta0 = 1                   
*** GIDL Current Parameters ***
+agidl = 0                     bgidl = 2.3E9                 cgidl = 0.5                   
+egidl = 0.8                   

.model ParaNMOS nmos
*** Flag Parameter ***
+level = 49                    version = 3.2                 binunit = 2                   
+mobmod = 1                    capmod = 3                    nqsmod = 0                    
*** Geometry Range Parameter ***
+lmin = 0                      lmax = 1                      wmin = 0                      
+wmax = 1                      
*** Process Parameter ***
+tox = 2E-7                    xj = 2E-6                     nch = 1.7E17                  
*** Vth Related  Parameter ***
+vth0 = 0.7                    k1 = 0.53                     k2 = -0.0186                  
*** Mobility Related Parameter ***
+u0 = 0.067                    ua = 2.25E-9                  ub = 5.87E-19                 
+uc = -4.65E-11                vsat = 8E4                    a0 = 1                        
+ags = 0                       keta = 0                      rdsw = 0                      
+prwb = 0                      prwg = 0                      
*** Temperature Coeffient ***
+tnom = 25                     ute = -1.5                    kt1 = -0.11                   
+kt1l = 0                      kt2 = 0.022                   ua1 = 4.31E-9                 
+ub1 = -7.61E-18               uc1 = -5.6E-11                at = 3.3E4                    
+prt = 0                       xti = 3                       

.ends
