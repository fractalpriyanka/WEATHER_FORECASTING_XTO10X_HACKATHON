# 🌦️ Weather Forecasting Model – Xto10X Hackathon

Welcome to our weather forecasting project built for the **Xto10X Hackathon**. This repository showcases a complete pipeline from data collection to a deployed machine learning model, a FastAPI backend, and a beautiful Next.js frontend.

---

## 🚀 Live Demo

- 🔗 Website: [weather-app.bhaweshagrawal.com.np](https://weather-app.bhaweshagrawal.com.np)
- 🌐 API Endpoint: `https://weather-app-tr3b.onrender.com/predict`
  - Example JSON request:
    ```json
    {
      "date": "2025-04-12"
    }
    ```

---

## 🧐 Tech Stack

- **Random Forest Regressor** (Scikit-learn)
- **FastAPI** (Python backend)
- **Next.js + Tailwind** (Frontend)
- **Vercel** (Frontend deployment)
- **Render** (Backend deployment)
- **GitHub Actions** (Model retraining automation)
- **Weather APIs**:
  - Historical: [Open-Meteo](https://open-meteo.com/)
  - Latest: [WeatherAPI](https://www.weatherapi.com/)

---

## 📂 Clone & Run Locally

```bash
git clone https://github.com/fractalpriyanka/WEATHER_FORECASTING_XTO10X_HACKATHON
cd WEATHER_FORECASTING_XTO10X_HACKATHON
```

---

## 🥪 1. Running the Random Forest Regressor Model Locally

1. Open the Jupyter Notebook `model_training.ipynb`.
2. Make sure you have the dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```
3. Make sure to initially download the historical dataset.
4. Run all cells to:
   - Load dataset
   - Preprocess
   - Train model
   - Predict

---

## 🔁 2. Data Pipeline

### ⏳ Historical Weather Data (Open-Meteo)

- Located in the script `backend/fetch_data.py`.
- Pulls data from [Open-Meteo](https://open-meteo.com/) API.

### ☄️ Latest Weather Data (WeatherAPI)

- Located in `backend/fetch_data.py`.
- Pulls recent updates using [WeatherAPI](https://www.weatherapi.com/).

---

## 🤖 3. GitHub Action: Dataset Update + Model Retrain

- We use GitHub Actions to automate:
  - Fetching new data.
  - Updating the dataset.
  - Retraining the model.
  - Committing the updated model (`model.pkl`) into the repository.

🛠️ GitHub Workflow File: `.github/workflows/daily_update.yml`

---

## 🖥️ 4. Running the FastAPI Backend Locally

### 📦 Setup

```bash
cd backend
pip install -r requirements.txt
```

### 🔐 Add Environment Variables

Create a `.env` file with your secret token:

```env
API_TOKEN=your_secret_token
```

You can generate a token manually or let the GitHub Action push the latest one and fetch it from the environment.

### ▶️ Run Server

```bash
uvicorn main:app --reload
```

### 🌐 Test the API

Visit: `http://localhost:8000/docs`

Or use:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_secret_token" \
  -d '{"date": "2025-04-12"}'
```

---

## 🌐 5. Running the Next.js Website Locally

### 🛠️ Setup

```bash
cd frontend
npm install
```

### 🥪 Start Development Server

```bash
npm run dev
```

Visit `http://localhost:3000` in your browser.

---

## 📦 Deployment Info

- **Frontend** is deployed via **Vercel** → [weather-app.bhaweshagrawal.com.np](https://weather-app.bhaweshagrawal.com.np)
- **Backend** is deployed via **Render** → `https://weather-app-tr3b.onrender.com/predict`

---

## 🧑‍💻 Contributors

- Bhawesh Agrawal
- Priyanka Kumari
- Meet Jani

---

## 📜 License

This project is licensed under the MIT License.

