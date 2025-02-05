import os
import django
from faker import Faker
import random
from datetime import timedelta
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'raktkadi.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import (
    BloodBankProfile, 
    StaffProfile, 
    DonorProfile, 
    ConsumerProfile
)

fake = Faker()

# Blood groups
BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

def create_sequential_users(num_users=10):
    """Create users with sequential emails for each profile type."""
    Admin = get_user_model()
    
    # Dictionaries to store users
    blood_bank_users = []
    staff_users = []
    donor_users = []
    consumer_users = []

    for i in range(1, num_users + 1):
        # Create Blood Bank users
        bb_user = Admin.objects.create_user(
            email=f'hospital{i}@mail.com', 
            password='Pass1234', 
            name=fake.name(),
            contact=f"+1{fake.random_number(digits=10)}",
            user_type='BLOOD_BANK'
        )
        blood_bank_users.append(bb_user)

        # Create Staff users
        staff_user = Admin.objects.create_user(
            email=f'staff{i}@mail.com', 
            password='Pass1234', 
            name=fake.name(),
            contact=f"+1{fake.random_number(digits=10)}",
            user_type='STAFF'
        )
        staff_users.append(staff_user)

        # Create Donor users
        donor_user = Admin.objects.create_user(
            email=f'donor{i}@mail.com', 
            password='Pass1234', 
            name=fake.name(),
            contact=f"+1{fake.random_number(digits=10)}",
            user_type='DONOR'
        )
        donor_users.append(donor_user)

        # Create Consumer users
        consumer_user = Admin.objects.create_user(
            email=f'consumer{i}@mail.com', 
            password='Pass1234', 
            name=fake.name(),
            contact=f"+1{fake.random_number(digits=10)}",
            user_type='CONSUMER'
        )
        consumer_users.append(consumer_user)

    return {
        'blood_bank': blood_bank_users,
        'staff': staff_users,
        'donor': donor_users,
        'consumer': consumer_users
    }

def create_profiles(users_dict):
    """Create profiles for each user type."""
    # Blood Bank Profiles
    for user in users_dict['blood_bank']:
        BloodBankProfile.objects.create(
            user=user,
            address=fake.address(),
            status=random.choice(['PENDING', 'VERIFIED', 'REJECTED'])
        )

    # Staff Profiles
    for user in users_dict['staff']:
        StaffProfile.objects.create(
            user=user,
            role=random.choice(['Manager', 'Coordinator', 'Technician', 'Receptionist'])
        )

    # Donor Profiles
    for user in users_dict['donor']:
        DonorProfile.objects.create(
            user=user,
            blood_group=random.choice(BLOOD_GROUPS),
            last_donation=timezone.now().date() - timedelta(days=random.randint(30, 365)),
            address=fake.address()
        )

    # Consumer Profiles
    for user in users_dict['consumer']:
        ConsumerProfile.objects.create(
            user=user,
            blood_group=random.choice(BLOOD_GROUPS),
            address=fake.address()
        )

def main():
    """Generate dummy data with sequential emails."""
    # Delete existing database
    db_path = 'db.sqlite3'
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Deleted {db_path}")
    
    # Run migrations
    os.system('python manage.py migrate')

    # Create users and profiles
    users_dict = create_sequential_users(num_users=10)
    create_profiles(users_dict)

    # Create superuser
    Admin = get_user_model()
    Admin.objects.create_superuser(
        email='demo@demo.com', 
        password='demo', 
        name='demo admin',
        contact='+11234567890'
    )

    print("Dummy data generation complete!")

if __name__ == '__main__':
    main()