import gradio as gr
import pandas as pd
import pymysql
from datetime import datetime

# Database connection setup
def create_connection():
    return pymysql.connect(
        host="mysql-2d683784-arcane-2024.h.aivencloud.com",
        user="avnadmin",
        password="AVNS_Gxjzg5ruqCMrTvIAi5z",
        database="defaultdb",
        port=28309,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

# Function to add a new machine
def add_machine(machid, name, machine_type):
    conn = create_connection()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO machines (machine_id, name, type) VALUES (%s, %s, %s)", (machid, name, machine_type))
        conn.commit()
    conn.close()
    return "Machine added successfully."

# Function to delete a machine
def delete_machine(machid):
    conn = create_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM machines WHERE machine_id = %s", (machid,))
        conn.commit()
    conn.close()
    return "Machine deleted successfully."

# Function to add energy usage
def add_energy_usage(usageid, machid, usage, production_status):
    timestamp = datetime.now()
    conn = create_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO energy_usage (usage_id, machine_id, timestamp, energy_usage, production_status) VALUES (%s, %s, %s, %s, %s)",
            (usageid, machid, timestamp, usage, production_status)
        )
        conn.commit()
    conn.close()
    return "Energy usage added successfully."

# Function to delete energy usage entry
def delete_energy_usage(usageid):
    conn = create_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM energy_usage WHERE usage_id = %s", (usageid,))
        conn.commit()
    conn.close()
    return "Energy usage deleted successfully."

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
    conn = create_connection()
    with conn.cursor() as cursor:
        cursor.execute(query)
        analysis_data = cursor.fetchall()
    conn.close()
    return pd.DataFrame(analysis_data).to_markdown()

# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("# Machine and Energy Usage Management")

    with gr.Tab("Machine Details"):
        gr.Markdown("### Add a New Machine")
        machid = gr.Number(label="Machine ID", precision=0)
        name = gr.Textbox(label="Machine Name")
        machine_type = gr.Textbox(label="Machine Type")
        add_machine_button = gr.Button("Add Machine")
        add_machine_output = gr.Textbox()

        add_machine_button.click(add_machine, inputs=[machid, name, machine_type], outputs=add_machine_output)

        gr.Markdown("### Delete a Machine")
        delete_machid = gr.Number(label="Machine ID to Delete", precision=0)
        delete_machine_button = gr.Button("Delete Machine")
        delete_machine_output = gr.Textbox()

        delete_machine_button.click(delete_machine, inputs=delete_machid, outputs=delete_machine_output)

    with gr.Tab("Energy Usage"):
        gr.Markdown("### Add Energy Usage Entry")
        usageid = gr.Number(label="Usage ID", precision=0)
        machine_id = gr.Number(label="Machine ID", precision=0)
        usage = gr.Number(label="Energy Used (kWh)", precision=2)
        production_status = gr.Checkbox(label="Running Status (Checked for True)")

        add_usage_button = gr.Button("Add Energy Usage")
        add_usage_output = gr.Textbox()

        add_usage_button.click(add_energy_usage, inputs=[usageid, machine_id, usage, production_status], outputs=add_usage_output)

        gr.Markdown("### Delete Energy Usage Entry")
        delete_usageid = gr.Number(label="Usage ID to Delete", precision=0)
        delete_usage_button = gr.Button("Delete Energy Usage")
        delete_usage_output = gr.Textbox()

        delete_usage_button.click(delete_energy_usage, inputs=delete_usageid, outputs=delete_usage_output)

    with gr.Tab("Energy Analysis"):
        gr.Markdown("### Energy Usage Analysis")
        analysis_button = gr.Button("Show Analysis")
        analysis_output = gr.Markdown()

        analysis_button.click(get_analysis_data, outputs=analysis_output)

demo.launch()
