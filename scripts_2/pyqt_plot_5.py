"""
Created on Mon Dec 07 16:34:10 2015

@author: SuperWang
"""

import matplotlib.pyplot as plt
import numpy as np

fig,ax=plt.subplots()


y1=[]
y2=[]

for i in range(50):
    y1.append(np.sin(i))
    y2.append(np.cos(i))
    ax.cla()
    ax.set_title("Loss")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Loss")
    ax.set_xlim(0,55)
    ax.set_ylim(-1,1)
    ax.grid()
    ax.plot(y1,label='train')
    ax.plot(y2,label='test')
    ax.legend(loc='best')
    plt.pause(0.1)

plt.show()

    