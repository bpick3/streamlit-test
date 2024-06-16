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

    tab1, tab2 = st.tabs(["Buyers", "Competition"])

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
            st.write("*Top Agencies*")
            agency_dept_df = grouped_df[grouped_df['Contracting Department Name'] == dept_option].groupby('Contracting Agency Name').agg({
                'Dollars Obligated': 'sum',
                'PIID': 'nunique',   # Count unique PIIDs
                'Number of Offers Received': 'mean'
            }).rename(columns={'PIID': 'Awards', 'Number of Offers Received': 'Average Offers'}).reset_index()

            agency_dept_df['Average Offers'] = agency_dept_df['Average Offers'].round(0)
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
                st.write("*Top Offices*")
                if agency_option is not None:
                    office_df = grouped_df[grouped_df['Contracting Agency Name'] == agency_option].groupby(['Contracting Office Name']).agg({
                        'Dollars Obligated': 'sum',
                        'PIID': 'nunique'  # Count unique PIIDs
                    }).rename(columns={'PIID': 'Awards'}).reset_index()
                else:
                    office_df = grouped_df.groupby(['Contracting Office Name']).agg({
                        'Dollars Obligated': 'sum',
                        'PIID': 'nunique'  # Count unique PIIDs
                    }).rename(columns={'PIID': 'Awards'}).reset_index()
                    
                top_office_df = office_df.nlargest(100, 'Dollars Obligated').reset_index(drop=True)
                st.write(top_office_df, index=False)

            with columns[1]:
                
                # select office
                office_option = st.selectbox(
                    "Select office in " + agency_option,
                    top_office_df,
                    index=None,
                    placeholder="Select an office",
                )
                
                if office_option is not None:
                    st.write("*Buyers across office*")
                    office_df = grouped_df[grouped_df['Contracting Office Name'] == office_option].groupby(['Approved By']).agg({
                        'Dollars Obligated': 'sum',
                        'PIID': 'nunique'  # Count unique PIIDs
                    }).rename(columns={'PIID': 'Awards'}).reset_index()
                else: 
                    st.write("*Buyers across agency*")
                    office_df = grouped_df[grouped_df['Contracting Agency Name'] == agency_option].groupby(['Approved By']).agg({
                        'Dollars Obligated': 'sum',
                        'PIID': 'nunique'  # Count unique PIIDs
                    }).rename(columns={'PIID': 'Awards', 'Contracting Office Name': 'Office'}).reset_index()

                top_buyer_df = office_df.nlargest(100, 'Dollars Obligated').reset_index(drop=True)
                st.write(top_buyer_df, index=False)

    with tab2:
        st.write("Coming Soon")
