import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 天气数据
dates = ['1月3日\n周六', '1月4日\n周日', '1月5日\n周一', '1月6日\n周二',
         '1月7日\n周三', '1月8日\n周四', '1月9日\n周五']
weather_conditions = ['晴转多云', '多云转小雨', '阴转多云', '晴', '多云', '晴', '多云']
high_temps = [7, 11, 10, 8, 9, 7, 8]
low_temps = [0, 1, 2, 1, 0, -1, 0]
weather_icons = ['☀️', '🌧️', '☁️', '☀️', '⛅', '☀️', '⛅']

# 创建图表
fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor('#f0f8ff')

# 绘制温度曲线
x = np.arange(len(dates))
ax.plot(x, high_temps, 'o-', linewidth=3, markersize=10, color='#ff6b6b', label='最高温度')
ax.plot(x, low_temps, 's-', linewidth=3, markersize=10, color='#4ecdc4', label='最低温度')

# 填充温度区间
ax.fill_between(x, low_temps, high_temps, alpha=0.2, color='#95e1d3')

# 添加温度标签
for i, (high, low) in enumerate(zip(high_temps, low_temps)):
    ax.text(i, high + 0.5, f'{high}°C', ha='center', va='bottom', fontsize=12, fontweight='bold', color='#ff6b6b')
    ax.text(i, low - 0.5, f'{low}°C', ha='center', va='top', fontsize=12, fontweight='bold', color='#4ecdc4')

# 添加天气图标和描述
for i, (icon, condition) in enumerate(zip(weather_icons, weather_conditions)):
    ax.text(i, 14, icon, fontsize=24, ha='center')
    ax.text(i, 12.5, condition, ha='center', fontsize=11, fontweight='bold')

# 设置x轴
ax.set_xticks(x)
ax.set_xticklabels(dates, fontsize=11)

# 设置y轴
ax.set_ylim(-2, 15)
ax.set_ylabel('温度 (°C)', fontsize=12, fontweight='bold')
ax.set_yticks(range(-2, 16, 2))

# 设置标题
ax.set_title('上海一周天气预报简报', fontsize=20, fontweight='bold', pad=20)

# 添加网格
ax.grid(True, alpha=0.3, linestyle='--')

# 添加图例
legend = ax.legend(loc='upper right', fontsize=12, framealpha=0.9)

# 添加说明文本
fig.text(0.5, 0.02, '数据来源：上海中心气象台 | 更新时间：2026年1月3日',
         ha='center', fontsize=10, style='italic')

# 添加天气提示框
textstr = '本周天气提示：\n• 周日可能有小雨，注意携带雨具\n• 气温较低，注意保暖\n• 空气质量良好，适宜出行'
props = dict(boxstyle='round', facecolor='wheat', alpha=0.3)
ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', bbox=props, family='monospace')

plt.tight_layout()
plt.savefig('D:\\ClaudeWork\\shanghai_weather_report.png', dpi=300, bbox_inches='tight')
print("天气简报已生成：shanghai_weather_report.png")
plt.show()
