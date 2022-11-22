from matplotlib import pyplot as plt
import numpy as np

with plt.style.context('science'):
    fig, axs = plt.subplots(1, 2, figsize=(3.5, 2.625))
    axs = axs.flatten()

    img = plt.imread("fig5-diagram.png")
    axs[0].imshow(img)
    axs[0].tick_params(axis='x', which='both', bottom=False, top=False)
    axs[0].tick_params(axis='y', which='both', left=False, right=False)
    axs[0].axis('off')

    R = 1
    r = np.linspace(R+.01,10*R)
    P_diffusion = np.ones_like(r)
    P_ballistic = (1/np.pi)*np.arcsin(R/r)
    axs[1].plot(r/R,P_diffusion,'-k')
    axs[1].plot(r/R,P_ballistic,'-r')
    axs[1].set_xlabel('r/R')
    axs[1].set_ylabel(r'$\varepsilon$')

    axs[0].text(-0.25, 0.95, 'a', transform=axs[0].transAxes)
    axs[1].text(-0.33, 0.95, 'b', transform=axs[1].transAxes)

    fig.savefig('new-fig5', dpi=300)