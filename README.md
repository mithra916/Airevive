# AIREVIVE
Airevive  monitors factory emissions in real time, tracking gases like CO₂, NO₂, and SO₂ with precise timestamps. It analyzes the data to identify pollution level breaches and assess severity. Alerts are generated instantly for quick response. The system helps industries and authorities maintain compliance and protect the environment. 

# Overview
The Real-Time Pollution Monitoring Dashboard is a Streamlit-based web application that allows users to visualize, analyze, and monitor air quality data from different stations.
It processes pollution data including CO₂, NO₂, SO₂ levels, calculates severity scores, and displays insights in an interactive dashboard.

It is ideal for environmental analysis, data visualization, and real-time pollution reporting.

# Problem Statement
Air pollution poses serious health risks and environmental challenges.
However, raw pollution data is often hard to interpret for decision-makers and the public.

We need a simple, visual, and interactive way to:

Monitor pollution levels in different areas

Identify dangerous spikes in harmful gases

Take timely action based on severity

# Proposed Solution
 Collects and processes station-wise pollution data
 Classifies readings into severity categories
 Provides interactive visualizations for analysis
 Highlights critical locations for immediate attention

 # Key Features
 Interactive Data Table — View pollution data with severity levels

 Visual Charts — CO₂, NO₂, SO₂ trends over time

 Severity Analysis — Color-coded severity status

 Timestamped Readings — Track pollution in real-time

 Export Support — Download analyzed reports for offline use

# Tech Stack

Technology	Purpose
Python 3.x	Core programming language
Streamlit	Web UI for interactive dashboards
Pandas	Data processing & analysis
Matplotlib / Plotly	Data visualization
CSV Dataset	Pollution data storage
Vercel / Localhost	Hosting environment

## How It Works (Simple Explanation)
### Data Input

The system reads pollution data from a CSV file (with details like station name, CO₂, NO₂, SO₂, time, and severity).

This can be real-time sensor data or dummy test data for simulation.

### Processing

The app uses Pandas to load and process the data.

Pollution levels are compared against pre-defined thresholds to determine Severity (Low, Medium, High).

### Visualization

Displays the pollution data in an interactive table.

Generates charts & graphs to show pollutant trends over time.

### Alerts & Insights

Automatically flags high-severity readings.

Helps understand which areas and times have the worst pollution.

### User Interaction

You can upload your own CSV to test.

View results instantly on a clean web dashboard built with Streamlit.

# Future Enhancements
🔹 Real-time IoT sensor integration

🔹 Map-based pollution heatmaps

🔹 Machine learning prediction for pollution trends

🔹 Mobile-friendly responsive UI

