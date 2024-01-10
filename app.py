import pandas as pd
import numpy as np

# Load the data
file_path = 'data.csv'  # Replace with your actual file path
jira_data = pd.read_csv(file_path)

# Filter for Story and Bug issue types and fill NaN values
stories = jira_data[jira_data['Issue Type'] == 'Story'].copy()
bugs = jira_data[jira_data['Issue Type'] == 'Bug'].copy()
stories.fillna({'Original estimate': 0, 'Time Spent': 0}, inplace=True)
bugs.fillna({'Time Spent': 0}, inplace=True)

# Prepare columns for linking stories and bugs
bug_link_columns = ['Outward issue link (Blocks)', 'Outward issue link (Problem/Incident)']
bugs['Linked Issue Keys'] = bugs[bug_link_columns].apply(lambda x: ','.join(x.dropna().astype(str)), axis=1)

# ... [previous parts of the script] ...

# Summarize the number of bugs per linked issue
bugs_summary = bugs.groupby('Linked Issue Keys').size().reset_index(name='Number of Bugs')

# Include all stories and bugs in the summary, regardless of whether they have linked issues
story_assignees = stories[['Issue key', 'Assignee']].rename(columns={'Issue key': 'Linked Issue Keys'})
bugs_summary = story_assignees.merge(bugs_summary, on='Linked Issue Keys', how='left').fillna({'Number of Bugs': 0})

# Group by assignee to get the summary of stories and their resulting bugs
assignee_summary = bugs_summary.groupby('Assignee').agg({
    'Linked Issue Keys': 'count',
    'Number of Bugs': 'sum'
}).rename(columns={'Linked Issue Keys': 'Issues Linked'}).reset_index()

# ... [rest of the script with new analysis columns] ...


# Creating a list of all assignees
all_assignees = pd.concat([stories['Assignee'], bugs['Assignee']]).unique()

# Initializing an empty DataFrame for the summary
assignee_summary = pd.DataFrame(all_assignees, columns=['Assignee'])

# Summarize the number of bugs per linked issue
bugs_summary = bugs.groupby('Linked Issue Keys').size().reset_index(name='Number of Bugs')

# Include all stories and bugs in the summary, regardless of whether they have linked issues
story_assignees = stories[['Issue key', 'Assignee']].rename(columns={'Issue key': 'Linked Issue Keys'})
merged_summary = story_assignees.merge(bugs_summary, on='Linked Issue Keys', how='left').fillna({'Number of Bugs': 0})

# Group by assignee to get the summary of stories and their resulting bugs
grouped_summary = merged_summary.groupby('Assignee').agg({
    'Linked Issue Keys': 'count',
    'Number of Bugs': 'sum'
}).rename(columns={'Linked Issue Keys': 'Issues Linked'})

# Update assignee_summary with the grouped data
assignee_summary = assignee_summary.merge(grouped_summary, on='Assignee', how='left').fillna({'Issues Linked': 0, 'Number of Bugs': 0})



# Calculations for each assignee
assignee_summary['Sum of Original Estimated Time (hours)'] = assignee_summary['Assignee'].apply(
    lambda x: stories[stories['Assignee'] == x]['Original estimate'].sum() / 3600
).round(1)

assignee_summary['Sum of Time Spent on Stories (hours)'] = assignee_summary['Assignee'].apply(
    lambda x: stories[stories['Assignee'] == x]['Time Spent'].sum() / 3600
).round(1)

assignee_summary['Sum of Time Spent on Bugs (hours)'] = assignee_summary['Assignee'].apply(
    lambda x: bugs[bugs['Assignee'] == x]['Time Spent'].sum() / 3600
).round(1)

assignee_summary['Total Time Spent (hours)'] = (
    assignee_summary['Sum of Time Spent on Stories (hours)'] + assignee_summary['Sum of Time Spent on Bugs (hours)']
).round(1)

# Add the new analysis columns as before...
# Add the new analysis columns

# Efficiency Ratio
assignee_summary['Efficiency Ratio'] = assignee_summary['Sum of Original Estimated Time (hours)'] / assignee_summary['Total Time Spent (hours)']

# Bugs to Issues Ratio
# Handling cases where 'Issues Linked' is zero to avoid division by zero
assignee_summary['Bugs to Issues Ratio'] = assignee_summary['Number of Bugs'] / assignee_summary['Issues Linked'].replace(0, 1)

# Average Time per Bug
# Handling cases where 'Number of Bugs' is zero to avoid division by zero
assignee_summary['Average Time per Bug (hours)'] = assignee_summary['Sum of Time Spent on Bugs (hours)'] / assignee_summary['Number of Bugs'].replace(0, 1)

# Average Time per Issue
# Handling cases where 'Issues Linked' is zero to avoid division by zero
assignee_summary['Average Time per Issue (hours)'] = assignee_summary['Sum of Time Spent on Stories (hours)'] / assignee_summary['Issues Linked'].replace(0, 1)

# Proportion of Time Spent on Bugs vs Stories
assignee_summary['Proportion on Bugs (%)'] = (assignee_summary['Sum of Time Spent on Bugs (hours)'] / assignee_summary['Total Time Spent (hours)']) * 100
assignee_summary['Proportion on Stories (%)'] = (assignee_summary['Sum of Time Spent on Stories (hours)'] / assignee_summary['Total Time Spent (hours)']) * 100

# Handling NaN and infinite values resulting from division by zero
assignee_summary.replace([float('inf'), -float('inf'), np.nan], 0, inplace=True)

# ... [rest of the script for saving the file and printing the message] ...

# Save the summary to a new CSV file
summary_file_path = 'Summary_Per_Assignee.csv'
assignee_summary.to_csv(summary_file_path, index=False)

print(f'Summary per assignee saved to {summary_file_path}')



# Combine stories and bugs data
combined_data = pd.concat([stories, bugs])

# Convert 'Original estimate' and 'Time Spent' to hours
combined_data['Original estimate'] = combined_data['Original estimate'] / 3600
combined_data['Time Spent'] = combined_data['Time Spent'] / 3600

# Calculate the percentage of Time Spent vs Original Estimate
combined_data['Percentage'] = (combined_data['Time Spent'] / combined_data['Original estimate']) * 100

# Filter for issues where Time Spent is 80% or more of Original Estimate and Resolution is not 'Done'
filtered_issues = combined_data[(combined_data['Percentage'] >= 80) & (combined_data['Status'] != 'Done')]

# Selecting the relevant columns
relevant_columns = ['Assignee', 'Issue key', 'Status', 'Original estimate', 'Time Spent', 'Percentage']
filtered_issues = filtered_issues[relevant_columns]

# Save to a new CSV file
filtered_issues_file_path = 'Issues_Close_To_Estimate.csv'
filtered_issues.to_csv(filtered_issues_file_path, index=False)

print(f'Issues close to estimate saved to {filtered_issues_file_path}')


