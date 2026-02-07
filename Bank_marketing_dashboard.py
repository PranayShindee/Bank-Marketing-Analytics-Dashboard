import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG (MUST BE FIRST)
# --------------------------------------------------
st.set_page_config(
    page_title="Bank Marketing Funnel Dashboard",
    layout="wide"
)

st.title("📊 Bank Marketing Funnel & Conversion Dashboard")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("bank.csv", sep=";")
    for col in ['job', 'marital', 'education', 'contact', 'poutcome', 'y']:
        df[col] = df[col].str.lower()
    return df

df = load_data()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("🔍 Filters")

contact_filter = st.sidebar.multiselect(
    "Select Contact Channel",
    options=df['contact'].unique(),
    default=df['contact'].unique()
)

job_filter = st.sidebar.multiselect(
    "Select Job Type",
    options=df['job'].unique(),
    default=df['job'].unique()
)

filtered_df = df[
    (df['contact'].isin(contact_filter)) &
    (df['job'].isin(job_filter))
]

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------
total_customers = len(filtered_df)
total_conversions = filtered_df[filtered_df['y'] == 'yes'].shape[0]
conversion_rate = (total_conversions / total_customers) * 100 if total_customers else 0

col1, col2, col3 = st.columns(3)
col1.metric("👥 Total Customers", total_customers)
col2.metric("✅ Total Conversions", total_conversions)
col3.metric("📈 Conversion Rate (%)", f"{conversion_rate:.2f}")

# --------------------------------------------------
# FUNNEL ANALYSIS
# --------------------------------------------------
st.subheader("🧩 Marketing Funnel")

funnel_df = pd.DataFrame({
    "Stage": ["Contacted", "Reached", "Interested", "Converted"],
    "Users": [
        len(filtered_df),
        len(filtered_df[filtered_df['contact'] != 'unknown']),
        len(filtered_df[(filtered_df['campaign'] <= 2) | (filtered_df['previous'] > 0)]),
        len(filtered_df[filtered_df['y'] == 'yes'])
    ]
})

fig_funnel = px.funnel(
    funnel_df,
    x="Users",
    y="Stage",
    title="Customer Conversion Funnel"
)

st.plotly_chart(fig_funnel, use_container_width=True)

# --------------------------------------------------
# CHANNEL PERFORMANCE
# --------------------------------------------------
st.subheader("📞 Conversion by Contact Channel")

channel_kpi = (
    filtered_df.groupby('contact')['y']
    .apply(lambda x: (x == 'yes').mean() * 100)
    .reset_index(name="Conversion Rate (%)")
)

fig_channel = px.bar(
    channel_kpi,
    x="contact",
    y="Conversion Rate (%)",
    text_auto=".2f",
    title="Conversion Rate by Channel"
)

st.plotly_chart(fig_channel, use_container_width=True)

# --------------------------------------------------
# CAMPAIGN FATIGUE
# --------------------------------------------------
st.subheader("📉 Campaign Fatigue Analysis")

campaign_kpi = (
    filtered_df.groupby('campaign')['y']
    .apply(lambda x: (x == 'yes').mean() * 100)
    .reset_index(name="Conversion Rate (%)")
)

fig_campaign = px.line(
    campaign_kpi,
    x="campaign",
    y="Conversion Rate (%)",
    markers=True,
    title="Conversion Rate vs Number of Contacts"
)

st.plotly_chart(fig_campaign, use_container_width=True)

# --------------------------------------------------
# AGE GROUP KPI
# --------------------------------------------------
st.subheader("🎯 Conversion by Age Group")

filtered_df['age_group'] = pd.cut(
    filtered_df['age'],
    bins=[18, 30, 40, 50, 60, 100],
    labels=['18-30', '31-40', '41-50', '51-60', '60+']
)

age_kpi = (
    filtered_df.groupby('age_group', observed=False)['y']
    .apply(lambda x: (x == 'yes').mean() * 100)
    .reset_index(name="Conversion Rate (%)")
)

fig_age = px.bar(
    age_kpi,
    x="age_group",
    y="Conversion Rate (%)",
    text_auto=".2f",
    title="Conversion Rate by Age Group"
)

st.plotly_chart(fig_age, use_container_width=True)

# --------------------------------------------------
# JOB ROLE PERFORMANCE
# --------------------------------------------------
st.subheader("👔 Top Job Roles by Conversion")

job_kpi = (
    filtered_df.groupby('job')['y']
    .apply(lambda x: (x == 'yes').mean() * 100)
    .sort_values(ascending=False)
    .head(10)
    .reset_index(name="Conversion Rate (%)")
)

fig_job = px.bar(
    job_kpi,
    x="job",
    y="Conversion Rate (%)",
    text_auto=".2f",
    title="Top 10 Job Roles by Conversion Rate"
)

st.plotly_chart(fig_job, use_container_width=True)

# --------------------------------------------------
# BUSINESS INSIGHTS
# --------------------------------------------------
st.subheader("🧠 Business Insights")

st.markdown("""
- 📈 **Older customers (60+) show the highest conversion rates** — prioritize this segment.
- 📞 **Cellular contact outperforms telephone** — allocate more budget here.
- 🔁 **Conversion drops after multiple contacts** — avoid campaign fatigue.
- 👔 Certain job roles consistently convert better — personalize messaging.
""")
