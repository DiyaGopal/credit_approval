from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer
from datetime import date

#EMI calculation
def calculate_emi(principal, rate, tenure):
    monthly_rate = rate / (12 * 100)
    emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure) / (((1 + monthly_rate) ** tenure) - 1)
    return round(emi, 2)

#Loan eligibility logic
def check_loan_eligibility_logic(customer, loan_amount, interest_rate, tenure):
    loans = Loan.objects.filter(customer=customer)
    current_year = date.today().year

    past_loans_paid = sum([1 for loan in loans if loan.emi_paid_on_time >= loan.tenure])
    num_loans = loans.count()
    loans_this_year = sum([1 for loan in loans if loan.start_date.year == current_year])
    total_loan_volume = sum([loan.loan_amount for loan in loans])

    #Credit score calculation
    credit_score = min(100, (
        past_loans_paid * 10 +
        max(0, 30 - num_loans * 2) +
        loans_this_year * 5 +
        min(30, total_loan_volume / 100000)
    ))

    approval = False
    corrected_rate = interest_rate
    message = ""

    #Approval logic
    if credit_score > 50:
        approval = True
    elif 50 >= credit_score > 30 and interest_rate >= 12:
        approval = True
    elif 30 >= credit_score > 10 and interest_rate >= 16:
        approval = True
    elif credit_score <= 10:
        message = "Credit score too low"

    if credit_score <= 10:
        corrected_rate = 16
    elif 10 < credit_score <= 30:
        corrected_rate = max(16, interest_rate)
    elif 30 < credit_score <= 50:
        corrected_rate = max(12, interest_rate)

    monthly_installment = calculate_emi(loan_amount, corrected_rate, tenure)

    
    if (monthly_installment + customer.current_debt) > 0.5 * customer.monthly_salary:
        approval = False
        message = "EMI exceeds 50% of salary"

    return {
        "approval": approval,
        "corrected_interest_rate": corrected_rate,
        "monthly_installment": monthly_installment,
        "message": message
    }

#Registering Customer
@api_view(['POST'])
def register_customer(request):
    data = request.data
    try:
        monthly_income = int(data['monthly_salary'])
        approved_limit = round(36 * monthly_income / 100000) * 100000
        customer = Customer.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            age=data['age'],
            monthly_salary=monthly_income,
            approved_limit=approved_limit,
            phone_number=data['phone_number'],
        )
        serializer = CustomerSerializer(customer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def check_eligibility(request):
    data = request.data
    try:
        customer = Customer.objects.get(customer_id=data['customer_id'])
        loan_amount = float(data['loan_amount'])
        interest_rate = float(data['interest_rate'])
        tenure = int(data['tenure'])

        eligibility_data = check_loan_eligibility_logic(customer, loan_amount, interest_rate, tenure)

        response = {
            "customer_id": customer.customer_id,
            "approval": eligibility_data["approval"],
            "interest_rate": interest_rate,
            "corrected_interest_rate": eligibility_data["corrected_interest_rate"],
            "tenure": tenure,
            "monthly_installment": eligibility_data["monthly_installment"],
            "message": eligibility_data["message"]
        }
        return Response(response, status=status.HTTP_200_OK)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#Loan Creation
@api_view(['POST'])
def create_loan(request):
    data = request.data
    customer_id = data.get("customer_id")
    try:
        customer = Customer.objects.get(customer_id=customer_id)
        loan_amount = float(data.get("loan_amount"))
        interest_rate = float(data.get("interest_rate"))
        tenure = int(data.get("tenure"))

        eligibility_data = check_loan_eligibility_logic(customer, loan_amount, interest_rate, tenure)

        if not eligibility_data["approval"]:
            return Response({
                "loan_id": None,
                "customer_id": customer_id,
                "loan_approved": False,
                "message": eligibility_data.get("message", "Loan not approved"),
                "monthly_installment": eligibility_data["monthly_installment"]
            }, status=status.HTTP_200_OK)

        loan = Loan.objects.create(
            customer=customer,
            loan_amount=loan_amount,
            interest_rate=eligibility_data["corrected_interest_rate"],
            tenure=tenure,
            monthly_installment=eligibility_data["monthly_installment"],
            emi_paid_on_time=0,
            start_date=date.today(),
            end_date=date.today().replace(year=date.today().year + int(tenure / 12))
        )
        customer.current_debt += eligibility_data["monthly_installment"]
        customer.save()

        return Response({
            "loan_id": loan.loan_id,
            "customer_id": customer_id,
            "loan_approved": True,
            "message": "Loan approved successfully",
            "monthly_installment": loan.monthly_installment
        })

    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#Viewing Loan by ID
@api_view(['GET'])
def view_loan(request, loan_id):
    try:
        loan = Loan.objects.get(loan_id=loan_id)
        customer = loan.customer
        return Response({
            "loan_id": loan.loan_id,
            "customer": {
                "customer_id": customer.customer_id,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "phone_number": customer.phone_number,
                "age": customer.age
            },
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_installment,
            "tenure": loan.tenure
        })
    except Loan.DoesNotExist:
        return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)

#Viewing Loan by Customer ID
@api_view(['GET'])
def view_loans_by_customer(request, customer_id):
    try:
        loans = Loan.objects.filter(customer__customer_id=customer_id)
        result = []
        for loan in loans:
            repayments_left = loan.tenure - loan.emi_paid_on_time
            result.append({
                "loan_id": loan.loan_id,
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_installment,
                "repayments_left": repayments_left
            })
        return Response(result)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
