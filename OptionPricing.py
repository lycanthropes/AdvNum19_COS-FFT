#!/usr/bin/env python
# coding: utf-8

# In[1]: Packages, Settings

import numpy as np
import AllFunctions as func
np.seterr(divide='ignore', invalid='ignore')


# In[2]: Inputs for Option
r     = 0          # risk-free rate
mu    = r          # model parameters
sigma = 0.15    
S0    = 100        # Today's stock price
tau   = 30 / 365   # Time to expiry in years
q     = 0
K     = np.arange(70, 131, dtype = np.float) #np.arange(100, 101, dtype = np.float) #np.arange(70, 131, dtype = np.float)


# In[3]: Black Scholes Option Pricing
C_BS, p, d1, d2 = func.blackS(S0, K, r, tau, sigma, q)
print (C_BS)


# In[4]: Inputs for COS-FFT Method (suffcient for BS Char Func)
scalea = -30 # how many standard deviations?
scaleb = 30 
a      = scalea*np.sqrt(tau)*sigma # -0.18382155830867142 #
b      = scaleb*np.sqrt(tau)*sigma # 0.18359029259206172 #
bma    = b-a
N      = 50
k      = np.arange(2**10) #np.arange(0, N, dtype=np.float)
u      = k*np.pi/bma


# In[5]: COS-FFT Value Function for Call
Uk = 2 / bma * ( func.cosSerExp(a,b,0,b,k) - func.cosSer1(a,b,0,b,k) )


# In[6]: COS-FFT with BS-Characterstic Function
charactersticFunction = func.charFuncBSM(u, mu, sigma, tau)

C_COS = np.zeros((np.size(K)))

for m in range(0,np.size(K)):
    x  = np.log(S0/K[m])
    addIntegratedTerm = np.exp(1j*k*np.pi*(x-a)/bma) # not needed unter Heston (is already included) could be moved out (see Fang p.22)
    Fk = np.real(np.multiply(charactersticFunction, addIntegratedTerm))
    Fk[0]=0.5*Fk[0] # weigh first term 1/2
    C_COS[m] = K[m] * np.sum(np.multiply(Fk,Uk)) * np.exp(-r*tau)
    
print (C_COS)


# In[7]: Inputs for COS-FFT Method (Necessary for Heston Char Func)
# All values according to Fang Osterle 2008 
#u      = k * np.pi / bma  # Input into phi
u      = k[:, np.newaxis] * np.pi / bma
u      = u.reshape((k.size,))
u0     = sigma                # Initial Vola of underyling at time 0 (called "a" in original paper)
bj     = 1.5768             # The speed of mean reversion also called lambda in Fang Paper; original Paper: b1 =kappa+lam-rho*sigma
v_bar  = 0.0398             # Also called u-bar, Mean level of variance of the underlying
uj     = 0.5                # In the original paper it is 0.5 and -0.5 -> *2 equals 1, so may be not relevant (not included in Fang papr)
volvol = 0.5751             # Volatility of the volatiltiy process (if 0 then constant Vol like BS)
rho    = -0.5711            # Covariance between the log stock and the variance process


# In[8]:Fang Oosterle Version of Heston
charactersticFunction = func.charFuncHestonFO(mu, r, u, tau, u0, bj, uj, rho, volvol)

C_COS_HFO = np.zeros((np.size(K)))

for m in range(0, np.size(K)):
    #x  = np.log(S0/K[m])
    #addIntegratedTerm = np.exp(-1j*k*np.pi*(x-a)/bma)
    x = np.log(K[m]/S0)
    addIntegratedTerm = np.exp(-1j*k*np.pi*(x+a)/bma)
    
    Fk = np.real(charactersticFunction * addIntegratedTerm)
    Fk[0] = 0.5 * Fk[0]						# weigh first term 1/2
    C_COS_HFO[m] = K[m] * np.sum(np.multiply(Fk, Uk)) * np.exp(-r * tau)
    #C_COS_HFO[m] = K[m] * np.dot(Fk, Uk) * np.exp(-r * tau)

print(C_COS_HFO)

## End