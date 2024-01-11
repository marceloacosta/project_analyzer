import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import numpy as np

st.set_option('deprecation.showPyplotGlobalUse', False)



# Function to process data and create CSV files
def process_data(uploaded_file):


    

    # Load the data

    jira_data = pd.read_csv(uploaded_file)

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
    return assignee_summary, filtered_issues




    # Your existing code from app.py goes here
    # Replace file loading with 'uploaded_file'
    # Instead of saving CSVs to files, return them as DataFrames

# Function to create visualizations
def create_visuals(assignee_summary):
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    df = assignee_summary

   
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
    st.pyplot()

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
    st.pyplot()


    # Creating a pie chart for the distribution of hours spent by assignee

    # Exclude assignees with 0 hours spent
    df_filtered = df[df['Total Time Spent (hours)'] > 0]

    # Creating a pie chart for the distribution of hours spent by assignee (excluding 0 hours)
    plt.figure(figsize=(10, 8))
    plt.pie(df_filtered['Total Time Spent (hours)'], labels=df_filtered['Assignee'], autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.title('Distribution of Total Hours Spent by Assignee (Excluding Zero Hours)')
    plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
    st.pyplot()

    # Instead of plt.show(), use st.pyplot()

# Streamlit app layout
def main():
    st.title("Dev Performance Analyzer Z")

    # File upload widget
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    if uploaded_file is not None:
        # Process uploaded file
        summary_df, issues_df = process_data(uploaded_file)

        # Display tables
        st.subheader("Summary Table")
        st.dataframe(summary_df)  # Use st.table if you prefer a static table

        st.subheader("Issues Close to Estimate")
        st.dataframe(issues_df)  # Use st.table if you prefer a static table

        # Display download links for CSV files
        st.download_button('Download Summary CSV', summary_df.to_csv(), file_name='summary.csv')
        st.download_button('Download Issues CSV', issues_df.to_csv(), file_name='issues.csv')

        # Create and display visualizations
        create_visuals(summary_df)

if __name__ == "__main__":
    main()
