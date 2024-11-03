import pandas as pd
import streamlit as st
from datetime import datetime
import pymysql
import matplotlib.pyplot as plt

# Database connection setup
def connection():
    return pymysql.connect(
        charset="utf8mb4",
        connect_timeout=10,
        cursorclass=pymysql.cursors.DictCursor,
        db="defaultdb",
        host="mysql-2d683784-arcane-2024.h.aivencloud.com",
        password="AVNS_Gxjzg5ruqCMrTvIAi5z",
        read_timeout=10,
        port=28309,
        user="avnadmin",
        write_timeout=10,
    )

# Function to create tables if they don't exist
def create_tables():
    conn = connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Machines (
                    machine_id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(255) NOT NULL,
                    type VARCHAR(255) NOT NULL
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Energy_Usage (
                    usage_id INT PRIMARY KEY AUTO_INCREMENT,
                    machine_id INT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    energy_usage FLOAT NOT NULL,
                    production_status BOOLEAN NOT NULL,
                    FOREIGN KEY (machine_id) REFERENCES Machines(machine_id)
                );
            """)
        conn.commit()
    except Exception as e:
        st.error(f"An error occurred while creating tables: {e}")
    finally:
        conn.close()

# Function to add a new machine
def add_machine(name, machine_type):
    conn = connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO Machines (name, type) VALUES (%s, %s)", (name, machine_type))
            conn.commit()
            st.success("Machine added successfully.")
    except Exception as e:
        st.error(f"An error occurred while adding the machine: {e}")
    finally:
        conn.close()

# Function to delete a machine
def delete_machine(machid):
    conn = connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Machines WHERE machine_id = %s", (machid,))
            conn.commit()
            st.success("Machine deleted successfully.")
    except Exception as e:
        st.error(f"An error occurred while deleting the machine: {e}")
    finally:
        conn.close()

# Function to add energy usage
def add_energy_usage(machid, usage, production_status):
    conn = connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Energy_Usage (machine_id, timestamp, energy_usage, production_status) VALUES (%s, %s, %s, %s)",
                (machid, datetime.now(), usage, production_status)
            )
            conn.commit()
            st.success("Energy usage added successfully.")
    except Exception as e:
        st.error(f"An error occurred while adding energy usage: {e}")
    finally:
        conn.close()

# Function to delete energy usage entry
def delete_energy_usage(usageid):
    conn = connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Energy_Usage WHERE usage_id = %s", (usageid,))
            conn.commit()
            st.success("Energy usage deleted successfully.")
    except Exception as e:
        st.error(f"An error occurred while deleting energy usage: {e}")
    finally:
        conn.close()

# Function to get analysis data
def get_analysis_data():
    query = '''
    SELECT 
        m.name, 
        AVG(eu.energy_usage) AS avg_usage, 
        MAX(eu.energy_usage) AS peak_usage, 
        MIN(eu.energy_usage) AS lowest_usage 
    FROM 
        Energy_Usage eu 
    JOIN 
        Machines m ON eu.machine_id = m.machine_id 
    GROUP BY 
        m.machine_id, m.name
    '''
    conn = connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            analysis_data = cursor.fetchall()
            return pd.DataFrame(analysis_data)
    except Exception as e:
        st.error(f"An error occurred while fetching analysis data: {e}")
    finally:
        conn.close()

# Streamlit UI
st.title("Machine and Energy Usage Management")

# Create tables if they don't exist
create_tables()

# Tabs for each section
tab1, tab2, tab3 = st.tabs(["Machine Details", "Energy Usage", "Energy Analysis"])

# Machine Details Tab
with tab1:
    st.header("Machine Details")
    
    # Add Machine
    st.subheader("Add a New Machine")
    name = st.text_input("Machine Name", key="add_machine_name")
    machine_type = st.text_input("Machine Type", key="add_machine_type")
    if st.button("Add Machine"):
        add_machine(name, machine_type)

    # Delete Machine
    st.subheader("Delete Machine")
    delete_id = st.number_input("Machine ID to Delete", min_value=1, step=1, key="delete_machine_id")
    if st.button("Delete Machine"):
        delete_machine(delete_id)

# Energy Usage Tab
with tab2:
    st.header("Energy Usage")

    # Add Energy Usage
    st.subheader("Add Energy Usage Entry")
    usageid = st.number_input("Usage ID", min_value=1, step=1, key="add_usage_id")
    machid = st.number_input("Machine ID", min_value=1, step=1, key="add_energy_machine_id")
    usage = st.number_input("Energy Used (kWh)", min_value=0, key="add_energy_usage")
    production_status = st.selectbox("Running Status", ["T", "F"], key="add_energy_status") == "T"
    if st.button("Add Energy Usage"):
        add_energy_usage(machid, usage, production_status)

    # Delete Energy Usage
    st.subheader("Delete Energy Usage Entry")
    delete_usage_id = st.number_input("Usage ID to Delete", min_value=1, step=1, key="delete_usage_id")
    if st.button("Delete Energy Usage"):
        delete_energy_usage(delete_usage_id)

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