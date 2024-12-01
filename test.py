import plotext as plt
import time
import numpy as np
t = 0
# plt.interactive(True)   
plt.plotsize(50, 15)
plt.theme("pro")
# while True:
t +=1
x = np.linspace(0, 1, 100)
y = np.sin(2 * np.pi * x+t)
plt.clear_data()
plt.clear_terminal() 
plt.plot(y,marker="braille")
print(plt.build())
    # time.sleep(1)