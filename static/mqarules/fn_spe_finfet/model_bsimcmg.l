simulator lang = spectre
model nmos bsimcmg
*** flag parameter ***
+bulkmod = 0            asymmod=0                type=n  
+coremod = 0            geomod = 0               rdsmod = 0
+igcmod = 0             igbmod = 0               gidlmod = 0 
+iimod = 0              nqsmod = 0               shmod = 0 
+rgatemod = 0           rgeomod = 0              cgeomod = 0
+capmod = 0             version = 107.0          cgeo1sw = 0

*** geometry range parameter ***
+lint = 0               ll = 0                   lln = 1
+dlc = 0                dlbin = 0                llc =0 
+dlcacc=0

*** process parameter ***
+eot = 1e-9             toxp = 1.2e-9            eotbox = 1.4e-7
+hfin = 3e-8            fech = 1                 deltaw = 0
+fechcv = 1             deltawcv = 0             nbody = 1e22
+nbodyn1 = 0            nbodyn2 = 1.0e5
+nsd = 2e26             phig = 4.61              epsrox = 3.9
+phigl = 0              phign1 = 0               phign2 = 1.0e5
+epsrsub = 11.9         easub = 4.05             ni0sub = 1.1e16
+bg0sub = 1.12          nc0sub = 2.86e25         ngate = 0
+imin=1e-15

*** short channel effects ***
+cit = 0.0              cdsc = 7e-3              cdscd = 7e-3
+cdscn1 = 0             cdscn2 = 1.0e5           cdscdn1 = 0                 
+cdscdn2 = 1.0e5        cdscdrn1 = 0             cdscdrn2 = 1.0e5
+dvt1ss = 0.6           eta0n1 = 0               eta0n2 = 1.0e5
+teta0 = 0.0            teta0r = 0.0             dvtp0 = 0
+dvtp1 = 0
+cdscdr = 7e-3          dvt0 = 0.0               dvt1 = 0.60
+phin = 0.05            eta0 = 0.60              eta0r = 0.60
+dsub = 1.06            k1rsce = 0               lpe0 = 5e-9
+dvtshift = 0 

*** lateral non-uniform doping effect (iv-cv vth shift) ***
+k0=0.0                 k01=0.0                  k0si=1.0
+k0si1=0.0              k1si=1.0                 k1si1=0.0

*** body effect for mg devices on bulk substrate (ex: finfets on bulk) ***
+phibe=0.7              k1=0.0                   k11=0.0
+k1sat=0.0              k1sat1=0.0

*** quantum mechanical effect ***
+qmfactor = 0           qmtceniv = 0             qmtcencv = 0
+qmtcencva=0.0
+aqmtcen = 0            bqmtcen = 12.0e-9        etaqm = 0.54
+qm0 = 1.00e-3          pqm = 0.66               qm0acc = 1.00e-3
+pqmacc = 0.66          

*** velocity saturation model ***
+vsat = 8.5e4           avsat = 0                bvsat = 100.0e-9
+vsatn1 = 0             vsatn2 = 1.0e5           vsat1n1 = 0
+vsat1n2 = 1.0e5        vsat1rn1 = 0             vsat1rn2 = 1.0e5
+vsat1 = 8.5e4          avsat1 = 0               vsat1r= 8.5e4
+bvsat1 = 100.0e-9      deltavsat = 1.0          ksativ = 1.0 
+mexp = 4               amexp = 0                bmexp = 1.0 
+mexpr = 4.0            amexpr = 0.0             bmexpr = 1.0             
+ptwg = 0               aptwg = 0                
+bptwg = 100.0e-9       at = -1.56e-3            tmexp = 0  
+tmexpr = 0.0              
+ptwgt = 0.004          ptwgr=0.0
+psat=2.0               apsat=0.0                bpsat=1.0
+vsatcv= 8.5e4          avsatcv=0.0              bvsatcv=100.0e-9
+deltavsatcv=1.0        psatcv=2.0               apsatcv=0.0
+bpsatcv=1.0          

*** mobility related parameter ***
+u0 = 0.03              etamob = 2.0             up = 0
+u0n1 = 0               u0n2 = 1.0e5
+lpa = 1                ua = 0.3                 aua = 0
+bua = 100.0e-9         eu = 2.5                 uc=0.0
+aeu = 0                beu = 100.0e-9           ud = 0.0                 
+aud = 0                bud = 50.0e-9            ucs = 1.0                
+ute = 0.0              utl = -1.5e-3            emobt=0.0             
+ua1 = 1.032e-3         ud1 = 0.0                uc1=0.056e-9
+ucste = -4.775e-3      chargewf = 0

*** access resistance model ***
+rdswmin = 0            rdsw = 100.0             ardsw = 0
+brdsw = 100.0e-9       rswmin = 0               rsw = 50.0
+arsw = 0               brsw = 100.0e-9          rdwmin = 0
+rdw = 50.0             ardw = 0                 brdw = 100.0e-9
+wr = 1                 prt = 0.001              rsdr=0.0
+rsdrr=0.0              rddr=0.0                 rddrr=0.0
+prsdr=1.0              prddr=1.0                prwgs=0.0
+prwgd=0.0              trsdr=0.0                trddr=0.0

*** dibl model ***
+pdibl1 = 1.30          pdibl2 = 2.0e-4         pdibl1r=1.3 
+drout = 1.06           pvag = 1.0             

*** channel length modulation effect ***
+pclm = 0.013           apclm = 0                bpclm = 100.0e-9       
+pclmg = 0              pclmcv = 0.013                    

*** non-saturation effect ***
+a1=0.0                 a11=0.0                  a2=0.0
+a21=0.0

*** gate electrode resistance ***
+rgext = 0.0            rgfin = 1.0e-3           rshs = 0.0
+rshd = 0.0             hepi = 1e-8              tsili = 1e-8
+rhoc = 1e-12           rhorsd = 1.0             
+cratio = 0.5           deltaprsd = 0            sdterm = 0.0
+lsp = 6e-9             epsrsp = 3.9
+tgate = 3e-8           tmask = 3e-8             asiliend = 0.0
+arsdend = 0.0          prsdend = 0.0            nsde = 2e25
+rgeoa = 1.0            rgeob = 0.0              rgeoc = 0.0
+rgeod = 0.0            rgeoe = 0.0              cgeoa = 1.0
+cgeob = 0.0            cgeoc = 0.0              cgeod = 0.0
+cgeoe = 1.0

*** gate current ***
+aigbinv = 1            bigbinv = 9.49e-4        cigbinv = 6.00e-3
+eigbinv = 1.1          nigbinv = 3.0            aigbacc = 1.36e-2
+bigbacc = 1.71e-3      cigbacc = 7.5e-2         nigbacc = 1.0
+aigc = 1.36e-2         bigc = 1.71e-3           cigc = 0.075
+dlcigs = 0.0           aigs = 1.36e-2
+bigs = 1.71e-3         cigs = 0.075             dlcigd = 0.0
+aigd = 1.36e-2         bigd = 1.71e-3           cigd = 0.075
+poxedge = 1.0          
+agidl = 6.055e-12      bgidl = 0.3e9            cgidl = 0.5 
+egidl = 0.2            pgidl=1.0
+agisl = 6.055e-12      bgisl = 0.3e9            cgisl = 0.5 
+egisl = 0.2            pigcd = 1.0                            
+aigbinv1=0.0           aigbacc1=0.0             aigc1=0.0
+aigs1=0.0              aigd1=0.0                toxref=1.2e-9
+toxg=1.2e-9            ntox=1.0                         

*** impact ionization current ***
+alpha0 = 0             alpha1 = 0               beta0 = 0.0
+betaii0 = 0            betaii1 = 0
+betaii2 = 0.1          esatii = 1.0e7           lii = 0.5e-9
+sii0 = 0.5             sii1 = 0.1               sii2 = 0.0
+siid = 0.0
+alpha01=0.0            alpha11=0.0              alphaii0=0.0
+alphaii01=0.0          alphaii1=0.0             alphaii11=0.0 

*** accumulation capacitance (capmod=1) ***
+eotacc = 1e-9          delvfbacc = 0.0

*** fringe capacitance ***
+cfs = 2.5e-11          cfd = 2.5e-11            

*** overlap capacitance (cgeomod=0 and 2) ***
+cgso = 0.0             cgdo = 0.0               cgsl = 0.0
+cgdl = 0.0             ckappas = 0.6            ckappad = 0.6
+cgbo = 0.0             cgbl = 0.0               ckappab = 0.6
+cgbn=0.0 
      

*** source/drain to substrate sidewall capacitance ***
+csdesw = 0.6

*** junction current and capacitance ***
+cjs = 5e-4             cjd = 5e-4                cjsws = 5e-10
+cjswd = 5e-10          cjswgs = 0.0              cjswgd = 0.0
+pbs = 1                pbd = 1                   pbsws = 1
+pbswd = 1              pbswgs = 1                pbswgd = 1
+mjs = 0.5              mjd = 0.5                 mjsws = 0.33
+mjswd = 0.33           mjswgs = 0.33             mjswgd = 0.33
+sjs = 0.0              sjd = 0.0                 sjsws = 0.0
+sjswd = 0.0            sjswgs = 0.0              sjswgd = 0.0
+mjs2 = 0.125           mjd2 = 0.125              mjsws2 = 0.083
+mjswd2 = 0.083         mjswgs2 = 0.083           mjswgd2 = 0.083
+jss = 1e-4             jsd = 1e-4                jsws = 0                  
+jswd = 0               jswgs = 0                 jswgd = 0                 
+njs = 1                njd = 1                   ijthsfwd = 0.1            
+ijthdfwd = 0.1         ijthsrev = 0.1            ijthdrev = 0.1            
+bvs = 10               bvd = 10                  xjbvs = 1                 
+xjbvd = 1

*** tunneling component of junction current ***
+jtss = 0               jtsd = 0                  jtssws = 0
+jtsswd = 0             jtsswgs = 0               jtsswgd = 0 
+jtweff = 0             njts = 20                 njtsd = 20 
+njtssw = 20            njtsswd = 20              njtsswg = 20
+njtsswgd = 20          vtss = 10                 vtsd = 10 
+vtssws = 10            vtsswd = 10               vtsswgs = 10 
+vtsswgd = 10           lintigen = 1e-10              ntgen = 1.0
+aigen = 0              bigen = 0 

*** nqs gate resistance model & nqs charge deficit model ***
+xrcrg1 = 12            xrcrg2 = 1

*** nqs charge segementation model ***
+nseg = 4

*** flicker noise ***
+ef = 1                 em = 4.1e7                noia = 6.25e39
+noib = 3.125e24        noic = 8.75e7            

*** thermal noise ***
+ntnoi = 1

*** temperature effects ***
+tnom = 27              tbgasub = 7.02e-4         tbgbsub = 1.108e3
+kt1 = 0.0              kt1l = 0                  iit = -0.5
+tii = 0.0              tgidl = -0.003            igt = 2.5
+tcj = 0.0              tcjsw = 0.0               tcjswg = 0.0
+tpb = 0.0              tpbsw = 0.0               tpbswg = 0.0
+xtis = 3               xtid = 3                  xtss = 0.02
+xtsd = 0.02            xtssws = 0.02             xtsswd = 0.02
+xtsswgs = 0.02         xtsswgd = 0.02            tnjts = 0 
+tnjtsd = 0             tnjtssw = 0               tnjtsswd = 0 
+tnjtsswg = 0           tnjtsswgd = 0             tss=0.0

*** self heating ***
+rth0 = 0.01            cth0 = 1e-5               wth0 = 0  