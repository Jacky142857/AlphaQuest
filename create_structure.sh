#!/bin/bash

echo "🚀 Creating complete Trading Signals App directory structure..."

echo "📁 Creating backend directories..."
# Backend directory structure
mkdir -p backend/trading_signals
mkdir -p backend/api
mkdir -p backend/media

echo "📁 Creating frontend directories..."
# Frontend directory structure
mkdir -p frontend/src/components
mkdir -p frontend/public

echo "📄 Creating all backend files..."
# Backend files
touch backend/requirements.txt
touch backend/manage.py
touch backend/trading_signals/__init__.py
touch backend/trading_signals/settings.py
touch backend/trading_signals/urls.py
touch backend/trading_signals/wsgi.py
touch backend/trading_signals/asgi.py
touch backend/api/__init__.py
touch backend/api/apps.py
touch backend/api/admin.py
touch backend/api/models.py
touch backend/api/views.py
touch backend/api/urls.py
touch backend/api/tests.py

echo "📄 Creating all frontend files..."
# Frontend files
touch frontend/package.json
touch frontend/public/index.html
touch frontend/src/index.js
touch frontend/src/index.css
touch frontend/src/App.js
touch frontend/src/App.css
touch frontend/src/components/DataUpload.js
touch frontend/src/components/AlphaFormula.js
touch frontend/src/components/PnLChart.js

echo "✅ Complete directory and file structure created!"
echo ""
echo "📂 Project structure:"
echo "trading-signals-app/"
echo "├── backend/"
echo "│   ├── trading_signals/"
echo "│   │   ├── __init__.py"
echo "│   │   ├── settings.py"
echo "│   │   ├── urls.py"
echo "│   │   ├── wsgi.py"
echo "│   │   └── asgi.py"
echo "│   ├── api/"
echo "│   │   ├── __init__.py"
echo "│   │   ├── apps.py"
echo "│   │   ├── admin.py"
echo "│   │   ├── models.py"
echo "│   │   ├── views.py"
echo "│   │   ├── urls.py"
echo "│   │   └── tests.py"
echo "│   ├── manage.py"
echo "│   └── requirements.txt"
echo "└── frontend/"
echo "    ├── public/"
echo "    │   └── index.html"
echo "    ├── src/"
echo "    │   ├── components/"
echo "    │   │   ├── AlphaFormula.js"
echo "    │   │   ├── DataUpload.js"
echo "    │   │   └── PnLChart.js"
echo "    │   ├── App.js"
echo "    │   ├── App.css"
echo "    │   ├── index.js"
echo "    │   └── index.css"
echo "    └── package.json"
echo ""
echo "📝 Next steps:"
echo "1. Copy content from each artifact above into the corresponding file"
echo "2. cd backend && python -m venv venv && source venv/bin/activate"
echo "3. pip install -r requirements.txt"
echo "4. python manage.py migrate"
echo "5. cd ../frontend && npm install"
echo "6. Start both servers: backend (python manage.py runserver) & frontend (npm start)"
echo ""
echo "💡 Tip: Open your code editor in the trading-signals-app folder and copy-paste"
echo "   each artifact content into its corresponding file. The file names match"
echo "   the artifact titles exactly!"