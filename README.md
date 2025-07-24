#  Credit Approval System

A Django-based Credit Approval System that allows customer registration, eligibility checking, and loan creation using REST APIs. Developed using Test-Driven Development (TDD) and Dockerized for easy deployment.
---

##  Features

- Register new customers
- Check loan eligibility
- Create and manage loans
- View loans by customer or loan ID
- Test-Driven Development (TDD) implementation
- Docker + PostgreSQL setup
- API tested via Postman and Unit Tests

---

##  Technologies Used

-Backend: Django, Django REST Framework

-Database: PostgreSQL

-DevOps: Docker, Docker Compose

-Testing: Postman, Python unit tests

---


## 📦 Installation & Setup

###  Clone the Repository

```bash
git clone https://github.com/DiyaGopal/credit_approval.git
cd credit_approval
```

### Run with Docker

```bash
docker-compose up --build
```
It will set up the PostgreSQL database, run migrations, and start the Django server on: 
```
http://localhost:8000/
```
---

## API Usage

### Use Postman to interact with the APIs. Example endpoints:
### 1. Register Customer
```
POST /register
```
```bash
{
  "first_name": "Diya",
  "last_name": "Gopal",
  "age": 25,
  "monthly_salary": 100000,
  "phone_number": "9876543210"
}
```

### 2. Check Eligibility
```
POST /check-eligibility
```
```bash
{
  "customer_id": 1,
  "loan_amount": 50000,
  "interest_rate": 10,
  "tenure": 12
}
```

### 3. Create Loan
```
POST /create-loan
```
```bash
{
  "customer_id": 1,
  "loan_amount": 50000,
  "interest_rate": 10,
  "tenure": 12
}
```

### 4. View Loan by ID
```
GET /view-loan/<loan_id>
```

### 5. View Loans by Customer
```
GET /view-loans/<customer_id>
```
---

## Running Tests (TDD)

### Run all unit tests:
```bash
docker-compose exec web python manage.py test core
```
### All key functionalities are covered in
```
core/tests.py
```

---

## Author
### DIYA GOPAL



