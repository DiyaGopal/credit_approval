from django.core.management.base import BaseCommand
import pandas as pd
from core.models import Customer, Loan
from datetime import datetime

class Command(BaseCommand):
    help = 'Import customer and loan data from Excel files'

    def handle(self, *args, **options):
        # Import customers
        customer_file = 'customer_data.xlsx'
        customer_df = pd.read_excel(customer_file)
        for _, row in customer_df.iterrows():
            Customer.objects.update_or_create(
                customer_id=row['Customer ID'],
                defaults={
                    'first_name': row['First Name'],
                    'last_name': row['Last Name'],
                    'age': row['Age'],
                    'phone_number': str(row['Phone Number']),
                    'monthly_salary': row['Monthly Salary'],
                    'approved_limit': row['Approved Limit']
                }
            )
        self.stdout.write(self.style.SUCCESS(f'Imported customers from {customer_file}'))

        # Import loans
        loan_file = 'loan_data.xlsx'
        loan_df = pd.read_excel(loan_file)
        for _, row in loan_df.iterrows():
            try:
                customer = Customer.objects.get(customer_id=row['Customer ID'])
            except Customer.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Customer ID {row['Customer ID']} not found. Skipping loan."))
                continue
            Loan.objects.update_or_create(
                loan_id=row['Loan ID'],
                defaults={
                    'customer': customer,
                    'loan_amount': row['Loan Amount'],
                    'tenure': row['Tenure'],
                    'interest_rate': row['Interest Rate'],
                    'monthly_payment': row['Monthly payment'],
                    'emis_paid_on_time': row['EMIs paid on Time'],
                    'date_of_approval': pd.to_datetime(row['Date of Approval']).date(),
                    'end_date': pd.to_datetime(row['End Date']).date(),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'Imported loans from {loan_file}'))
