import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import matplotlib.cm as cm

georgia_font_path = './configs/Georgia.ttf' 
fm.fontManager.addfont(georgia_font_path)
plt.rcParams['font.family'] = 'Georgia' 
plt.rcParams['font.size'] = 18  
plt.rcParams['axes.labelsize'] = 18  
plt.rcParams['xtick.labelsize'] = 15 
plt.rcParams['ytick.labelsize'] = 15 
plt.rcParams['legend.fontsize'] = 17 
plt.rcParams['axes.titlesize'] = 18 
colormap = cm.get_cmap('viridis')
# colormap = cm.get_cmap('Blues')
