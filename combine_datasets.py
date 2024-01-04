import pandas as pd

# Define the file paths for the three CSV files
file1_path = 'data/Autism_Parenting_Venting-Needs-Support_Advice-Needed_no_comments.csv'
file2_path = 'data/Autism_Parenting_Venting-Needs-Support_Advice-Needed_no_comments(hot).csv'
file3_path = 'data/Autism_Parenting_Venting-Needs-Support_Advice-Needed_no_comments(new).csv'

# Read each CSV file into a pandas DataFrame
df1 = pd.read_csv(file1_path)
df2 = pd.read_csv(file2_path)
df3 = pd.read_csv(file3_path)

# Concatenate the DataFrames
combined_df = pd.concat([df1, df2, df3])

# Drop duplicates based on Title, Selftext, and Timestamp
combined_df.drop_duplicates(subset=['Title', 'Selftext', 'Timestamp'], inplace=True)

# Write the final DataFrame to a new CSV file
final_file_path = 'data/Autism_Parenting_Venting-Needs-Support_Advice-Needed_no_comments(combined).csv'
combined_df.to_csv(final_file_path, index=False)

print(f"Combined CSV file saved to {final_file_path}")
