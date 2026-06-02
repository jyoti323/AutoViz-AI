# AutoViz AI Enterprise Hub

An enterprise-grade, multi-user analytics portal designed with **Streamlit**, **Pandas**, **Plotly**, and **Scikit-Learn**. This application enables users to manage data pipelines, execute dynamic visualizations in responsive grids, audit dataset quality, run machine learning models, and securely persist workspaces.

---

## 🔮 Enterprise Feature Suite

1. **🔒 Secure Profile & Role Management**:
   - Simulated JWT authentication backend linked to a local hashed JSON store (`users.json`).
   - Role-Based Access Controls (RBAC):
     - **Admin**: Full administrative permissions (data cleaning, file deletion, saving).
     - **Analyst**: Access dashboard visualizers and run ML models, but cannot purge files.
     - **Viewer**: Read-only access (dashboard visualization and ML tabs are disabled).
2. **⚖️ Dataset Comparison Engine**:
   - Parallel metrics grid highlighting discrepancies in row counts, percentage size differences, common columns, and trend alignment.
3. **🛠️ Advanced Cleaner & Stats**:
   - Live analytics logging (**Rows Removed**, **Nulls Imputed**, **Columns Converted**).
   - Conversions (Strings, Ints, Floats, Datetimes), duplicate drops, and Outlier Purges based on $1.5 \times IQR$ ranges.
4. **🎨 Visualizer Studio & Custom Dashboard Grid**:
   - Interactive layouts for Scatter, Line, Bar, Box, Histogram, Correlation Matrix, Bubble, Treemap, and Radar charts.
   - Dynamic Dashboard Builder Grid: Pin widgets to a grid layout with adjustable sizes (Full vs Half-Width).
   - Instant file exports (Interactive Plotly HTML, Excel Report Sheets, CSV exports).
5. **🧠 AI Analytics Desk**:
   - **Chat with Data**: Dynamic compiler that parses natural language math operations (e.g. *"average Sales"*, *"maximum Marks"*) to calculate figures and output corresponding chart distributions.
   - **Automated Summary**: Computes a 5-point report including anomalies, distributions, and best-fit chart cards.
6. **🔮 Predictive ML Sandbox**:
   - **Linear Regression**: Estimate numerical variables, plot regression trendlines, and return $R^2$ accuracy.
   - **Time-Series Forecasting**: Extrapolate trends over date/time steps.
   - **K-Means Clustering**: Group multi-dimensional numerical columns.

---

## 🚀 Setup & Execution

### Local Development
1. Clone the repository and navigate into it:
   ```bash
   cd "AutoViz AI"
   ```
2. Set up and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
4. Run the Streamlit server:
   ```bash
   streamlit run app.py
   ```

### 🐳 Containerization (Docker)
Build and run the application locally in an isolated container:
```bash
docker build -t autoviz-enterprise .
docker run -p 8501:8501 autoviz-enterprise
```

---

## 🌐 Production Readiness & Deployment

### 1. Database Connection (PostgreSQL)
To scale this application in production:
- Replace the local `users.json` with a PostgreSQL database.
- Use `SQLAlchemy` or `psycopg2` to manage tables (`users`, `saved_files`, `cleaner_logs`).
- Define database URI in a `.env` file:
  ```env
  DATABASE_URL=postgresql://user:password@host:port/database_name
  ```

### 2. Cloud Hosting Architecture
- **Frontend & Backend (Streamlit App)**: Deploy directly on **Render**, **Railway**, or **AWS ECS** by linking your GitHub repository.
- **File Storage**: Connect `storage/` uploads to an **AWS S3 Bucket** or **Google Cloud Storage** bucket using `boto3`.

### 3. CI/CD (GitHub Actions)
Deployments are automated on every commit using the following `.github/workflows/deploy.yml` structure:
```yaml
name: Deploy Pipeline

on:
  push:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run Code Linter
        run: |
          pip install flake8
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

  docker-deploy:
    needs: build-and-test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker Image
        run: |
          docker build -t autoviz-enterprise:latest .
```
