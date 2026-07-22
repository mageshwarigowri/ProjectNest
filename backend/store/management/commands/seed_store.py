from decimal import Decimal
from django.contrib.auth.models import User
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Category, Product

CATEGORIES = {
    "Robotics": ["Line Follower Robot", "Obstacle Avoider", "Bluetooth Rover", "Gesture Control Bot", "Maze Solver", "Mini Robotic Arm", "Voice Control Car", "Fire Fighter Bot", "Soccer Robot", "Delivery Rover"],
    "Internet of Things": ["Smart Home Hub", "Weather Monitor", "Plant Watering System", "Energy Meter", "Air Quality Station", "Smart Door Lock", "Parking Assistant", "Water Tank Monitor", "Pet Feeder", "Cold Storage Alert"],
    "Artificial Intelligence": ["Vision Sorter", "Face Attendance System", "Sign Language Reader", "Plant Disease Scanner", "Voice Assistant", "Waste Classifier", "Pose Coach", "Traffic Counter", "Emotion Display", "Study Companion"],
    "Web Development": ["Portfolio Website", "Event Booking Portal", "Recipe Community", "Learning Dashboard", "Job Board", "Expense Tracker", "Library Portal", "Habit Tracker", "Quiz Platform", "Local Business Site"],
    "Mobile Applications": ["Fitness Tracker App", "Campus Navigator", "Study Timer", "Meal Planner", "Travel Journal", "Emergency Contact App", "Budget Planner", "Flashcard App", "Volunteer Connect", "Queue Manager"],
    "Electronics": ["Digital Clock", "Audio Amplifier", "Bench Power Supply", "LED Music Visualizer", "Electronic Dice", "Battery Capacity Tester", "Touchless Bell", "Solar Charger", "Continuity Tester", "Mini Oscilloscope"],
    "Renewable Energy": ["Solar Tracker", "Mini Wind Turbine", "Hybrid Power Monitor", "Solar Irrigation Controller", "Energy Harvesting Demo", "Smart Street Light", "Solar Phone Charger", "Micro Hydro Model", "Sunlight Data Logger", "Greenhouse Controller"],
    "Cybersecurity": ["Network Security Lab", "Password Audit Tool", "Phishing Awareness Kit", "Secure Chat Demo", "File Integrity Monitor", "Web Security Sandbox", "USB Access Monitor", "Log Analysis Dashboard", "Encryption Learning Kit", "Home Firewall Lab"],
    "Data Science": ["Sales Forecast Studio", "Customer Insights Lab", "Sports Analytics Dashboard", "Movie Recommender", "Sentiment Explorer", "Housing Price Model", "Churn Prediction Lab", "Climate Data Explorer", "Retail Basket Analysis", "Survey Analytics Kit"],
    "Embedded Systems": ["Digital Thermostat", "RFID Access System", "Motor Speed Controller", "Ultrasonic Distance Meter", "Smart Alarm Clock", "Pulse Monitor", "Automated Garden Light", "Data Logger", "Keypad Security Lock", "Mini Elevator Controller"],
}
COLORS = ["#6d5dfc", "#00a884", "#ff7a59", "#377dff", "#d946ef", "#eab308", "#16a34a", "#ef4444", "#0891b2", "#7c3aed"]
IMAGE_KEYS = ["robot", "technology", "artificial-intelligence", "computer", "mobile", "electronics", "solar-energy", "cybersecurity", "data", "microcontroller"]

class Command(BaseCommand):
    help = "Create ten project categories with ten realistic products each."

    def handle(self, *args, **options):
        for c_index, (category_name, products) in enumerate(CATEGORIES.items()):
            category, _ = Category.objects.update_or_create(name=category_name, defaults={"slug": slugify(category_name), "description": f"Hands-on {category_name.lower()} projects with guided documentation and practical components.", "color": COLORS[c_index]})
            for p_index, name in enumerate(products):
                sku = f"PN-{c_index + 1:02d}-{p_index + 1:03d}"
                level = ["Beginner", "Intermediate", "Advanced"][p_index % 3]
                price = Decimal(699 + c_index * 90 + p_index * 145)
                Product.objects.update_or_create(sku=sku, defaults={
                    "category": category, "name": name, "slug": slugify(f"{name}-{sku}"),
                    "short_description": f"A complete {level.lower()} kit to build a working {name.lower()}.",
                    "description": f"Build a functional {name} while learning core {category_name.lower()} concepts. This {level.lower()} project includes the essential component set, structured source code, circuit or architecture guidance, setup instructions, and testing checklist. Ideal for portfolio demonstrations, coursework, and intern training.",
                    "price": price, "discount_percent": [0, 5, 10, 12, 15][(p_index + c_index) % 5],
                    "stock": [0, 3, 8, 14, 22, 35][(p_index * 2 + c_index) % 6], "low_stock_threshold": 5,
                    "rating": Decimal(f"{4 + ((p_index + c_index) % 10) / 10:.1f}"), "review_count": 12 + p_index * 9 + c_index * 4,
                    "image_url": f"https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=900&q=80&sig={c_index * 10 + p_index}",
                    "featured": p_index == 0, "active": True,
                })
        if settings.DEBUG:
            admin, created = User.objects.get_or_create(username="admin", defaults={"email": "admin@projectnest.local", "is_staff": True, "is_superuser": True})
            if created: admin.set_password("ChangeMe123!"); admin.save()
            admin_note = " Development admin: admin / ChangeMe123! (change immediately)."
        else:
            admin_note = " No production administrator was created."
        self.stdout.write(self.style.SUCCESS(f"Seeded 10 categories and 100 products.{admin_note}"))
