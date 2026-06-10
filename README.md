# 🏆 Nobel Laureates Dashboard

An interactive Streamlit dashboard for exploring Nobel Prize data from 1901 to the present. Built with Plotly for interactive charts and Matplotlib/Seaborn for advanced statistical visualizations.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

The dashboard is organized into five tabs:

| Tab | Description |
|---|---|
| 📈 **Overview** | Key metrics and prize trends over time |
| 🌍 **Geography** | Global distribution of laureates by country |
| 👤 **Demographics** | Gender, age, and laureate-type breakdowns |
| 🧪 **Advanced** | Six in-depth analyses: prizes by category & gender, winners by category, top countries, Peace Prize individuals vs. organizations, age analysis by category, and global distribution |
| 🔎 **Raw Data** | Searchable, filterable data table with CSV export |

**Sidebar filters** apply across all tabs:
- 📅 Year range slider
- 🎯 Prize category
- 👤 Laureate type (individual / organization)
- ⚧ Gender
- 🌍 Top N countries

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/nobel-laureates-dashboard.git
cd nobel-laureates-dashboard
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add the dataset

Place the Nobel Prize dataset next to the script. The app automatically detects any of the following filenames:

```
SDnobel.csv
SDnobel.xls
SDnobel.xlsx
```

If no file is found, you can upload one directly through the sidebar when the app is running.

### 4. Run the app

```bash
streamlit run Merged_Dashboard_3.py
```

The dashboard will open in your browser at `http://localhost:8501`.

## 📂 Project Structure

```
.
├── Merged_Dashboard_3.py   # Main Streamlit application
├── SDnobel.csv             # Nobel Prize dataset (not included)
├── requirements.txt        # Python dependencies
└── README.md
```

## 📊 Dataset

The app expects a Nobel laureates dataset with columns such as `year`, `category`, `full_name`, `laureate_type`, `sex`, `birth_country`, `age` (or `age_at_award`), and `motivation`. Column names are normalized automatically (case-insensitive, whitespace-trimmed).

A suitable dataset is the public [Nobel Prize dataset on Kaggle](https://www.kaggle.com/datasets/nobelfoundation/nobel-laureates).

## 🛠️ Built With

- [Streamlit](https://streamlit.io/) — web app framework
- [Plotly](https://plotly.com/python/) — interactive charts
- [Matplotlib](https://matplotlib.org/) & [Seaborn](https://seaborn.pydata.org/) — statistical visualizations
- [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/) — data processing

## 📄 License

This project is licensed under the MIT License — see the `LICENSE` file for details.
