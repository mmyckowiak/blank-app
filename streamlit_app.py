import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Page Configuration
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# importing data
data = pd.read_csv('/workspaces/blank-app/healthcare_fraud_detection.csv')
data = pd.DataFrame(data)
print(data)

# cleaning column names and data types
columns = data.columns.str.replace('_', ' ')
data.columns = columns
data['Procedure Code'] = data['Procedure Code'].astype(str)

# limiting claims to florida
florida_claims = data[data['Patient State'] == 'FL']
florida_claims = florida_claims.dropna(subset=['Insurance Type'])

# shortening data set
short_florida_claims = florida_claims[['Patient Age', 'Patient Gender','Diagnosis Code', 'Procedure Code', 'Insurance Type', 'Claim Amount', 'Approved Amount', 'Provider Specialty']]

# appending the approved/claim ratio to our dataset
short_florida_claims['Approved/Claim Ratio'] = short_florida_claims['Approved Amount'] / short_florida_claims['Claim Amount']

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
st.sidebar.header('Dashboard `version 2`')

st.sidebar.subheader('Pie Chart Parameter')
insurance_type = st.sidebar.selectbox('Select Data', ('Medicare', 'Medicaid', 'Private')) 

filtered = short_florida_claims[short_florida_claims['Insurance Type'] == insurance_type]
procedure_code = st.sidebar.selectbox(
    "Select Procedure Code",
    sorted(filtered["Procedure Code"].unique())
)

proc_filtered = filtered[filtered["Procedure Code"] == procedure_code]
total_claimed = proc_filtered["Claim Amount"].sum()
total_approved = proc_filtered["Approved Amount"].sum()

pie_data = pd.DataFrame({
    "Category": ["Total Claimed Amount", "Total Approved Amount"],
    "Amount": [total_claimed, total_approved]
})

# st.sidebar.subheader('Donut chart parameter')
# donut_theta = st.sidebar.selectbox('Select data', ('q2', 'q3'))

# st.sidebar.subheader('Line chart parameters')
# plot_data = st.sidebar.multiselect('Select data', ['temp_min', 'temp_max'], ['temp_min', 'temp_max'])
# plot_height = st.sidebar.slider('Specify plot height', 200, 500, 250)

st.title("Healthcare Dashboard")

# beginning metric code (average age, most common procedure code, total claim amount, total approved amount)
average_age = short_florida_claims['Patient Age'].mean().round();
average_age = average_age.astype(int);

common_procedure = short_florida_claims['Procedure Code'].mode()[0]
# common_procedure = print(common_procedure);

total_amount_claim = short_florida_claims['Claim Amount'].sum().round()
total_amount_claim = total_amount_claim.astype(int);

total_amount_approved = short_florida_claims['Approved Amount'].sum().round()
total_amount_approved = total_amount_approved.astype(int);

# finding the average approved/claimed amount per procedure code per insurance
grouped_mean = short_florida_claims.groupby(['Procedure Code', 'Insurance Type'])['Approved/Claim Ratio'].mean().unstack()

# limiting insurance to medicaid and procedure code to 93000
# medicaid = short_florida_claims[(short_florida_claims['Insurance Type'] == 'Medicaid') & (short_florida_claims['Procedure Code'] == 93000)].reset_index(drop = False)


# Row A
st.markdown('### Metrics')

col1, col2, col3, col4 = st.columns(4)

col1.metric("Average Age", average_age)
col2.metric("Most Common Procedure", common_procedure)
col3.metric("Total Claimed Amount", total_amount_claim)
col4.metric("Total Approved Amount", total_amount_approved)


# Row B
col21, col22 = st.columns(2)
st.markdown('## Average Approved/Claim Ratio by Procedure Code and Insurance Type')
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(grouped_mean, annot = True, fmt = '.2f', cmap = 'Blues', ax = ax)
ax.set_title('Average Approved/Claim Ratio by Procedure Code and Insurance Type')
ax.set_xlabel('Insurance Type')
ax.set_ylabel('Procedure Code')
ax.set_yticklabels(['99214', '99213', '97110', '93000', '87086', '85025', '80053', '71046', '36415'], rotation = 45)
col21.pyplot(fig)

## Time of approved/claimed with differing insurance types

# Total claimed vs. total approved per insurance type and procedure code (pie chart)

# Pie Chart 
with col22:
    st.markdown(f"## Claim vs. Approved Amount for {insurance_type}")

    fig, ax = plt.subplots(figsize=(5,5))
    ax.pie(
        pie_data["Amount"],
        labels = pie_data["Category"],
        autopct = "%1.1f%%",
        startangle = 90
    )
    ax.axis("equal")
    st.pyplot(fig)
