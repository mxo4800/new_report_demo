from io import StringIO
import streamlit as st
import pandas as pd
from ai import run_grammar_chain, run_rewrite_chain

# Sidebar
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    # Read the uploaded CSV file
    df = pd.read_csv(uploaded_file)

    # Display the data
    st.write("Original Data:")
    st.write(df)

    client_name = st.text_input("Client Name:", "Tullamore Dew")
    industry_type = st.text_input("Industry Type:", "irish whiskey")
    format = st.text_input("Format:", "YouTube")

    # Data manipulations

    col_to_pivot = st.multiselect("Select a column to pivot:", df.columns)
    pivot_values = st.multiselect("Select a column to aggregate:", df.columns)
    calculate_ctr = st.checkbox("Calculate CTR?")
    calculate_vcr = st.checkbox("Calculate VCR?")

    if calculate_ctr:
        clicks = st.selectbox("Select a column for clicks:",
                              df.columns, key='clicks')
        impressions = st.selectbox(
            "Select a column for impressions:", df.columns, key='impressions')

    if calculate_vcr:
        views = st.selectbox("Select a column for views:",
                             df.columns, key='views')
        starts = st.selectbox(
            "Select a column for starts:", df.columns, key='starts')

    best_performing = {"CTR": {}, "VCR": {}}

    create_report = st.checkbox("Create report?")

    if create_report and col_to_pivot and pivot_values:
        for index, col in enumerate(col_to_pivot):
            pivot_table = df.pivot_table(
                index=col, values=pivot_values, aggfunc="sum").reset_index()

            # CTR Calculation
            if calculate_ctr and clicks and impressions:
                pivot_table["CTR"] = pivot_table[clicks] / \
                    pivot_table[impressions]

                # Sorting
                pivot_table_ctr = pivot_table.sort_values(
                    by="CTR", ascending=False).reset_index(drop=True)

                # add top performers by CTR greater than average
                ctr_average = pivot_table[clicks].mean(
                ) / pivot_table[impressions].mean()
                pivot_table_ctr = pivot_table_ctr[pivot_table_ctr["CTR"]
                                                  > ctr_average]

                # Storing top performers in the new format
                for col_value in pivot_table_ctr[col]:
                    ctr_value = round(
                        pivot_table_ctr[pivot_table_ctr[col] == col_value]["CTR"].iloc[0] * 100, 2)
                    best_performing["CTR"].setdefault(
                        col, []).append((col_value, f"{ctr_value}%"))

            # VCR Calculation
            if calculate_vcr and views and starts:
                pivot_table["VCR"] = pivot_table[views] / \
                    pivot_table[starts]

                pivot_table_vcr = pivot_table.sort_values(
                    by="VCR", ascending=False).reset_index(drop=True)

                # add top performers by VCR greater than average
                vcr_average = pivot_table[views].mean(
                ) / pivot_table[starts].mean()
                pivot_table_vcr = pivot_table_vcr[pivot_table_vcr["VCR"]
                                                  > vcr_average]

                # Storing top performers in the new format
                for col_value in pivot_table_vcr[col]:
                    vcr_value = round(
                        pivot_table_vcr[pivot_table_vcr[col] == col_value]["VCR"].iloc[0] * 100, 2)
                    best_performing["VCR"].setdefault(
                        col, []).append((col_value, f"{vcr_value}%"))

                # Flattening the dictionary
        rows = []
        for kpi, variables in best_performing.items():
            for variable, values in variables.items():
                for value in values:
                    description, kpi_value = value
                    rows.append([kpi, variable, description, kpi_value])

        # Creating the DataFrame
        df = pd.DataFrame(
            rows, columns=["KPI", "Variable", "Description", "KPI_Value"])

        remove_rows = st.checkbox("Remove rows?")
        if remove_rows:
            rows_to_remove = st.multiselect(
                "Select rows to remove:", df["Description"].unique())
            df = df[~df["Description"].isin(rows_to_remove)]

        st.write("Best performing:")
        st.write(df)

        ai_report = st.checkbox("Create AI report?")

        best_vals = []

        # Convert DataFrame to the nested dictionary
        nested_dict = {kpi: df[df['KPI'] == kpi].groupby('Variable').apply(
            lambda x: x[['Description', 'KPI_Value']].values.tolist()
        ).to_dict() for kpi in df['KPI'].unique()}

        if ai_report:

            if calculate_ctr:

                kpi = "CTR"

                for col in nested_dict["CTR"].keys():

                    for idx, value in enumerate(nested_dict["CTR"][col]):

                        if idx == 0:

                            truth = f"The best value in the {col} column is {value[0]} with a {kpi} of {value[1]}."
                        else:
                            truth = f"{truth} The next best value in the {col} column is {value[0]} with a {kpi} of {value[1]}."

                        best_vals.append(truth)

            if calculate_vcr:

                kpi = "VCR"

                for col in nested_dict["VCR"].keys():

                    for idx, value in enumerate(nested_dict["VCR"][col]):

                        if idx == 0:

                            truth = f"The best value in the {col} column is {value[0]} with a {kpi} of {value[1]}."
                        else:
                            truth = f"{truth} The next best value in the {col} column is {value[0]} with a {kpi} of {value[1]}."

                        best_vals.append(truth)

            report = " ".join(best_vals)

            def run_report():
                # Call the long-running function with a spinner

                new_report = run_grammar_chain(
                    report, client_name, industry_type, format=format)
                return new_report

            with st.spinner(text='In progress...'):
                new_report = run_report()

            # Display the result
            st.write("A.I Report:")
            st.write(new_report)

        @st.cache_data
        def convert_df(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv().encode('utf-8')

        csv = convert_df(df)

        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='large_df.csv',
            mime='text/csv',
        )
        # save dataframe report to csv and let user download

    # Add saving functionality if needed
    # ...
