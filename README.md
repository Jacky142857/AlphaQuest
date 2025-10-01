# AlphaQuest

AlphaQuest is a comprehensive alpha factor research and backtesting platform that enables quantitative researchers to develop, test, and analyze trading strategies using mathematical operators and market data.

## 🚀 Live Demo

**Try AlphaQuest now:** [https://alpha-quest.vercel.app/simulate](https://alpha-quest.vercel.app/simulate)

Since this is a free deployment, the backend server may take one to two minutes to start due to a cold start.
## Features

### 🧮 Mathematical Operators
- **Arithmetic**: Basic math operations (add, multiply, log, power, etc.)
- **Time Series**: Rolling calculations, differences, and temporal analysis
- **Grouping & Ranking**: Cross-sectional ranking, bucketing, and normalization
- **Logical & Comparison**: Boolean logic and conditional operations
- **Conditional Trading**: Advanced market condition-based strategies

### 📊 Data & Backtesting
- Pre-loaded Dow Jones 30 data
- Custom CSV data upload support
- Real-time alpha formula evaluation
- Performance metrics and visualization
- Risk management controls (truncation, delays, position limits)

### 🎯 Key Capabilities
- **Formula Editor**: Interactive alpha formula development with syntax highlighting
- **Learn Section**: Comprehensive documentation and examples for all operators
- **Portfolio Simulation**: Multi-stock backtesting with proper position sizing
- **User Management**: Save and manage custom alpha strategies
- **Dark/Light Theme**: Modern, responsive UI with theme switching

## Quick Start

### Local Development

#### Frontend (React)
```bash
cd frontend
npm install
npm start
```

#### Backend (Django)
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Deployment

### Live Deployment

AlphaQuest is currently deployed at: **[https://alpha-quest.vercel.app/simulate](https://alpha-quest.vercel.app/simulate)**

### Render Deployment

AlphaQuest is configured for easy deployment on Render with the included `render.yaml` configuration.

#### Backend Deployment
1. Connect your GitHub repository to Render
2. The backend will automatically deploy using:
   - **Build Command**: `cd backend && pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command**: `cd backend && gunicorn trading_signals.wsgi:application --bind 0.0.0.0:$PORT`

#### Frontend Deployment
1. The frontend will build and serve using:
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Start Command**: `cd frontend && npx serve -s build -l $PORT`

#### Environment Variables
Configure these environment variables in Render Dashboard:
- `DEBUG=False` (for production)
- `SECRET_KEY` (generate a secure secret key)
- `ALLOWED_HOSTS=.onrender.com`
- `CORS_ALLOWED_ORIGINS` (add your frontend URL)

## Example Alpha Formulas

### Basic Momentum
```
Rank(Returns(Close, 5))
```

### Mean Reversion with Volume Filter
```
if_else(Volume > ts_sum(Volume, 10)/10,
        Rank(-Returns(Close, 1)),
        0)
```

### Advanced Quantile Strategy
```
quantile(ts_av_diff(Close, 20),
         driver=gaussian,
         sigma=1.0)
```

### Multi-Condition Logic
```
and_op(gt_op(Volume, ts_mean(Volume, 20)),
       lt_op(Close, ts_mean(Close, 50)))
```

## Project Structure

```
alpha_quest/
├── frontend/          # React.js frontend application
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── contexts/      # React contexts
│   │   └── styles/        # CSS files
│   └── public/
├── backend/           # Python Flask backend
│   ├── services/          # Core business logic
│   ├── utils/             # Mathematical operators
│   ├── data/              # Market data files
│   └── app.py             # Flask application entry point
└── README.md
```

## Technology Stack

- **Frontend**: React.js, CSS3, Context API
- **Backend**: Python, Flask, pandas, NumPy
- **Database**: MongoDB (for user data)
- **Data**: CSV files, pandas DataFrames
- **Mathematical Libraries**: SciPy, NumPy

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is available for educational and research purposes.

---

**AlphaQuest** - Empowering quantitative research through intuitive alpha factor development.
