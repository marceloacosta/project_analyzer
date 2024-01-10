import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
df = pd.read_csv('Summary_Per_Assignee.csv')  # Replace with the path to your CSV file

# Exclude assignees with 0 efficiency ratio
df_filtered_efficiency = df[df['Efficiency Ratio'] > 0].sort_values('Efficiency Ratio')
# Identify the assignee with the minimum non-zero efficiency ratio
min_efficiency_assignee = df_filtered_efficiency['Efficiency Ratio'].idxmin()

# Assign colors
colors_efficiency = ['red' if x == df_filtered_efficiency.loc[min_efficiency_assignee, 'Efficiency Ratio'] else 'grey' for x in df_filtered_efficiency['Efficiency Ratio']]

# Visualization 1: Efficiency Ratio per Assignee (excluding 0 values)
plt.figure(figsize=(10, 6))
sns.barplot(x='Efficiency Ratio', y='Assignee', data=df_filtered_efficiency, palette=colors_efficiency)
plt.title('Efficiency Ratio per Assignee (Excluding Zero Values)')
plt.xlabel('Efficiency Ratio')
plt.ylabel('Assignee')
plt.show()

# Visualization 2: Bugs to Issues Ratio per Assignee
# Sorting the DataFrame based on 'Bugs to Issues Ratio'
df_sorted_bugs_issues = df.sort_values('Bugs to Issues Ratio', ascending=False)
# Identify the index of the maximum bugs to issues ratio
max_bugs_issues_index = df_sorted_bugs_issues['Bugs to Issues Ratio'].idxmax()
# Assign colors
colors_bugs_issues = ['red' if i == max_bugs_issues_index else 'grey' for i in df_sorted_bugs_issues.index]
plt.figure(figsize=(12, 8))
sns.barplot(x='Bugs to Issues Ratio', y='Assignee', data=df_sorted_bugs_issues, palette=colors_bugs_issues)
plt.title('Bugs to Issues Ratio per Assignee')
plt.xlabel('Bugs to Issues Ratio')
plt.ylabel('Assignee')
plt.tight_layout()
plt.show()


# Creating a pie chart for the distribution of hours spent by assignee

# Exclude assignees with 0 hours spent
df_filtered = df[df['Total Time Spent (hours)'] > 0]

# Creating a pie chart for the distribution of hours spent by assignee (excluding 0 hours)
plt.figure(figsize=(10, 8))
plt.pie(df_filtered['Total Time Spent (hours)'], labels=df_filtered['Assignee'], autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
plt.title('Distribution of Total Hours Spent by Assignee (Excluding Zero Hours)')
plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
plt.show()
