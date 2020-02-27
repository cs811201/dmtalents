from pymqa import *
from math import pi, sqrt, fabs

from pymqacore import *

Vdd = "3.3"
HalfVdd = "1.65"
Vgg = "3.3"
Vdlin = "0.1"
Icon = 1E-7


def showInfo():
    srcdir = r"C:\\Users\\shuancai\\Desktop\\MQA_test\\Python_Test\\IV_Sweeps"
    prjs = loadmqaresult(srcdir)
    r = prjs[0]
    showinfo(r)


def showInfoCV():
    srcdir = r"C:\\Users\\shuancai\\Desktop\\MQA_test\\Python_Test\\Freq_Sweeps"
    prjs = loadmqaresult(srcdir)
    r = prjs[0]
    showinfo(r)


"""
Targets from Ids_Vds_Vgs curves:
1. Idsat: device,vds=vdd,vgs=vdd, vbs
2. Idlin: device,vds=vdlin,vgs=vdd,vbs
3. Ioff: device,vds=vdd,vgs=0,vbs
4. Vtlin: device, Icon, vbs, Vdlin
5. Vtsat: device, Icon, vbs, Vdd
6. DIBL: Vtlin - Vtsat 
7. Gm: derivative of IdVg
8. Gm2: second order derivative of IdVg

"""


def getTargetsFromIdVg():
    print("Working on Ids_Vgs_Vbs curves.")
    srcdir = r"C:\\Users\\shuancai\\Desktop\\MQA_test\\Python_Test\\IV_Sweeps"
    prjs = loadmqaresult(srcdir)
    r = prjs[0]
    # pcore.showinfo(r)


    ids = MqaTarget()
    ids = r.searchtag("Ids", ruleid="5001")
    # ids = ids.select("(T < 25)")

    print(ids.getnames())
    idsat = ids.select("Vgs==3.3")
    idsat = idsat.select("Vds==3.3")
    idsat = ids.select("Vgs==" + Vgg + " & Vds==" + Vdd)
    createScalingPlots(idsat, "Idsat")

    idsatw = idsat / "W"
    createScalingPlots(idsatw, "IdsatW")

    idlin = ids.select("Vgs==" + Vgg + " & Vds==" + Vdlin)
    createScalingPlots(idlin, "Idlin")

    ioff = ids.select("Vgs==0  & Vds==" + Vdd)
    createScalingPlots(ioff, "Ioff")

    gm = derivative(ids, "Vgs")
    createVsVgsPlots(gm, "Gm", "Vbs")
    createVsVgsPlots(gm, "Gm", "W")
    createVsVgsPlots(gm, "Gm", "L")
    createVsVgsPlots(gm, "Gm", "T")

    gm2 = derivative(gm, "Vgs")
    createVsVgsPlots(gm2, "Gm2", "Vbs")
    createVsVgsPlots(gm2, "Gm2", "W")
    createVsVgsPlots(gm2, "Gm2", "L")
    createVsVgsPlots(gm2, "Gm2", "T")

    # vth = calVtgm(ids, "Vgs")  # Max Gm method
    vth = calVthcon(ids, "Vgs")  # Vth_con method
    vtlin = vth.select("Vds == " + Vdlin)
    vtsat = vth.select("Vds == " + Vdd)
    dibl = vtlin - vtsat
    createScalingPlots(vtlin, "Vtlin")
    createScalingPlots(vtsat, "Vtsat")
    createScalingPlots(dibl, "DIBL")


"""
Targets from Ids_Vds_Vgs curves:
1. Idhigh: device,vds=vdd/2,vgs=vdd,vbs
2. Idlow: device,vds=vdd,vgs=vdd/2,vbs
3. Ideff: (Idhigh+Idlow)/2
4. Gds: derivative of IdVd
5. Gds2: second order derivative of IdVd
"""


def getTargetsFromIdVd():
    print("Now working on Ids_Vds_Vgs curves.")
    print("Working on Ids_Vgs_Vbs curves.")
    srcdir = r"C:\\Users\\shuancai\\Desktop\\MQA_test\\Python_Test\\IV_Sweeps"
    prjs = loadmqaresult(srcdir)
    r = prjs[0]
    ids = r.searchtag("Ids", ruleid="5002")

    idhigh = ids.select("Vgs==" + Vdd + " & Vds==" + HalfVdd)
    createScalingPlots(idhigh, "Idhigh")

    idlow = ids.select("Vgs==" + HalfVdd + " & Vds==" + Vdd)
    createScalingPlots(idlow, "Idlow")

    ideff = (idhigh + idlow) / 2
    createScalingPlots(ideff, "Ideff")

    gds = derivative(ids, "Vds")
    createVsVdsPlots(gds, "Gds", "Vgs", yLog=True)
    createVsVdsPlots(gds, "Gds", "T", yLog=True)
    createVsVdsPlots(gds, "Gds", "W", yLog=True)
    createVsVdsPlots(gds, "Gds", "L", yLog=True)
    createVsVdsPlots(gds, "Gds", "Vbs", yLog=True)

    gds2 = derivative(gds, "Vds")
    createVsVdsPlots(gds2, "Gds2", "Vgs", yLog=True)
    createVsVdsPlots(gds2, "Gds2", "T", yLog=True)
    createVsVdsPlots(gds2, "Gds2", "W", yLog=True)
    createVsVdsPlots(gds2, "Gds2", "L", yLog=True)
    createVsVdsPlots(gds2, "Gds2", "Vbs", yLog=True)


"""
SelfGain = Gm / Gds, it needs input from both IdVg and IdVd.
"""


def getSelfGain():
    print("Now calculate SelfGain")
    srcdir = r"C:\\Users\\shuancai\\Desktop\\MQA_test\\Python_Test\\IV_Sweeps"
    prjs = loadmqaresult(srcdir)
    r = prjs[0]
    idvg = r.searchtag("Ids", ruleid="5001")
    idvd = r.searchtag("Ids", ruleid="5002")

    gm = derivative(idvg, "Vgs")
    gds = derivative(idvd, "Vds")

    selfgain = gm / gds
    createScalingPlots(selfgain, "SelfGain")


"""
Find 2 nearest points around   Vth in curve Ids_Vgs, 
Vg1 ~ Vth, Vg2 ~ Vth - deltaVg(0.1 for SS, 0.05 for others)
    SS: Swing = 1000.0 * (Vg1 - Vg2) / (log10(abs(Id1)) - log10(abs(Id2)))
"""


def getSubthresholdSwing():
    # need to be able to calculate Vth for each IdVg curve, then fine the slope of that curve.
    # cannot do it right now
    ss = 0
    return ss


def createVsVdsPlots(target, newTargetName, zName, yLog=False):
    target.setname(newTargetName)
    pb = PlotBuilder()  # object to create plots or tables
    pb.buildplot(target, "Vds", zName)
    title = newTargetName + " vs Vds @ " + zName
    saveWithDirAndTitle(pb, newTargetName, title, yLog)


def createVsVgsPlots(target, newTargetName, zName=None, yLog=False):
    target.setname(newTargetName)
    pb = PlotBuilder()  # object to create plots or tables
    if zName is not None:
        pb.buildplot(target, "Vgs", zName)
        title = newTargetName + " vs Vgs @ " + zName
    else:
        pb.buildplot(target, "Vgs")
        title = newTargetName + " vs Vgs"
    saveWithDirAndTitle(pb, newTargetName, title, yLog)


def createScalingPlots(target, newTargetName):
    target.setname(newTargetName)
    pb = PlotBuilder()  # object to create plots or tables
    # Create Idsat vs L/W/T/Vbs
    pb.buildplot(target, "L", "W")
    # pb.save(dirName, YScale="Log",Title="")
    title = newTargetName + " vs L @ W"
    saveWithDirAndTitle(pb, newTargetName, title)

    pb.buildplot(target, "W", "L")
    title = newTargetName + " vs W @ L"
    saveWithDirAndTitle(pb, newTargetName, title)

    pb.buildplot(target, "T", "L")
    title = newTargetName + " vs T @ L"
    saveWithDirAndTitle(pb, newTargetName, title)

    pb.buildplot(target, "T", "W")
    title = newTargetName + " vs T @ W"
    saveWithDirAndTitle(pb, newTargetName, title)

    pb.buildplot(target, "Vbs")
    title = newTargetName + " vs Vbs"
    saveWithDirAndTitle(pb, newTargetName, title)


def saveWithDirAndTitle(pb, newTargetName, title, yLog=False):
    dir = newTargetName + "/" + title
    yscale = "Linear"
    if yLog:
        yscale = "Log"
    pb.save(givendir=dir, Title=title, YLabel=newTargetName, YScale=yscale)


# function to calculate first order derivative
@mqawrapper_loop
def derivative(y, x):
    num = len(x)
    d1 = []
    for i in range(0, num):
        if i == 0:
            a = 1
            b = 0
        elif i == num - 1:
            a = i
            b = i - 1
        else:
            a = i + 1
            b = i - 1
        drv = (y[a] - y[b]) / (x[a] - x[b])
        d1.append(drv)
    return d1


@mqawrapper_loop
def calVtgm(ids, vgs):
    vds = mqagetvalue("Vds")
    if vds is None:
        print("We can not get value with Vds !")
        return None
    gm = derivativePlain(ids, vgs)
    maxGm = max(gm)
    idx = gm.index(maxGm)

    vgatMaxGm = vgs[idx]

    idatMaxGm = ids[idx]

    vth = None
    if (vds < 0.5):
        vth = (vgatMaxGm - idatMaxGm / maxGm - vds / 2)
    else:
        # vds >= 0.5V
        vth = (vgatMaxGm - idatMaxGm / maxGm)
    # print("Vth", vth)
    return vth


@mqawrapper_loop
def calVthcon(y, x):
    M = mqagetvalue("M")
    if M is None:
        M = 1
    W = mqagetvalue("W")
    if W is None:
        print("We can not get value with W !")
        return None
    L = mqagetvalue("L")
    if L is None:
        print("We can not get value with L !")
        return None
    Iref = Icon * M * W / L
    num = len(x)
    vth = None
    ndirPre = 0
    for i in range(0, num):
        Ids = y[i]
        if Ids == Iref:
            vth = x[i]
            break
        if Ids > Iref:
            ndir = 1
        else:
            ndir = -1
        if ndirPre == 0:
            ndirPre = ndir
        elif ndir != ndirPre:
            # cross now
            vth = x[i] + (Iref - y[i]) * (x[i] - x[i - 1]) / (y[i] - y[i - 1])
            break
    if vth is None:
        print("Failed to find vth with W=", W, " L=", L)
    return vth


def derivativePlain(y, x):
    num = len(x)
    d1 = []
    for i in range(0, num):
        if i == 0:
            a = 1
            b = 0
        elif i == num - 1:
            a = i
            b = i - 1
        else:
            a = i + 1
            b = i - 1
        drv = (y[a] - y[b]) / (x[a] - x[b])
        d1.append(drv)
    return d1


@mqawrapper_loop
def findXwithmaxY(y, x):
    idx = y.index(max(y))
    return x[idx]


@mqawrapper_loop
def findXwhenYisOne(y, x):
    ret = y[0]
    idx = 0
    err0 = abs(y[0] - 1)
    count = 0
    for d in y:
        err = abs(d - 1)
        if err < err0:
            ret = d
            idx = count
        count += 1

    return x[idx]


# get targets from Y-parameters
def getTargetsFromY():
    print("Working on Y parameters.")
    srcdir = r"C:\\Users\\shuancai\\Desktop\\MQA_test\\Python_Test\\Freq_Sweeps"
    prjs = loadmqaresult(srcdir)
    r = prjs[0]

    Y11 = r.searchtag("y11", ruleid="4016")
    Y12 = r.searchtag("y12", ruleid="4016")
    Y21 = r.searchtag("y21", ruleid="4016")
    Y22 = r.searchtag("y22", ruleid="4016")

    # R0=50 is an option parameter
    [S11, S12, S21, S22] = Y2S([Y11, Y12, Y21, Y22], R0=50)
    # Complex functions are:  real(), imag(), mag(),phase(), angle()

    createVsFreqPlots(S11.real(), "S11r", "W", yLog=True)
    createVsFreqPlots(S11.imag(), "S11i", "W", yLog=True)
    createVsFreqPlots(S12.real(), "S12r", "W", yLog=True)
    createVsFreqPlots(S12.imag(), "S12i", "W", yLog=True)
    createVsFreqPlots(S21.real(), "S21r", "W", yLog=True)
    createVsFreqPlots(S21.imag(), "S21i", "W", yLog=True)
    createVsFreqPlots(S22.real(), "S22r", "W", yLog=True)
    createVsFreqPlots(S22.imag(), "S22i", "W", yLog=True)

    freq = 1E+5  # 100K Hz

    Cgg = Y11.imag() / (2 * pi * freq)
    createVsVgsPlots(Cgg, "Cgg", yLog=False)

    Cgs = (Y11.imag() + Y12.imag()) / (2 * pi * freq)
    createVsVgsPlots(Cgs, "Cgs", yLog=False)

    Cgd = -Y12.imag() / (2 * pi * freq)
    createVsVgsPlots(Cgd, "Cgd", yLog=False)

    Cgb = Cgg - Cgs - Cgd
    createVsVgsPlots(Cgb, "Cgb", yLog=False)

    Cout = Y22.imag() / (2 * pi * freq)
    createVsVgsPlots(Cout, "Cout", yLog=False)

    [H11, H12, H21, H22] = Y2H([Y11, Y12, Y21, Y22])
    H21mag = H21.mag()
    Ft = findXwhenYisOne(H21mag, "Freq")
    createVsVgsPlots(Ft, "Ft", yLog=False)
    createScalingPlots(Ft, "Ft")

    # Fmax:
    #U(fmax) = | Y21 - Y12 | 2 / 4*(Re(Y11)*Re(Y22) - Re(Y12)*Re(Y21) ) = 1
    D = Y21 - Y12
    Nu = D.mag()
    De = (Y11.real() * Y22.real() - Y12.real() * Y21.real()) * 4
    MAG = Nu / De
    Fmax = findXwhenYisOne(MAG, "Freq")
    createVsVgsPlots(Fmax, "Fmax", yLog=False)
    createScalingPlots(Fmax, "Fmax")
    print("...")


def createVsFreqPlots(target, newTargetName, zName=None, yLog=False):
    target.setname(newTargetName)
    pb = PlotBuilder()  # object to create plots or tables
    if zName is not None:
        pb.buildplot(target, "Freq", zName)
        title = newTargetName + " vs Freq @ " + zName
    else:
        pb.buildplot(target, "Freq")
        title = newTargetName + " vs Freq"
    saveWithDirAndTitle(pb, newTargetName, title, yLog)


if __name__ == "__main__":
    import time

    t1 = time.time()
    # showInfo()
    getTargetsFromIdVg()
    getTargetsFromIdVd()
    getSelfGain()
    # showInfoCV()
    getTargetsFromY()
    t2 = time.time()
    print("Total time:", (t2 - t1))
