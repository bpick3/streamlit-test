import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("Personal Federal Market Overview")

df = st.file_uploader("Upload your ad hoc report", type=["xlsx"])


if df:
    # read xlsx
    df = pd.read_excel(df)
    # st.write(df)
    
    col_set = st.columns(2)
    
    with col_set[0]:
        set_aside_options = df['Type of Set Aside Code'].unique()

        set_aside_option = st.selectbox(
            "Select set aside",
            set_aside_options,
            index=None,
            placeholder="Select a set aside",
        )

    with col_set[1]:
        location_options = df['Principal Place of Performance State Code'].unique()

        location_option = st.multiselect(
            "Select location(s)",
            location_options,
            placeholder="Select a location",
        )

    tab1, tab2, tab3 = st.tabs(["Buyers", "Competition (Coming Soon)", "Teaming (Coming Soon)"])

    with tab1:
        if set_aside_option is None and not location_option:
            # base case - no set aside and no location
            st.write("Showing top results across the US")
            grouped_df = df
            
        elif set_aside_option is not None and not location_option:
            # set aside and no location
            st.write("Showing top results for: ", set_aside_option)
            grouped_df = df[(df['Type of Set Aside Code'] == set_aside_option)]
        elif set_aside_option is not None and location_option:
            # set aside and location
            st.write("Showing top results for all set asides")
            grouped_df = df[(df['Type of Set Aside Code'] == set_aside_option) & (df['Principal Place of Performance State Code'].isin(location_option))]
        elif set_aside_option is None and location_option:
            # location and no set aside
            st.write("Showing top results for all departments")
            grouped_df = df[(df['Principal Place of Performance State Code'].isin(location_option))]
            
        
        depts_df = grouped_df.groupby('Contracting Department Name')['Dollars Obligated'].sum().reset_index()

        columns = st.columns(2)

        with columns[0]:
            # Get the top 10 contracting departments by dollars obligated
            top_depts = depts_df.nlargest(10, 'Dollars Obligated')
            st.write(top_depts, index=False)

        with columns[1]:
            st.bar_chart(top_depts, x='Contracting Department Name', y='Dollars Obligated')

        # filter with department name

        dept_option = st.selectbox(
            "Select a department",
            top_depts,
            index=None,
            placeholder="Select a department",
        )

        if dept_option is not None:
            agency_dept_df = grouped_df[grouped_df['Contracting Department Name'] == dept_option].groupby('Contracting Agency Name').agg({
                'Dollars Obligated': 'sum',
                'PIID': 'nunique'  # Count unique PIIDs
            }).rename(columns={'PIID': 'Awards'}).reset_index()
            top_agency_dept_df = agency_dept_df.nlargest(10, 'Dollars Obligated')
            st.write(top_agency_dept_df, index=False)

            agency_option = st.selectbox(
                "Select agency in " + dept_option,
                top_agency_dept_df,
                index=None,
                placeholder="Select an agency",
            )

            columns = st.columns(2)
            with columns[0]:
                if agency_option is not None:
                    agency_df = grouped_df[grouped_df['Contracting Agency Name'] == agency_option].groupby('Approved By').agg({
                        'Dollars Obligated': 'sum',
                        'PIID': 'nunique'  # Count unique PIIDs
                    }).rename(columns={'PIID': 'Awards'}).reset_index()
                else:
                    agency_df = grouped_df.groupby('Approved By').agg({
                        'Dollars Obligated': 'sum',
                        'PIID': 'nunique'  # Count unique PIIDs
                    }).rename(columns={'PIID': 'Awards'}).reset_index()
                    
                top_buyer_df = agency_df.nlargest(100, 'Dollars Obligated').reset_index(drop=True)
                st.write(top_buyer_df, index=False)

            with columns[1]:
                st.write("*Note*: here are the email addresses or beginnings of emails for the buyers in the selected office who are buying the most of what you sell.")
        

    with tab2:
        st.write("Coming Soon")



    with tab3:
        st.write("Coming Soon")
