from fastapi import FastAPI, Query, Response
from pydantic import BaseModel, Field
from typing import Optional
import math

app = FastAPI()

# -------------------------
# DATA
# -------------------------
cars = [
    {"id": 1, "name": "Hyundai Creta", "type": "SUV", "price_per_day": 2000, "is_available": True},
    {"id": 2, "name": "Maruti Swift", "type": "Hatchback", "price_per_day": 1200, "is_available": True},
    {"id": 3, "name": "Honda City", "type": "Sedan", "price_per_day": 1800, "is_available": True},
    {"id": 4, "name": "Toyota Fortuner", "type": "SUV", "price_per_day": 3500, "is_available": True},
    {"id": 5, "name": "Tata Nexon EV", "type": "EV", "price_per_day": 2200, "is_available": True},
    {"id": 6, "name": "BMW X5", "type": "Luxury", "price_per_day": 6000, "is_available": True}
]

rentals = []
rental_counter = 1

# -------------------------
# HELPERS
# -------------------------
def find_car(car_id):
    for car in cars:
        if car["id"] == car_id:
            return car
    return None

def calculate_cost(price, days, rental_type):
    total = price * days
    if rental_type == "with_driver":
        total += 500 * days
    return total

def filter_cars_logic(type=None, max_price=None, is_available=None):
    result = cars
    if type is not None:
        result = [c for c in result if c["type"].lower() == type.lower()]
    if max_price is not None:
        result = [c for c in result if c["price_per_day"] <= max_price]
    if is_available is not None:
        result = [c for c in result if c["is_available"] == is_available]
    return result

# -------------------------
# PYDANTIC MODELS
# -------------------------
class RentalRequest(BaseModel):
    customer_name: str = Field(min_length=2)
    car_id: int = Field(gt=0)
    days: int = Field(gt=0, le=30)
    rental_type: str = "self_drive"

class NewCar(BaseModel):
    name: str = Field(min_length=2)
    type: str = Field(min_length=2)
    price_per_day: int = Field(gt=0)
    is_available: bool = True

# -------------------------
# BEGINNER
# -------------------------
@app.get("/")
def home():
    return {"message": "Welcome to Car Rental System"}

@app.get("/cars")
def get_cars():
    return {"total": len(cars), "cars": cars}

@app.get("/cars/summary")
def summary():
    available = sum(1 for c in cars if c["is_available"])
    return {
        "total": len(cars),
        "available": available,
        "unavailable": len(cars) - available
    }


@app.get("/rentals")
def get_rentals():
    return {"total": len(rentals), "rentals": rentals}

# -------------------------
# EASY
# -------------------------
@app.post("/rent")
def rent_car(req: RentalRequest):
    global rental_counter

    car = find_car(req.car_id)
    if not car:
        return {"error": "Car not found"}

    if not car["is_available"]:
        return {"error": "Car not available"}

    total = calculate_cost(car["price_per_day"], req.days, req.rental_type)

    rental = {
        "rental_id": rental_counter,
        "customer_name": req.customer_name,
        "car_id": req.car_id,
        "days": req.days,
        "total_price": total,
        "status": "rented"
    }

    rentals.append(rental)
    rental_counter += 1
    car["is_available"] = False

    return rental

@app.get("/cars/filter")
def filter_cars(
    type: Optional[str] = None,
    max_price: Optional[int] = None,
    is_available: Optional[bool] = None
):
    result = filter_cars_logic(type, max_price, is_available)
    return {"count": len(result), "cars": result}


# -------------------------
# MEDIUM (CRUD)
# -------------------------
@app.post("/cars")
def add_car(car: NewCar, response: Response):
    for c in cars:
        if c["name"].lower() == car.name.lower():
            return {"error": "Car already exists"}

    new_car = car.dict()
    new_car["id"] = len(cars) + 1
    cars.append(new_car)
    response.status_code = 201
    return new_car

@app.put("/cars/{car_id}")
def update_car(car_id: int, price_per_day: Optional[int] = None, is_available: Optional[bool] = None):
    car = find_car(car_id)
    if not car:
        return {"error": "Car not found"}

    if price_per_day is not None:
        car["price_per_day"] = price_per_day
    if is_available is not None:
        car["is_available"] = is_available

    return car




# -------------------------
# HARD
# -------------------------
@app.get("/cars/search")
def search(keyword: str):
    result = [c for c in cars if keyword.lower() in c["name"].lower() or keyword.lower() in c["type"].lower()]
    if not result:
        return {"message": "No cars found"}
    return {"total": len(result), "cars": result}

@app.get("/cars/sort")
def sort_cars(sort_by: str = "price_per_day", order: str = "asc"):
    if sort_by not in ["price_per_day", "name", "type"]:
        return {"error": "Invalid sort field"}

    reverse = True if order == "desc" else False
    sorted_cars = sorted(cars, key=lambda x: x[sort_by], reverse=reverse)

    return {"sorted_by": sort_by, "order": order, "cars": sorted_cars}

@app.get("/cars/page")
def paginate(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    total = len(cars)
    total_pages = math.ceil(total / limit)

    return {
        "page": page,
        "total_pages": total_pages,
        "cars": cars[start:start + limit]
    }

@app.get("/cars/browse")
def browse(
    keyword: Optional[str] = None,
    sort_by: str = "price_per_day",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    result = cars

    if keyword:
        result = [c for c in result if keyword.lower() in c["name"].lower()]

    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    start = (page - 1) * limit
    total = len(result)

    return {
        "total": total,
        "page": page,
        "cars": result[start:start + limit]
    }
@app.get("/cars/{car_id}")
def get_car(car_id: int):
    car = find_car(car_id)
    if not car:
        return {"error": "Car not found"}
    return car
