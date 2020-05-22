import matplotlib.pyplot as plt
import numpy as np
# import seaborn as sns

# sns.set()

values = np.genfromtxt('win_fast_values.csv', delimiter=',')
rewards = np.genfromtxt('win_fast_rewards.csv', delimiter=',')

value_mean, value_std = np.mean(values,axis=0), np.std(values,axis=0)
reward_mean, reward_std = np.mean(rewards,axis=0), np.std(rewards,axis=0)

normed_values = (values - value_mean)/value_std
normed_rewards = (rewards - reward_mean)/reward_std

fig1, (ax1, ax2) = plt.subplots(2,1, True)
c1 = ax1.pcolor(normed_values)
ax1.set_title('values')
ax1.set_ylabel('action index')
c2 = ax2.pcolor(normed_rewards)
ax2.set_title('rewards')
ax2.set_xlabel('depth from start (episode steps)')
ax2.set_ylabel('action index')
fig1.subplots_adjust(right=0.8)
cbar_ax = fig1.add_axes([0.85, 0.15, 0.05, 0.7])
fig1.colorbar(c1, cax=cbar_ax)
plt.suptitle('win_fast: normalized color plot for action values vs depth from start')
plt.legend()  
plt.show()                                                      

# fig2, (ax1,ax2) = plt.subplots(1, 2,sharey=True)
# fig2 = plt.figure(2)
# plt.boxplot(values)
# plt.plot(list(range(1,len(value_mean)+1)),value_mean, label='values')
# plt.boxplot(rewards)
# plt.plot(list(range(1,len(reward_mean)+1)),reward_mean, label='rewards')
# plt.title('win_fast: boxplot of rewards and values vs depth from start')
# plt.legend()
# plt.xlabel('depth from start')
# plt.show()
