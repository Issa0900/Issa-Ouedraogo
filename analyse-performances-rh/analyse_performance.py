import pandas as pd
import numpy as np

pd.set_option('display.width', 140)
pd.set_option('display.max_columns', 50)

df = pd.read_csv('data/HRDataset_v14.csv', encoding='utf-8-sig')

print("=== SHAPE ===")
print(df.shape)

# Nettoyage
df['Department'] = df['Department'].str.strip()
df['ManagerName'] = df['ManagerName'].str.strip()

numeric_cols = ['EngagementSurvey', 'EmpSatisfaction', 'SpecialProjectsCount',
                 'Absences', 'DaysLateLast30', 'Salary', 'PerfScoreID']

print("\n=== STATS DESCRIPTIVES ===")
desc = df[numeric_cols].describe().T
desc['median'] = df[numeric_cols].median()
desc['mode'] = df[numeric_cols].mode().iloc[0]
desc['variance'] = df[numeric_cols].var()
desc['skew'] = df[numeric_cols].skew()
print(desc[['mean','median','mode','std','variance','min','25%','50%','75%','max','skew']].round(2))

print("\n=== REPARTITION PerformanceScore ===")
perf_counts = df['PerformanceScore'].value_counts()
perf_pct = df['PerformanceScore'].value_counts(normalize=True).mul(100).round(1)
print(pd.concat([perf_counts, perf_pct], axis=1, keys=['n','%']))

print("\n=== PERFORMANCE MOYENNE PAR DEPARTEMENT (EngagementSurvey) ===")
dept_perf = df.groupby('Department').agg(
    n=('EmpID','count'),
    engagement_moy=('EngagementSurvey','mean'),
    satisfaction_moy=('EmpSatisfaction','mean'),
    absences_moy=('Absences','mean'),
    retard_moy=('DaysLateLast30','mean'),
    salaire_moy=('Salary','mean')
).round(2).sort_values('engagement_moy', ascending=False)
print(dept_perf)

print("\n=== DETECTION OUTLIERS (regle 1.5*IQR) ===")
def iqr_outliers(series, name):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5*iqr
    upper = q3 + 1.5*iqr
    mask = (series < lower) | (series > upper)
    return {
        'variable': name, 'Q1': round(q1,2), 'Q3': round(q3,2), 'IQR': round(iqr,2),
        'borne_inf': round(lower,2), 'borne_sup': round(upper,2),
        'nb_outliers': int(mask.sum()), 'pct_outliers': round(mask.sum()/len(series)*100,2)
    }, mask

outlier_summary = []
outlier_masks = {}
for col in ['Salary','Absences','DaysLateLast30','EngagementSurvey','SpecialProjectsCount']:
    res, mask = iqr_outliers(df[col], col)
    outlier_summary.append(res)
    outlier_masks[col] = mask

outlier_df = pd.DataFrame(outlier_summary)
print(outlier_df)

print("\n=== DETAIL OUTLIERS SALAIRE (top) ===")
sal_out = df.loc[outlier_masks['Salary'], ['Employee_Name','Position','Department','Salary','PerformanceScore']].sort_values('Salary', ascending=False)
print(sal_out)

print("\n=== DETAIL OUTLIERS RETARDS (DaysLateLast30) ===")
late_out = df.loc[outlier_masks['DaysLateLast30'], ['Employee_Name','Department','DaysLateLast30','Absences','PerformanceScore','EngagementSurvey']]
print(late_out)

print("\n=== DETAIL OUTLIERS ABSENCES ===")
abs_out = df.loc[outlier_masks['Absences'], ['Employee_Name','Department','Absences','PerformanceScore']]
print(abs_out)
print(f"(n={len(abs_out)})")

print("\n=== CORRELATION variables cles ===")
corr_cols = ['Salary','EngagementSurvey','EmpSatisfaction','Absences','DaysLateLast30','SpecialProjectsCount','PerfScoreID']
print(df[corr_cols].corr().round(2))

print("\n=== PerfScore vs Termd (taux de depart) ===")
print(pd.crosstab(df['PerformanceScore'], df['Termd'], normalize='index').mul(100).round(1))

print("\n=== PerfScore vs Absences/Retards moyens ===")
print(df.groupby('PerformanceScore')[['Absences','DaysLateLast30','EngagementSurvey','EmpSatisfaction']].mean().round(2))
