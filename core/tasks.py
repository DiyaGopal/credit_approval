from celery import shared_task
import pandas as pd
from .models import Customer, Loan
from datetime import datetime

@shared_task
def ingest_customer_data(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        Customer.objects.create(
            customer_id=row['customer_id'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            phone_number=row['phone_number'],
            monthly_salary=row['monthly_salary'],
            approved_limit=row['approved_limit'],
            current_debt=row['current_debt']
        )

@shared_task
def ingest_loan_data(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        Loan.objects.create(
            customer_id=row['customer_id'],
            loan_id=row['loan_id'],
            loan_amount=row['loan_amount'],
            tenure=row['tenure'],
            interest_rate=row['interest_rate'],
            monthly_installment=row['monthly_repayment (emi)'],
            emi_paid_on_time=row['EMIs paid on time'],
            start_date=pd.to_datetime(row['start date']),
            end_date=pd.to_datetime(row['end date'])
        )
