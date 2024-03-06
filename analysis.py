import pandas as pd
import matplotlib.pyplot as plt

folder1 = "iforget_LM_results/ml1m/agent_topk=25-50-1"
folder2 = "iforget_WSC_results/ml1m/agent_topk=25-50-1"
folder0 = "original_results/ml1m/agent_topk=25-50-1"

opt_dict = {
    "ETD": "ETDopt_moving_alpha_avg.csv",
    "SEP": "SEPopt_moving_alpha_avg.csv",
    "LIR": "LIRopt_moving_alpha_avg.csv",
    "ETD_LIR": "ETD_LIR_opt_moving_alpha_avg.csv",
    "SEP_LIR": "SEP_LIR_opt_moving_alpha_avg.csv",
    "ETD_SEP": "ETD_SEP_opt_moving_alpha_avg.csv",
    "ETD_SEP_LIR": "ETD_SEP_LIR_opt_moving_alpha_avg.csv"
}

metrics = ["ndcg", "hr", "recall", "precision", "LIR", "SEP","ETD"]

for opt in opt_dict.keys():
    df0 = pd.read_csv(f"{folder0}/{opt_dict[opt]}",header=0)
    df1 = pd.read_csv(f"{folder1}/{opt_dict[opt]}",header=0)
    df2 = pd.read_csv(f"{folder2}/{opt_dict[opt]}",header=0)
    
    for metric in metrics:
        # plt.figure(figsize=(10, 6))
        df_metric0 = df0[df0["metric"] == metric]
        df_metric0 = df_metric0[df_metric0["group"] == 'Overall']
        df_metric1 = df1[df1["metric"] == metric]
        df_metric1 = df_metric1[df_metric1["group"] == 'Overall']
        df_metric2 = df2[df2["metric"] == metric]
        df_metric2 = df_metric2[df_metric2["group"] == 'Overall']
        plt.plot(df_metric0["alpha"],df_metric0["data"], label=f"Original_{metric}",color='red')
        plt.plot(df_metric1["alpha"],df_metric1["data"], label=f"LM_{metric}",color='green')
        plt.plot(df_metric2["alpha"],df_metric2["data"], label=f"WSC_{metric}",color='blue')
        plt.title(f"OPT: {opt} - Metric: {metric}")
        plt.legend()
        plt.savefig(f'results_pic/{opt}_scores_{metric}.png')
        plt.clf()



for metric in metrics:
    metric_comparison_df = pd.DataFrame()

    for opt in opt_dict.keys():
        df0 = pd.read_csv(f"{folder0}/{opt_dict[opt]}", header=0)
        df1 = pd.read_csv(f"{folder1}/{opt_dict[opt]}", header=0)
        df2 = pd.read_csv(f"{folder2}/{opt_dict[opt]}", header=0)
        df_metric0 = df0[(df0["metric"] == metric) & (df0["group"] == 'Overall')][['alpha', 'data']].rename(columns={'data': f'{opt}_Original'})
        df_metric1 = df1[(df1["metric"] == metric) & (df1["group"] == 'Overall')][['alpha', 'data']].rename(columns={'data': f'{opt}_LM'})
        df_metric2 = df2[(df2["metric"] == metric) & (df2["group"] == 'Overall')][['alpha', 'data']].rename(columns={'data': f'{opt}_WSC'})
        if metric_comparison_df.empty:
            metric_comparison_df = df_metric0.merge(df_metric1, on='alpha').merge(df_metric2, on='alpha')
        else:
            merged_df = df_metric0.merge(df_metric1, on='alpha').merge(df_metric2, on='alpha')
            metric_comparison_df = metric_comparison_df.merge(merged_df, on='alpha', how='outer')
    cols_to_format = metric_comparison_df.columns.drop('alpha')
    metric_comparison_df[cols_to_format] = metric_comparison_df[cols_to_format].applymap(lambda x: f"{x:.4f}")
    metric_comparison_df.reset_index(drop=True, inplace=True)
    metric_comparison_df.to_csv(f'results_table/comparison_{metric}.csv', index=False)

for metric in metrics:
    metric_comparison_df = pd.DataFrame()

    for opt in opt_dict.keys():
        df0 = pd.read_csv(f"{folder0}/{opt_dict[opt]}", header=0)
        df1 = pd.read_csv(f"{folder1}/{opt_dict[opt]}", header=0)
        df2 = pd.read_csv(f"{folder2}/{opt_dict[opt]}", header=0)

        df_metric0 = df0[(df0["metric"] == metric) & (df0["group"] == 'Overall')][['alpha', 'data']].rename(columns={'data': f'{opt}_Original'})
        df_metric1 = df1[(df1["metric"] == metric) & (df1["group"] == 'Overall')][['alpha', 'data']].rename(columns={'data': f'{opt}_LM'})
        df_metric2 = df2[(df2["metric"] == metric) & (df2["group"] == 'Overall')][['alpha', 'data']].rename(columns={'data': f'{opt}_WSC'})

        merged_df = df_metric0.merge(df_metric1, on='alpha').merge(df_metric2, on='alpha')

        merged_df[f'{opt}_LM'] = ((merged_df[f'{opt}_LM'] / merged_df[f'{opt}_Original']) * 100).round(2)
        merged_df[f'{opt}_WSC'] = ((merged_df[f'{opt}_WSC'] / merged_df[f'{opt}_Original']) * 100).round(2)
        merged_df[f'{opt}_Original'] = 100

        if metric_comparison_df.empty:
            metric_comparison_df = merged_df
        else:
            metric_comparison_df = metric_comparison_df.merge(merged_df, on='alpha', how='outer')

    metric_comparison_df.reset_index(drop=True, inplace=True)

    metric_comparison_df.to_csv(f'results_table/{metric}_comparison_percentage.csv', index=False)
    with open("results_table/latex.txt", 'a+') as f:
        f.write(f"\\subsection*{{{metric}}}\n")
        f.write(metric_comparison_df.to_latex(index=False, float_format="%.2f"))
        f.write("\n")

for metric in metrics:
    metric_comparison_df = pd.DataFrame()

    for opt in opt_dict.keys():
        df0 = pd.read_csv(f"{folder0}/{opt_dict[opt]}", header=0)
        df1 = pd.read_csv(f"{folder1}/{opt_dict[opt]}", header=0)
        df2 = pd.read_csv(f"{folder2}/{opt_dict[opt]}", header=0)

        df_metric0 = df0[(df0["metric"] == metric) & (df0["group"] == 'Overall')][['alpha', 'data']].rename(columns={'data': f'{opt}_Original'})
        df_metric1 = df1[(df1["metric"] == metric) & (df1["group"] == 'Overall')][['alpha', 'data']].rename(columns={'data': f'{opt}_LM'})
        df_metric2 = df2[(df2["metric"] == metric) & (df2["group"] == 'Overall')][['alpha', 'data']].rename(columns={'data': f'{opt}_WSC'})

        merged_df = df_metric0.merge(df_metric1, on='alpha').merge(df_metric2, on='alpha')

        merged_df[f'{opt}_LM'] = ((merged_df[f'{opt}_LM'] / merged_df[f'{opt}_Original']) * 100).round(2) -100
        merged_df[f'{opt}_WSC'] = ((merged_df[f'{opt}_WSC'] / merged_df[f'{opt}_Original']) * 100).round(2) -100
        merged_df[f'{opt}_Original'] = 100

        if metric_comparison_df.empty:
            metric_comparison_df = merged_df
        else:
            metric_comparison_df = metric_comparison_df.merge(merged_df, on='alpha', how='outer')

    metric_comparison_df.reset_index(drop=True, inplace=True)

    metric_comparison_df.to_csv(f'results_table/{metric}_comparison_percentage.csv', index=False)
    with open("results_table/latex.txt", 'a+') as f:
        f.write(f"\\subsection*{{{metric}}}\n")
        f.write(metric_comparison_df.to_latex(index=False, float_format="%.2f"))
        f.write("\n")