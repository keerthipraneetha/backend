from datetime import datetime, timedelta
from app.services.user_service import UserService
from app.services.vehicle_service import VehicleService
from app.services.log_service import LogService
from app.models.user import UserCreate
from app.models.vehicle import VehicleCreate, FuelType, Provision, VehicleCondition, VehicleStatus, VehicleType
import asyncio

async def seed_users():
    """Create sample users"""
    user_service = UserService()
    
    users_data = [
        {
            "username": "admin",
            "email": "admin@vms.com",
            "password": "password",
            "fullName": "System Administrator",
            "role": "admin"
        },
        {
            "username": "manager",
            "email": "manager@vms.com",
            "password": "password",
            "fullName": "Fleet Manager",
            "role": "manager"
        },
        {
            "username": "operator",
            "email": "operator@vms.com",
            "password": "password",
            "fullName": "Vehicle Operator",
            "role": "operator"
        }
    ]
    
    created_users = []
    for user_data in users_data:
        # Check if user already exists
        existing_user = await user_service.get_user_by_username(user_data["username"])
        if not existing_user:
            user = await user_service.create_user(UserCreate(**user_data))
            created_users.append(user)
            print(f"Created user: {user.username}")
        else:
            created_users.append(existing_user)
            print(f"User already exists: {user_data['username']}")
    
    return created_users

async def seed_vehicles(users):
    """Create sample vehicles"""
    vehicle_service = VehicleService()
    
    admin_user = users[0]  # Use admin user as creator
    
    vehicles_data = [
        {
            "VehRegNo": "ABC-1234",
            "CustomerID": "CUST001",
            "MakeType": "Toyota",
            "Model": "Camry",
            "KMPL": 15.5,
            "VehicleGroup": "Sedan",
            "Category": "Official",
            "PurchaseDate": datetime.now() - timedelta(days=365),
            "VehicleCost": 25000.00,
            "PurchasedFrom": "Toyota Dealership",
            "RegistrationDate": datetime.now() - timedelta(days=360),
            "FuelType": FuelType.PETROL,
            "TankCapacity": 50.0,
            "SeatingCapacity": 5,
            "Provision": Provision.OWNED,
            "unitId": "UNIT001",
            "PresentUnitName": "Head Office",
            "PreviousUnitName": "",
            "EngineNumber": "ENG001",
            "ChassisNumber": "CHA001",
            "GoDate": datetime.now() - timedelta(days=360),
            "GoNumber": "GO001",
            "VehicleCondition": VehicleCondition.GOOD,
            "Remarks": "Primary official vehicle",
            "Status": VehicleStatus.ON_DUTY,
            "VehicleType": VehicleType.CAR
        },
        {
            "VehRegNo": "DEF-5678",
            "CustomerID": "CUST002",
            "MakeType": "Honda",
            "Model": "Civic",
            "KMPL": 18.2,
            "VehicleGroup": "Compact",
            "Category": "Pool",
            "PurchaseDate": datetime.now() - timedelta(days=200),
            "VehicleCost": 22000.00,
            "PurchasedFrom": "Honda Dealership",
            "RegistrationDate": datetime.now() - timedelta(days=195),
            "FuelType": FuelType.PETROL,
            "TankCapacity": 45.0,
            "SeatingCapacity": 5,
            "Provision": Provision.LEASED,
            "unitId": "UNIT002",
            "PresentUnitName": "Sales Department",
            "PreviousUnitName": "Marketing",
            "EngineNumber": "ENG002",
            "ChassisNumber": "CHA002",
            "GoDate": datetime.now() - timedelta(days=195),
            "GoNumber": "GO002",
            "VehicleCondition": VehicleCondition.GOOD,
            "Remarks": "Pool vehicle for sales team",
            "Status": VehicleStatus.ON_DUTY,
            "VehicleType": VehicleType.CAR
        },
        {
            "VehRegNo": "GHI-9012",
            "CustomerID": "CUST003",
            "MakeType": "Ford",
            "Model": "Transit",
            "KMPL": 12.0,
            "VehicleGroup": "Commercial",
            "Category": "Delivery",
            "PurchaseDate": datetime.now() - timedelta(days=500),
            "VehicleCost": 35000.00,
            "PurchasedFrom": "Ford Commercial",
            "RegistrationDate": datetime.now() - timedelta(days=495),
            "FuelType": FuelType.DIESEL,
            "TankCapacity": 80.0,
            "SeatingCapacity": 3,
            "Provision": Provision.OWNED,
            "unitId": "UNIT003",
            "PresentUnitName": "Logistics",
            "PreviousUnitName": "",
            "EngineNumber": "ENG003",
            "ChassisNumber": "CHA003",
            "GoDate": datetime.now() - timedelta(days=495),
            "GoNumber": "GO003",
            "VehicleCondition": VehicleCondition.FAIR,
            "Remarks": "Delivery vehicle - scheduled for maintenance",
            "Status": VehicleStatus.MAINTENANCE,
            "VehicleType": VehicleType.VAN
        },
        {
            "VehRegNo": "JKL-3456",
            "CustomerID": "CUST004",
            "MakeType": "Nissan",
            "Model": "Leaf",
            "KMPL": 120.0,  # km/charge equivalent
            "VehicleGroup": "Electric",
            "Category": "Executive",
            "PurchaseDate": datetime.now() - timedelta(days=100),
            "VehicleCost": 45000.00,
            "PurchasedFrom": "Nissan EV Center",
            "RegistrationDate": datetime.now() - timedelta(days=95),
            "FuelType": FuelType.ELECTRIC,
            "TankCapacity": 0.0,  # Battery capacity different
            "SeatingCapacity": 5,
            "Provision": Provision.OWNED,
            "unitId": "UNIT004",
            "PresentUnitName": "Executive Office",
            "PreviousUnitName": "",
            "EngineNumber": "ELEC001",
            "ChassisNumber": "CHA004",
            "GoDate": datetime.now() - timedelta(days=95),
            "GoNumber": "GO004",
            "VehicleCondition": VehicleCondition.NEW,
            "Remarks": "Executive electric vehicle",
            "Status": VehicleStatus.OFF_DUTY,
            "VehicleType": VehicleType.CAR
        },
        {
            "VehRegNo": "MNO-7890",
            "CustomerID": "CUST005",
            "MakeType": "Yamaha",
            "Model": "FZ",
            "KMPL": 45.0,
            "VehicleGroup": "Motorcycle",
            "Category": "Messenger",
            "PurchaseDate": datetime.now() - timedelta(days=300),
            "VehicleCost": 1500.00,
            "PurchasedFrom": "Yamaha Motors",
            "RegistrationDate": datetime.now() - timedelta(days=295),
            "FuelType": FuelType.PETROL,
            "TankCapacity": 12.0,
            "SeatingCapacity": 2,
            "Provision": Provision.OWNED,
            "unitId": "UNIT005",
            "PresentUnitName": "Courier Services",
            "PreviousUnitName": "",
            "EngineNumber": "ENG005",
            "ChassisNumber": "CHA005",
            "GoDate": datetime.now() - timedelta(days=295),
            "GoNumber": "GO005",
            "VehicleCondition": VehicleCondition.GOOD,
            "Remarks": "Messenger bike for quick deliveries",
            "Status": VehicleStatus.ON_DUTY,
            "VehicleType": VehicleType.TWO_WHEELER
        }
    ]
    
    created_vehicles = []
    for vehicle_data in vehicles_data:
        # Check if vehicle already exists
        existing_vehicle = await vehicle_service.get_vehicle_by_reg_no(vehicle_data["VehRegNo"])
        if not existing_vehicle:
            vehicle = await vehicle_service.create_vehicle(
                VehicleCreate(**vehicle_data),
                str(admin_user.id)
            )
            created_vehicles.append(vehicle)
            print(f"Created vehicle: {vehicle.VehRegNo}")
        else:
            created_vehicles.append(existing_vehicle)
            print(f"Vehicle already exists: {vehicle_data['VehRegNo']}")
    
    return created_vehicles

async def seed_logs(users, vehicles):
    """Create sample log entries"""
    log_service = LogService()
    
    admin_user = users[0]
    manager_user = users[1]
    
    # Create some sample log entries
    logs_data = [
        {
            "action": "VIEW",
            "entity_type": "vehicle",
            "entity_id": str(vehicles[0].id),
            "user_id": str(manager_user.id),
            "user_name": manager_user.fullName,
            "details": {"VehRegNo": vehicles[0].VehRegNo}
        },
        {
            "action": "UPDATE",
            "entity_type": "vehicle", 
            "entity_id": str(vehicles[1].id),
            "user_id": str(admin_user.id),
            "user_name": admin_user.fullName,
            "details": {
                "VehRegNo": vehicles[1].VehRegNo,
                "changes": {"Status": "ON_DUTY"}
            }
        }
    ]
    
    created_logs = []
    for log_data in logs_data:
        log = await log_service.create_log(**log_data)
        created_logs.append(log)
        print(f"Created log: {log.action} on {log.entityType}")
    
    return created_logs

async def seed_all_data():
    """Seed all sample data"""
    print("Starting data seeding...")
    
    # Seed users first
    print("\n--- Seeding Users ---")
    users = await seed_users()
    
    # Seed vehicles
    print("\n--- Seeding Vehicles ---")
    vehicles = await seed_vehicles(users)
    
    # Seed logs
    print("\n--- Seeding Logs ---")
    logs = await seed_logs(users, vehicles)
    
    print(f"\n--- Seeding Complete ---")
    print(f"Created {len(users)} users")
    print(f"Created {len(vehicles)} vehicles") 
    print(f"Created {len(logs)} logs")
    
    return {
        "users": users,
        "vehicles": vehicles,
        "logs": logs
    }

if __name__ == "__main__":
    # Run the seeding script
    asyncio.run(seed_all_data())