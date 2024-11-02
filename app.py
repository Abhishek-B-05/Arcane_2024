import mysql.connector
import pandas as pd
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt

# Database connection setup
def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="abhi2005",
        database="stats"
    )

# Function to add a new machine
def add_machine(machid, name, machine_type):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO machines (machine_id, name, type) VALUES (%s, %s, %s)", (machid, name, machine_type))
    connection.commit()
    cursor.close()
    connection.close()

# Function to delete a machine
def delete_machine(machid):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM machines WHERE machine_id = %s", (machid,))
    connection.commit()
    cursor.close()
    connection.close()

# Function to add energy usage
def add_energy_usage(usageid, machid, timestamp, usage, production_status):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO energy_usage (usage_id, machine_id, timestamp, energy_usage, production_status) VALUES (%s, %s, %s, %s, %s)",
        (usageid, machid, timestamp, usage, production_status)
    )
    connection.commit()
    cursor.close()
    connection.close()

# Function to delete energy usage entry
def delete_energy_usage(usageid):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM energy_usage WHERE usage_id = %s", (usageid,))
    connection.commit()
    cursor.close()
    connection.close()

# Function to calculate and display energy usage statistics
def get_analysis_data():
    query = '''
    SELECT 
        m.name, 
        AVG(eu.energy_usage) AS avg_usage, 
        MAX(eu.energy_usage) AS peak_usage, 
        MIN(eu.energy_usage) AS lowest_usage 
    FROM 
        energy_usage eu 
    JOIN 
        machines m ON eu.machine_id = m.machine_id 
    GROUP BY 
        m.machine_id, m.name
    '''
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query)
    analysis_data = cursor.fetchall()
    cursor.close()
    connection.close()
    return pd.DataFrame(analysis_data)

# Streamlit UI
st.title("Machine and Energy Usage Management")

# Tabs for each section
tab1, tab2, tab3 = st.tabs(["Machine Details", "Energy Usage", "Energy Analysis"])

# Machine Details Tab
with tab1:
    st.header("Machine Details")
    
    # Add Machine
    st.subheader("Add a New Machine")
    machid = st.number_input("Machine ID", min_value=1, step=1)
    name = st.text_input("Machine Name")
    machine_type = st.text_input("Machine Type")
    if st.button("Add Machine"):
        add_machine(machid, name, machine_type)
        st.success("Machine added successfully.")

    # Delete Machine
    st.subheader("Delete Machine")
    delete_id = st.number_input("Machine ID to Delete", min_value=1, step=1)
    if st.button("Delete Machine"):
        delete_machine(delete_id)
        st.success("Machine deleted successfully.")

# Energy Usage Tab
with tab2:
    st.header("Energy Usage")

    # Add Energy Usage
    st.subheader("Add Energy Usage Entry")
    usageid = st.number_input("Usage ID", min_value=1, step=1)
    machid = st.number_input("Machine ID", min_value=1, step=1)
    timestamp = datetime.now()
    usage = st.number_input("Energy Used (kWh)", min_value=0)
    production_status = st.selectbox("Running Status", ["T", "F"]) == "T"
    if st.button("Add Energy Usage"):
        add_energy_usage(usageid, machid, timestamp, usage, production_status)
        st.success("Energy usage added successfully.")

    # Delete Energy Usage
    st.subheader("Delete Energy Usage Entry")
    delete_usage_id = st.number_input("Usage ID to Delete", min_value=1, step=1)
    if st.button("Delete Energy Usage"):
        delete_energy_usage(delete_usage_id)
        st.success("Energy usage deleted successfully.")

# Energy Analysis Tab
with tab3:
    st.header("Energy Usage Analysis")
    
    # Calculate and display analysis
    if st.button("Show Analysis"):
        analysis_df = get_analysis_data()
        if not analysis_df.empty:
            st.write("### Energy Usage Analysis")
            st.write(analysis_df)
            
            # Plot
            fig, ax = plt.subplots()
            analysis_df.plot(kind="bar", x="name", y="avg_usage", ax=ax, legend=False)
            ax.set_title("Average Energy Usage per Machine")
            ax.set_xlabel("Machine Name")
            ax.set_ylabel("Average Energy Usage (kWh)")
            st.pyplot(fig)
        else:
            st.write("No data available for analysis.")
