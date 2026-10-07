from app.database import SessionLocal
from app.models import Customer

def query_customers(status:str=None):
    db=SessionLocal()

    try:
        query = db.query(Customer)

        if status:
            query = query.filter(Customer.status == status)

        customers = query.all()

        result=[]

        for customer in customers:
            result.append({
                "id":customer.id,
                "name":customer.name,
                "company":customer.company,
                "status":customer.status,
                "phone":customer.phone
            })

        return result

    finally:
        db.close()

