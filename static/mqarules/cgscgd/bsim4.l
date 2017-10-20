.model nmos nmos
*** Flag Parameter ***
+level = 54                    version = 4.3                 binunit = 1                   
+paramchk = 1                  mobmod = 0                    capmod = 2                    
+rdsmod = 0                    igcmod = 0                    igbmod = 0                    
+rbodymod = 0                  trnqsmod = 0                  acnqsmod = 0                  
+fnoimod = 1                   tnoimod = 0                   diomod = 1                    
+tempmod = 0                   permod = 1                    geomod = 1                    
*** Geometry Range Parameter ***
+lmin = 0                      lmax = 1                      wmin = 0                      
+wmax = 1                      
*** Process Parameter ***
+epsrox = 3.9                  toxe = 3E-9                   xj = 1.5E-7                   
+ndep = 2.8E18                 ngate = 0                     nsd = 1E20                    
+rsh = 8                       rshg = 0.4                    
*** dW and dL Parameter ***
+wint = 0                      wl = 0                        wln = 1                       
+ww = 0                        wwn = 1                       wwl = 0                       
+lint = 0                      ll = 0                        lln = 1                       
+lw = 0                        lwn = 1                       lwl = 0                       
+dwg = 0                       dwb = 0                       xl = 0                        
+xw = 0                        
***Layout-Dependent Parasitics Model Parameter ***
+dmcg = 0                      dmci = 0                      dmdg = 0                      
+dmcgt = 0                     dwj = 0                       xgw = 0                       
+xgl = 0                       ngcon = 1                     
*** Vth Related  Parameter ***
+vth0 = 0.7                    vfb = -1                      phin = 0                      
+k1 = 0.53                     k2 = -0.0186                  k3 = 80                       
+k3b = 0                       w0 = 2.5E-6                   lpe0 = 1.74E-7                
+lpeb = 0                      dvtp0 = 0                     dvtp1 = 0                     
+dvt0 = 2.2                    dvt1 = 0.53                   dvt2 = -0.032                 
+dvt0w = 0                     dvt1w = 5.3E6                 dvt2w = -0.032                
*** Mobility Related Parameter ***
+u0 = 0.067                    ua = 1E-9                     ub = 1E-19                    
+uc = -4.65E-11                vsat = 8E4                    a0 = 1                        
+ags = 0                       b0 = 0                        b1 = 0                        
+keta = -0.047                 a1 = 0                        a2 = 1                        
+rdsw = 0                      rdswmin = 0                   rdw = 100                     
+rdwmin = 0                    rsw = 100                     rswmin = 0                    
+prwb = 0                      prwg = 0                      wr = 1                        
*** Subthreshold Related Parameter ***
+voff = -0.08                  voffl = 0                     minv = 0                      
+nfactor = 1                   eta0 = 0.08                   etab = -0.07                  
+dsub = 0.56                   cit = 0                       cdsc = 2.4E-4                 
+cdscb = 0                     cdscd = 0                     
*** Output Resistance Related Parameter ***
+pclm = 0.08                   pdiblc1 = 0.028               pdiblc2 = 0.022               
+pdiblcb = -5E-3               drout = 0.45                  pscbe1 = 8.14E8               
+pscbe2 = 5E-8                 pvag = 0                      delta = 0.01                  
+fprout = 0.2                  pdits = 0.2                   pditsl = 2.3E6                
+pditsd = 0.23                 lambda = 4E-10                vtl = 2E5                     
+lc = 5E-9                     xn = 6                        alpha0 = 0.074                
+alpha1 = 5E-3                 beta0 = 0                     
*** Gate Dielectric Tunneling Current ***
+aigbacc = 0.012               bigbacc = 2.8E-3              cigbacc = 2E-3                
+nigbacc = 1                   aigbinv = 0.014               bigbinv = 4E-3                
+cigbinv = 4E-3                eigbinv = 1.1                 nigbinv = 3                   
+aigc = 0.012                  bigc = 2.8E-3                 cigc = 2E-3                   
+aigsd = 0.012                 bigsd = 2.8E-3                cigsd = 2E-3                  
+dlcig = 0                     nigc = 1                      poxedge = 1                   
+pigcd = 1                     ntox = 1                      toxref = 3E-9               
*** GIDL Effect Parameters ***
+agidl = 0                     bgidl = 2.3E9                 cgidl = 0.5                  
+egidl = 0.8                   
*** Flicker Noise Model Parameter ***
+rnoia = 0.577                 rnoib = 0.37                  
*** Capacitance Parameter ***
+xpart = 0                     cgso = 0                      cgdo = 0                      
+cgbo = 0                      ckappas = 0.6                 ckappad = 0.6                 
+noff = 1                      voffcv = 0                    acde = 1                      
+moin = 15                     cgsl = 0                      cgdl = 0                      
*** Souce/Drain Junction Diode Model Parameter ***
+ijthsrev = 0.1                ijthdrev = 0.1                ijthsfwd = 0.1                
+ijthdfwd = 0.1                xjbvs = 1                     xjbvd = 1                     
+bvs = 10                      bvd = 10                      jss = 1E-4                    
+jsd = 1E-4                    jsws = 0                      jswd = 0                      
+jswgs = 0                     jswgd = 0                     cjs = 5E-4                    
+cjd = 5E-4                    mjs = 0.5                     mjd = 0.5                     
+mjsws = 0.33                  mjswd = 0.33                  cjsws = 5E-10                 
+cjswd = 5E-10                 cjswgs = 5E-10                cjswgd = 5E-10                
+mjswgs = 0.33                 mjswgd = 0.33                 pbs = 1                       
+pbd = 1                       pbsws = 1                     pbswd = 1                     
+pbswgs = 1                    pbswgd = 1                    
** RF Model Related Parameter ***
+xrcrg1 = 12                   xrcrg2 = 1                    rbpb = 50                     
+rbpd = 50                     rbps = 50                     rbdb = 50                     
+rbsb = 50                     gbmin = 1E-12                 
*** Temperature coefficient ***
+tnom = 27                     ute = -1.5                    kt1 = -0.11                   
+kt1l = 0                      kt2 = 0.022                   ua1 = 4.31E-9                 
+ub1 = -7.61E-18               uc1 = -5.6E-11                at = 3.3E4                    
+prt = 0                       njs = 1                       njd = 1                       
+xtis = 3                      xtid = 3                      tpb = 0                       
+tpbsw = 0                     tpbswg = 0                    tcj = 0                       
+tcjsw = 0                     tcjswg = 0                    
*** Stress Effect Related Parameter ***
+saref = 5E-6                  sbref = 5E-6                  wlod = 0                      
+ku0 = 0                       kvsat = 0                     kvth0 = 0                     
+tku0 = 0                      llodku0 = 0                   wlodku0 = 0                   
+llodvth = 0                   wlodvth = 0                   lku0 = 0                      
+wku0 = 0                      pku0 = 0                      lkvth0 = 0                    
+wkvth0 = 0                    pkvth0 = 0                    stk2 = 0                      
+lodk2 = 1                     steta0 = 0                    lodeta0 = 1                   

