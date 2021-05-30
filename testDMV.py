# %% Imports
from readDMV import readDMV
import matplotlib.pyplot as plt

# %% RNC
c1 = readDMV('/Users/vonw/data/paeri/raw/AE160201/160201C1.RNC')
plt.figure()
c1.mean_rad[0].plot()
c1.mean_rad[-1].plot()
plt.show()

c2 = readDMV('/Users/vonw/data/paeri/raw/AE160201/160201C2.RNC')
plt.figure()
c2.mean_rad[0].plot()
c2.mean_rad[-1].plot()
plt.show()

# %% RLC
b1 = readDMV('/Users/vonw/data/paeri/reprocessed/AE110602/110602B1.RLC')
plt.figure()
b1.atmosphericRadiance[0].plot()
b1.atmosphericRadiance[-1].plot()
plt.show()

f1 = readDMV('/Users/vonw/data/paeri/reprocessed/AE110602/110602F1.RLC')
plt.figure()
f1.atmosphericRadiance[0].plot()
f1.atmosphericRadiance[-1].plot()
plt.show()

b2 = readDMV('/Users/vonw/data/paeri/reprocessed/AE110602/110602B2.RLC')
plt.figure()
b2.atmosphericRadiance[0].plot()
b2.atmosphericRadiance[-1].plot()
plt.show()

f2 = readDMV('/Users/vonw/data/paeri/reprocessed/AE110602/110602F2.RLC')
plt.figure()
f2.atmosphericRadiance[0].plot()
f2.atmosphericRadiance[-1].plot()
plt.show()

c1 = readDMV('/Users/vonw/data/paeri/reprocessed/AE110602/110602C1.RLC')
plt.figure()
c1.averageRadiance[0].plot()
c1.averageRadiance[-1].plot()
plt.show()

c2 = readDMV('/Users/vonw/data/paeri/reprocessed/AE110602/110602C2.RLC')
plt.figure()
c2.averageRadiance[0].plot()
c2.averageRadiance[-1].plot()
plt.show()

# %% CXS
b1 = readDMV('/Users/vonw/data/paeri/reprocessed/AE110602/110602B1.CXS')
plt.figure()
b1.Ch1BackwardScanRealPartCounts[0].plot()
b1.Ch1BackwardScanImagPartCounts[0].plot()
b1.Ch1BackwardScanRealPartCounts[-1].plot()
b1.Ch1BackwardScanImagPartCounts[-1].plot()
plt.show()

f1 = readDMV('/Users/vonw/data/paeri/reprocessed/AE110602/110602F1.CXS')
plt.figure()
f1.Ch1ForwardScanRealPartCounts[0].plot()
f1.Ch1ForwardScanImagPartCounts[0].plot()
f1.Ch1ForwardScanRealPartCounts[-1].plot()
f1.Ch1ForwardScanImagPartCounts[-1].plot()
plt.show()

b2 = readDMV('/Users/vonw/data/paeri/reprocessed/AE110602/110602B2.CXS')
plt.figure()
b2.Ch2BackwardScanRealPartCounts[0].plot()
b2.Ch2BackwardScanImagPartCounts[0].plot()
b2.Ch2BackwardScanRealPartCounts[-1].plot()
b2.Ch2BackwardScanImagPartCounts[-1].plot()
plt.show()

f2 = readDMV('/Users/vonw/data/paeri/reprocessed/AE110602/110602F2.CXS')
plt.figure()
f2.Ch2ForwardScanRealPartCounts[0].plot()
f2.Ch2ForwardScanImagPartCounts[0].plot()
f2.Ch2ForwardScanRealPartCounts[-1].plot()
f2.Ch2ForwardScanImagPartCounts[-1].plot()
plt.show()

# %% CXV
b1 = readDMV('/Users/vonw/data/paeri/reprocessed/AE110602/110602B1.CXV')
plt.figure()
b1.RealPartCounts[0].plot()
b1.ImagPartCounts[0].plot()
b1.RealPartCounts[-1].plot()
b1.ImagPartCounts[-1].plot()
plt.show()

f1 = readDMV('/Users/vonw/data/paeri/reprocessed/AE110602/110602F1.CXV')
plt.figure()
f1.RealPartCounts[0].plot()
f1.ImagPartCounts[0].plot()
f1.RealPartCounts[-1].plot()
f1.ImagPartCounts[-1].plot()
plt.show()

# %% SUM
sm = readDMV('/Users/vonw/data/paeri/reprocessed/AE110602/110602.SUM')
plt.figure()
sm.ABBapexTemp.plot()
plt.show()
plt.figure()
sm.HBB2minNENestimateNo2ch1[0].plot()
sm.HBB2minNENestimateNo2ch1[-1].plot()
plt.show()

