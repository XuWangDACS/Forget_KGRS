import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 假设df是您的DataFrame

df = pd.read_csv("results_table/comparison_ndcg.csv")

opts = ['ETD', 'SEP', 'LIR']  # 根据需要添加其他opt
metrics = ['Original', 'LM', 'WSC']  # 定义metrics

fig, ax = plt.subplots()
x_pos = np.arange(len(opts))  # x轴位置
width = 0.25  # 条形宽度

# 计算每种opt下不同alpha值的平均值及区间
for i, metric in enumerate(metrics):
    means = [df[f'{opt}_{metric}'].mean() for opt in opts]  # 计算每个opt的平均值
    ax.bar(x_pos + i*width, means, width, label=metric)

# 设置图表元素
ax.set_xlabel('Opt')
ax.set_ylabel('Mean Value')
ax.set_title('Mean Values for Each Opt by Metric')
ax.set_xticks(x_pos + width / len(metrics))
ax.set_xticklabels(opts)
ax.legend()

plt.tight_layout()
plt.show()