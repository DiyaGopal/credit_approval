from rest_framework.test import APITestCase
from rest_framework import status

class CreditApprovalTests(APITestCase):

    def setUp(self):
        self.customer_data = {
    "first_name": "Diya",
    "last_name": "Gopal",
    "age": 25,
    "phone_number": "9876543210",
    "monthly_salary": 100000
}


    def test_register_customer(self):
        response = self.client.post("/register/", self.customer_data, format='json')
        print("Register Response:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("customer_id", response.data)

    def test_check_eligibility(self):
        reg = self.client.post("/register/", self.customer_data, format='json')
        cid = reg.data["customer_id"]

        data = {
            "customer_id": cid,
            "loan_amount": 50000,
            "interest_rate": 10.0,
            "tenure": 36
        }

        response = self.client.post("/check-eligibility/", data, format='json')
        print("Eligibility Response:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("approval", response.data)

    def test_create_loan(self):
        reg = self.client.post("/register/", self.customer_data, format='json')
        cid = reg.data["customer_id"]

        data = {
    "customer_id": cid,
    "loan_amount": 50000,
    "interest_rate": 16.0,
    "tenure": 36
}


        response = self.client.post("/create-loan/", data, format='json')
        print("Loan Create Response:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("loan_approved"))

    def test_view_loans_and_loan_by_id(self):
        reg = self.client.post("/register/", self.customer_data, format='json')
        cid = reg.data["customer_id"]

        data = {
            "customer_id": cid,
            "loan_amount": 50000,
            "interest_rate": 16.0,
            "tenure": 36
        }

        loan = self.client.post("/create-loan/", data, format='json')
        print("View Loan - Create Response:", loan.data)
        loan_id = loan.data["loan_id"]

        detail = self.client.get(f"/view-loan/{loan_id}/")
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["loan_id"], loan_id)

        all_loans = self.client.get(f"/view-loans/{cid}/")
        self.assertEqual(all_loans.status_code, status.HTTP_200_OK)
        self.assertTrue(len(all_loans.data) >= 1)
