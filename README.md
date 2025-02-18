# 2coins
## Django-Based Multi-User Money Tracking Application

2coins is a financial tracking application that helps users manage their income and expenses efficiently. 
It supports multiple currencies and provides insightful visualizations through a variety of charts.

## Features
- Multi-User Support – Track personal or shared finances with separate accounts  
- Multi-Currency Support – Manage transactions in different currencies with automatic conversions  
- Categorized Transactions – Organize expenses and income into categories for better insights  
- Transfers Between Accounts – Move funds between accounts while keeping records up to date  
- Interactive Charts & Visualizations – Gain insights into your financial habits with dynamic reports
- Optional OAuth Authentication – Users can log in with OAuth-based authentication for enhanced security

## Screenshots
| Page | Screenshot |
|:----:|:----------:|
| Dashboard | ![Dashboard page](https://github.com/user-attachments/assets/8ff86da1-e0dc-41cd-9a2d-1e19ece28b60) |
| Transactions | ![Transactions page](https://github.com/user-attachments/assets/b9b4b86e-3575-4e27-b105-67972a3de53b) |
| Categories | ![Categories page](https://github.com/user-attachments/assets/ecd11f33-b440-47f9-a6ef-7f58b298a825) |
| Accounts | ![Accounts page](https://github.com/user-attachments/assets/c874f953-f5a8-45c8-9163-b22029870294) |

## Getting Started

1. Clone the repository:
```sh
git clone git@github.com:oleh-papka/2coins.git
cd 2coins
```

2. Setup a virtual environment:
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```sh
cd two_coins
pip install -r requirements.txt
```

4. Create and run migrations:
```sh
python manage.py makemigrations
python manage.py migrate
```

5. Load currencies data:
```sh
python manage.py loaddata currencies.json
```

6. Set your `.env` file by using [`.env.example`](./.env.example)

7. Start the development server: 
```sh
python manage.py runserver
```

8. Access the app at: [`http://127.0.0.1:8000/`](http://127.0.0.1:8000/)

9. Optionally you can set up it with docker-compose (by default it will use PostgreSQL db with Docker setup)
```sh
docker compose up 
```

## Tech Stack
**Backend:** Django, Django REST Framework  
**Frontend:** HTML, CSS, JavaScript, Bootstrap  
**Database:** PostgreSQL / SQLite  
**Deployment:** Docker (optional)  

