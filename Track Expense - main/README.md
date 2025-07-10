# Track Expense
<img width="965" height="595" alt="Screenshot 2025-07-10 204142" src="https://github.com/user-attachments/assets/1bc5435b-e683-43a0-b6e9-f1127b53b5aa" />

<img width="975" height="578" alt="Screenshot 2025-07-10 204354" src="https://github.com/user-attachments/assets/d341276b-4d68-48eb-a2f4-e294fdaafc92" />
<img width="450" height="172" alt="Screenshot 2025-07-10 030416" src="https://github.com/user-attachments/assets/570b93b3-a86e-4ba3-b8aa-22fe21ff628d" />
<img width="973" height="593" alt="Screenshot 2025-07-10 204239" src="https://github.com/user-attachments/assets/fafa8b3e-6029-4809-98b7-4855af9ae886" />
<img width="424" height="261" alt="Screenshot 2025-07-10 002625" src="https://github.com/user-attachments/assets/56d7d25c-88c1-4832-9b7a-34cffa67fb56" />
<img width="968" height="575" alt="Screenshot 2025-07-10 204223" src="https://github.com/user-attachments/assets/cd87ba0a-f544-4093-83d5-090104289a09" />
<img width="958" height="618" alt="Screenshot 2025-07-10 204339" src="https://github.com/user-attachments/assets/15191baa-650a-4269-abbd-3333f445e416" />
<img width="973" height="604" alt="Screenshot 2025-07-10 204326" src="https://github.com/user-attachments/assets/9850e2a0-3c93-42a2-b8eb-26a815bc1f8f" />
<img width="975" height="561" alt="Screenshot 2025-07-10 204311" src="https://github.com/user-attachments/assets/3181379e-1251-4439-b7b1-a9270fbc599b" />
<img width="968" height="575" alt="Screenshot 2025-07-10 204223" src="https://github.com/user-attachments/assets/bdaea5b6-0d26-401e-872c-b4452b466dce" />
<img width="963" height="598" alt="Screenshot 2025-07-10 204252" src="https://github.com/user-attachments/assets/ade7ec21-3f4a-4824-ad9b-d98f225deb6d" />



![Dashboard Overview](./static/img/dashboard_overview.png)
![Dashboard Earnings Chart](./static/img/dashboard_earnings_chart.png)
![Earnings Overview and Revenue Sources](./static/img/earnings_revenue.png)
![Expense Summary](./static/img/expense_summary.png)
![Expenses List](./static/img/expenses_list.png)
![Income List](./static/img/income_list.png)
![Expense Forecast Table](./static/img/expense_forecast_table.png)
![Expense Forecast for Next 30 Days](./static/img/forecast_plot.png)
![Preferences Page](./static/img/preferences_page.png)
![User Profile Page](./static/img/user_profile.png)
![Goal List Page](./static/img/goal_list.png)

## Overview

Track Expense is a comprehensive personal expense tracker web application built using Django. It allows users to log their expenses, categorize them automatically using machine learning, and provides future expense predictions. Additionally, users can set financial goals and track their progress.

## Features

- **Expense Logging**: Log daily expenses with details such as date, description, amount, and category.

- **Automated Expense Categorization**: Uses a machine learning model to categorize expenses based on descriptions.

- **Future Expense Prediction**: Forecasts expenses for the next 30 days using ARIMA time series modeling.

- **Goal Management**: Set financial goals, add savings amounts, and receive congratulatory notifications upon achievement.

- **User Authentication**: Secure user registration, login, and profile management.

- **Expense Limits**: Set daily expense limits with email alerts when exceeded.

## Setup

To run this application locally, follow these steps:

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/yourusername/track-expense.git
   ```

2. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   - **Windows**:

     ```bash
     venv\Scripts\activate
     ```

   - **macOS and Linux**:

     ```bash
     source venv/bin/activate
     ```

4. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

6. Create a superuser account to access the admin panel:

   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:

   ```bash
   python manage.py runserver
   ```

8. Open your web browser and go to `http://localhost:8000` to access the application.

## Usage

1. Register a new account or log in using your credentials.

2. Log your expenses by clicking the "Add Expense" button and filling in the details.

3. View your expense history, categorized expenses, and future expense predictions on the dashboard.

4. Manage your financial goals by adding new goals and tracking your savings progress.

5. Access the admin panel at `http://localhost:8000/admin/` for administrative tasks.

## Contributing

If you'd like to contribute to this project, please follow these steps:

1. Fork the repository on GitHub.

2. Create a new branch for your feature or bug fix:

   ```bash
   git checkout -b feature-name
   ```

3. Make your changes and commit them:

   ```bash
   git commit -m "Add new feature"
   ```

4. Push your changes to your forked repository:

   ```bash
   git push origin feature-name
   ```

5. Create a pull request on the original repository to propose your changes.

## Acknowledgments

- Thanks to the Django community for creating such a powerful web framework.

- The automated expense categorization and prediction features are powered by machine learning models, which were trained using various open-source libraries and datasets.

Feel free to customize and enhance Track Expense according to your needs. Happy budgeting!

## Author

Hamza Abdul Karim
