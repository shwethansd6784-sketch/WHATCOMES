"""
seed_data.py - Populates SQLite with 60+ realistic returns, 12 products, 6 suppliers,
inspections, recommendations, and corrective actions for ReturnWise demo.
"""

import json
from datetime import datetime, timedelta
import random
from database import init_db, get_db_connection
from recovery_engine import evaluate_recovery

SUPPLIERS = [
    {
        "code": "SUP-SND-01",
        "name": "SoundCraft Technologies",
        "contact_email": "qa@soundcraft-audio.demo",
        "category": "Audio & Acoustics",
        "quality_rating": 3.4,
        "lead_time_days": 18
    },
    {
        "code": "SUP-APX-02",
        "name": "ApexWear Electronics",
        "contact_email": "support@apexwear.demo",
        "category": "Wearables & Sensors",
        "quality_rating": 4.6,
        "lead_time_days": 12
    },
    {
        "code": "SUP-VLT-03",
        "name": "VoltPeak Power Solutions",
        "contact_email": "b2b@voltpeak-power.demo",
        "category": "Power & Charging",
        "quality_rating": 3.8,
        "lead_time_days": 10
    },
    {
        "code": "SUP-OPT-04",
        "name": "OptiCore Vision Systems",
        "contact_email": "vendor@opticore-vision.demo",
        "category": "Computer Peripherals",
        "quality_rating": 4.7,
        "lead_time_days": 14
    },
    {
        "code": "SUP-KEY-05",
        "name": "KeyForge Labs",
        "contact_email": "partners@keyforge-labs.demo",
        "category": "Gaming & Input",
        "quality_rating": 4.5,
        "lead_time_days": 16
    },
    {
        "code": "SUP-BRZ-06",
        "name": "BreezeTech Corp",
        "contact_email": "supply@breezetech.demo",
        "category": "Smart Home Appliances",
        "quality_rating": 4.8,
        "lead_time_days": 21
    }
]

PRODUCTS = [
    {
        "sku": "PRD-AURA-01",
        "name": "AuraWave ANC Wireless Headphones",
        "category": "Audio",
        "supplier_code": "SUP-SND-01",
        "retail_price": 149.99,
        "cost_price": 62.00,
        "units_sold": 850,
        "resale_eligible": 1,
        "processing_cost_base": 6.0
    },
    {
        "sku": "PRD-NEOB-02",
        "name": "NeoBass Portable Bluetooth Speaker",
        "category": "Audio",
        "supplier_code": "SUP-SND-01",
        "retail_price": 79.99,
        "cost_price": 31.00,
        "units_sold": 620,
        "resale_eligible": 1,
        "processing_cost_base": 5.0
    },
    {
        "sku": "PRD-PULS-03",
        "name": "PulseFit Pro Smartwatch",
        "category": "Wearables",
        "supplier_code": "SUP-APX-02",
        "retail_price": 199.99,
        "cost_price": 84.00,
        "units_sold": 1200,
        "resale_eligible": 1,
        "processing_cost_base": 7.0
    },
    {
        "sku": "PRD-TRCK-04",
        "name": "PulseFit Active Tracker Band",
        "category": "Wearables",
        "supplier_code": "SUP-APX-02",
        "retail_price": 49.99,
        "cost_price": 18.00,
        "units_sold": 950,
        "resale_eligible": 1,
        "processing_cost_base": 4.0
    },
    {
        "sku": "PRD-HYPR-05",
        "name": "HyperDrive 100W GaN Wall Charger",
        "category": "Mobile Accessories",
        "supplier_code": "SUP-VLT-03",
        "retail_price": 59.99,
        "cost_price": 22.00,
        "units_sold": 1400,
        "resale_eligible": 1,
        "processing_cost_base": 4.0
    },
    {
        "sku": "PRD-SOLR-06",
        "name": "SolarCharge 20000mAh PowerBank",
        "category": "Mobile Accessories",
        "supplier_code": "SUP-VLT-03",
        "retail_price": 45.99,
        "cost_price": 16.50,
        "units_sold": 780,
        "resale_eligible": 1,
        "processing_cost_base": 4.5
    },
    {
        "sku": "PRD-OMNI-07",
        "name": "OmniView 2K HDR Webcam",
        "category": "Computer Peripherals",
        "supplier_code": "SUP-OPT-04",
        "retail_price": 89.99,
        "cost_price": 38.00,
        "units_sold": 530,
        "resale_eligible": 1,
        "processing_cost_base": 5.0
    },
    {
        "sku": "PRD-DOCK-08",
        "name": "PowerSync 9-in-1 USB-C Docking Station",
        "category": "Computer Peripherals",
        "supplier_code": "SUP-OPT-04",
        "retail_price": 119.99,
        "cost_price": 49.00,
        "units_sold": 410,
        "resale_eligible": 1,
        "processing_cost_base": 6.5
    },
    {
        "sku": "PRD-ERGO-09",
        "name": "ErgoType RGB Mechanical Keyboard",
        "category": "Gaming & Input",
        "supplier_code": "SUP-KEY-05",
        "retail_price": 129.99,
        "cost_price": 54.00,
        "units_sold": 670,
        "resale_eligible": 1,
        "processing_cost_base": 6.0
    },
    {
        "sku": "PRD-Mous-10",
        "name": "UltraGrip Pro Wireless Gaming Mouse",
        "category": "Gaming & Input",
        "supplier_code": "SUP-KEY-05",
        "retail_price": 69.99,
        "cost_price": 28.00,
        "units_sold": 890,
        "resale_eligible": 1,
        "processing_cost_base": 4.5
    },
    {
        "sku": "PRD-AERO-11",
        "name": "AeroFlow Smart Oscillating Desk Fan",
        "category": "Smart Home",
        "supplier_code": "SUP-BRZ-06",
        "retail_price": 54.99,
        "cost_price": 23.00,
        "units_sold": 610,
        "resale_eligible": 1,
        "processing_cost_base": 5.0
    },
    {
        "sku": "PRD-LAMP-12",
        "name": "LuminaGlow Smart Ambient Desk Lamp",
        "category": "Smart Home",
        "supplier_code": "SUP-BRZ-06",
        "retail_price": 39.99,
        "cost_price": 16.00,
        "units_sold": 450,
        "resale_eligible": 1,
        "processing_cost_base": 4.0
    }
]

CUSTOMERS = [
    "Alex Rivera", "David Miller", "Sophia Taylor", "Liam Chen", "Emma Wilson",
    "Noah Garcia", "Olivia Brown", "Ethan Patel", "Ava Martinez", "Lucas Jones",
    "Mia Anderson", "Mason Thomas", "Isabella Jackson", "Oliver White", "Charlotte Harris",
    "Benjamin Clark", "Amelia Lewis", "Elijah Robinson", "Harper Walker", "James Hall",
    "Evelyn Allen", "Logan Young", "Abigail King", "Alexander Wright", "Emily Scott",
    "Daniel Torres", "Elizabeth Nguyen", "Matthew Hill", "Mila Flores", "Henry Green"
]

INSPECTORS = [
    "David Martinez (Tech Lead)",
    "Sarah Jenkins (Senior QA)",
    "Robert Chen (Diagnostics)",
    "Jessica Taylor (Returns Triage)"
]

def seed_database():
    """Initializes schema and inserts complete realistic demo data."""
    init_db(force_recreate=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Insert Suppliers
    supplier_map = {}
    for s in SUPPLIERS:
        cursor.execute("""
            INSERT INTO suppliers (code, name, contact_email, category, quality_rating, lead_time_days)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (s["code"], s["name"], s["contact_email"], s["category"], s["quality_rating"], s["lead_time_days"]))
        supplier_map[s["code"]] = cursor.lastrowid

    # 2. Insert Products
    product_map = {}
    for p in PRODUCTS:
        supp_id = supplier_map[p["supplier_code"]]
        cursor.execute("""
            INSERT INTO products (sku, name, category, supplier_id, retail_price, cost_price, units_sold, resale_eligible, processing_cost_base)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (p["sku"], p["name"], p["category"], supp_id, p["retail_price"], p["cost_price"], p["units_sold"], p["resale_eligible"], p["processing_cost_base"]))
        product_map[p["sku"]] = {
            "id": cursor.lastrowid,
            "sku": p["sku"],
            "name": p["name"],
            "category": p["category"],
            "supplier_id": supp_id,
            "supplier_name": [s["name"] for s in SUPPLIERS if s["code"] == p["supplier_code"]][0],
            "retail_price": p["retail_price"],
            "resale_eligible": p["resale_eligible"],
            "processing_cost_base": p["processing_cost_base"]
        }

    # 3. Carefully crafted return records (Total 60 returns)
    base_date = datetime(2026, 10, 9)

    return_records = [
        # --- HACKATHON DEMO ITEM 1: AuraWave Headphones pending inspection ---
        {
            "code": "RET-1002",
            "order_id": "ORD-90214",
            "sku": "PRD-AURA-01",
            "customer": "Alex Rivera",
            "reason": "Defective product",
            "comment": "Left earbud audio cuts out completely after 2 minutes of playback.",
            "days_ago": 1,
            "status": "Pending Inspection",
            "inspect": False  # User / Judge will inspect this live!
        },
        # --- HACKATHON DEMO ITEM 2: PulseFit Pro Smartwatch pending inspection (Unopened restock candidate) ---
        {
            "code": "RET-1014",
            "order_id": "ORD-90412",
            "sku": "PRD-PULS-03",
            "customer": "David Miller",
            "reason": "Customer changed mind",
            "comment": "Bought as a birthday gift but recipient already has one. Factory seal unbroken.",
            "days_ago": 2,
            "status": "Pending Inspection",
            "inspect": False  # User / Judge can inspect this live to see instant Restock!
        },
        # --- AuraWave ANC Headphones Defect Pattern (SoundCraft Tech) ---
        {
            "code": "RET-1001",
            "order_id": "ORD-90105",
            "sku": "PRD-AURA-01",
            "customer": "Sophia Taylor",
            "reason": "Defective product",
            "comment": "Cracking static in left earcup, microphone fails on calls.",
            "days_ago": 22,
            "status": "Inspected",
            "inspect": True,
            "condition": "Confirmed defective",
            "functionality": "Complete Failure / Dead",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "Acoustic driver voice-coil open circuit verified on audio analyzer."
        },
        {
            "code": "RET-1003",
            "order_id": "ORD-90240",
            "sku": "PRD-AURA-01",
            "customer": "Liam Chen",
            "reason": "Defective product",
            "comment": "No sound from left speaker at all. Right side works fine.",
            "days_ago": 19,
            "status": "Inspected",
            "inspect": True,
            "condition": "Confirmed defective",
            "functionality": "Intermittent Fault",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "Left transducer solder point fractured during assembly."
        },
        {
            "code": "RET-1004",
            "order_id": "ORD-90278",
            "sku": "PRD-AURA-01",
            "customer": "Emma Wilson",
            "reason": "Defective product",
            "comment": "Loud buzzing in left channel whenever ANC is activated.",
            "days_ago": 15,
            "status": "Inspected",
            "inspect": True,
            "condition": "Confirmed defective",
            "functionality": "Complete Failure / Dead",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "ANC internal feedback mic failed bench test. Consistent with driver assembly batch #41."
        },
        {
            "code": "RET-1005",
            "order_id": "ORD-90310",
            "sku": "PRD-AURA-01",
            "customer": "Noah Garcia",
            "reason": "Defective product",
            "comment": "Left ear audio distorted and volume is very low.",
            "days_ago": 12,
            "status": "Inspected",
            "inspect": True,
            "condition": "Confirmed defective",
            "functionality": "Complete Failure / Dead",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "Driver diaphragm friction causing acoustic harmonic distortion >14%."
        },
        {
            "code": "RET-1006",
            "order_id": "ORD-90342",
            "sku": "PRD-AURA-01",
            "customer": "Olivia Brown",
            "reason": "Defective product",
            "comment": "Audio cuts out randomly every few seconds.",
            "days_ago": 8,
            "status": "Inspected",
            "inspect": True,
            "condition": "Confirmed defective",
            "functionality": "Intermittent Fault",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "Intermittent ribbon cable detachment at left pivot hinge."
        },
        {
            "code": "RET-1007",
            "order_id": "ORD-90390",
            "sku": "PRD-AURA-01",
            "customer": "Ethan Patel",
            "reason": "Customer changed mind",
            "comment": "Too bulky for my commute, decided to buy in-ear earbuds.",
            "days_ago": 5,
            "status": "Inspected",
            "inspect": True,
            "condition": "Opened and working",
            "functionality": "Fully Functional",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "All hardware functions pass 100%. Approved for Open-Box refurbishing."
        },
        {
            "code": "RET-1008",
            "order_id": "ORD-90425",
            "sku": "PRD-AURA-01",
            "customer": "Ava Martinez",
            "reason": "Defective product",
            "comment": "Headphones won't turn on or charge.",
            "days_ago": 3,
            "status": "Pending Inspection",
            "inspect": False
        },

        # --- HyperDrive 100W GaN Wall Charger (VoltPeak - Packaging Vulnerability) ---
        {
            "code": "RET-1009",
            "order_id": "ORD-88120",
            "sku": "PRD-HYPR-05",
            "customer": "Lucas Jones",
            "reason": "Damaged packaging",
            "comment": "Outer shipping box and product retail box completely smashed.",
            "days_ago": 28,
            "status": "Inspected",
            "inspect": True,
            "condition": "Damaged",
            "functionality": "Fully Functional",
            "packaging": "Torn / Distressed",
            "missing": "None",
            "notes": "Packaging cardboard crushed. Charger unit itself passed 100W electrical load test with zero flaws."
        },
        {
            "code": "RET-1010",
            "order_id": "ORD-88195",
            "sku": "PRD-HYPR-05",
            "customer": "Mia Anderson",
            "reason": "Damaged packaging",
            "comment": "Retail box was torn and taped back together.",
            "days_ago": 24,
            "status": "Inspected",
            "inspect": True,
            "condition": "Damaged",
            "functionality": "Fully Functional",
            "packaging": "Torn / Distressed",
            "missing": "None",
            "notes": "Inner plastic tray cracked. Electrical bench test passed 100% (20V/5A sustained)."
        },
        {
            "code": "RET-1011",
            "order_id": "ORD-88240",
            "sku": "PRD-HYPR-05",
            "customer": "Mason Thomas",
            "reason": "Damaged packaging",
            "comment": "Corner of packaging ripped, didn't want to gift a torn box.",
            "days_ago": 20,
            "status": "Inspected",
            "inspect": True,
            "condition": "Damaged",
            "functionality": "Fully Functional",
            "packaging": "Torn / Distressed",
            "missing": "None",
            "notes": "Cosmetic box damage only. Unit operates flawlessly."
        },
        {
            "code": "RET-1012",
            "order_id": "ORD-88310",
            "sku": "PRD-HYPR-05",
            "customer": "Isabella Jackson",
            "reason": "Damaged packaging",
            "comment": "Box arrived crushed flat.",
            "days_ago": 16,
            "status": "Inspected",
            "inspect": True,
            "condition": "Damaged",
            "functionality": "Cosmetic Damage Only",
            "packaging": "Torn / Distressed",
            "missing": "None",
            "notes": "External shell has minor scuff from carton puncture. Electronics test OK."
        },
        {
            "code": "RET-1013",
            "order_id": "ORD-88402",
            "sku": "PRD-HYPR-05",
            "customer": "Oliver White",
            "reason": "Damaged packaging",
            "comment": "Box crushed on one side.",
            "days_ago": 4,
            "status": "Pending Inspection",
            "inspect": False
        },

        # --- SolarCharge 20000mAh PowerBank (VoltPeak - Spec Description Mismatch) ---
        {
            "code": "RET-1015",
            "order_id": "ORD-89101",
            "sku": "PRD-SOLR-06",
            "customer": "Charlotte Harris",
            "reason": "Incorrect product description",
            "comment": "Website says 20,000mAh, but product label clearly says 10,000mAh capacity!",
            "days_ago": 25,
            "status": "Inspected",
            "inspect": True,
            "condition": "Opened and working",
            "functionality": "Fully Functional",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "Physical unit printed silk-screen says '10,000mAh 37Wh'. Website catalog copy error confirmed."
        },
        {
            "code": "RET-1016",
            "order_id": "ORD-89180",
            "sku": "PRD-SOLR-06",
            "customer": "Benjamin Clark",
            "reason": "Incorrect product description",
            "comment": "Spec mismatch: Received 10000mAh power bank instead of 20000mAh as advertised.",
            "days_ago": 21,
            "status": "Inspected",
            "inspect": True,
            "condition": "Opened and working",
            "functionality": "Fully Functional",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "Unit verified 10,000mAh. Operates normally; listing spec is wrong."
        },
        {
            "code": "RET-1017",
            "order_id": "ORD-89240",
            "sku": "PRD-SOLR-06",
            "customer": "Amelia Lewis",
            "reason": "Incorrect product description",
            "comment": "Item rating is 10k mAh on the box, not 20k mAh as ordered.",
            "days_ago": 17,
            "status": "Inspected",
            "inspect": True,
            "condition": "Unopened",
            "functionality": "Untested",
            "packaging": "Original Sealed",
            "missing": "None",
            "notes": "Factory seal intact. Outer box barcode PRD-SOLR-06 has correct SKU but 10,000mAh marking."
        },
        {
            "code": "RET-1018",
            "order_id": "ORD-89315",
            "sku": "PRD-SOLR-06",
            "customer": "Elijah Robinson",
            "reason": "Incorrect product description",
            "comment": "Misleading product page. This is half the battery capacity advertised.",
            "days_ago": 11,
            "status": "Inspected",
            "inspect": True,
            "condition": "Opened and working",
            "functionality": "Fully Functional",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "Verified working 10Ah battery. Zero electrical defect."
        },
        {
            "code": "RET-1019",
            "order_id": "ORD-89400",
            "sku": "PRD-SOLR-06",
            "customer": "Harper Walker",
            "reason": "Incorrect product description",
            "comment": "Listed as 20000mAh on site, received 10000mAh model.",
            "days_ago": 3,
            "status": "Pending Inspection",
            "inspect": False
        },

        # --- PulseFit Pro Smartwatch (ApexWear - Compatibility Friction / Buyer Remorse) ---
        {
            "code": "RET-1020",
            "order_id": "ORD-87110",
            "sku": "PRD-PULS-03",
            "customer": "James Hall",
            "reason": "Incompatible product",
            "comment": "Could not pair with iPhone on iOS 16. App kept dropping Bluetooth connection.",
            "days_ago": 26,
            "status": "Inspected",
            "inspect": True,
            "condition": "Opened and working",
            "functionality": "Fully Functional",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "Paired immediately to test iPhone 14. Customer likely did not allow Bluetooth location permission in iOS."
        },
        {
            "code": "RET-1021",
            "order_id": "ORD-87185",
            "sku": "PRD-PULS-03",
            "customer": "Evelyn Allen",
            "reason": "Incompatible product",
            "comment": "Doesn't sync properly with Apple Health.",
            "days_ago": 23,
            "status": "Inspected",
            "inspect": True,
            "condition": "Opened and working",
            "functionality": "Fully Functional",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "Firmware 2.1 applied. HealthKit sync confirmed working normally."
        },
        {
            "code": "RET-1022",
            "order_id": "ORD-87240",
            "sku": "PRD-PULS-03",
            "customer": "Logan Young",
            "reason": "Customer changed mind",
            "comment": "Color didn't look like what I expected.",
            "days_ago": 18,
            "status": "Inspected",
            "inspect": True,
            "condition": "Unopened",
            "functionality": "Untested",
            "packaging": "Original Sealed",
            "missing": "None",
            "notes": "Factory seal intact. Flawless Grade-A condition."
        },
        {
            "code": "RET-1023",
            "order_id": "ORD-87312",
            "sku": "PRD-PULS-03",
            "customer": "Abigail King",
            "reason": "Customer changed mind",
            "comment": "Decided to keep my old watch.",
            "days_ago": 14,
            "status": "Inspected",
            "inspect": True,
            "condition": "Opened and working",
            "functionality": "Fully Functional",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "Screen protector peeled off but display mint. Cleared for certified open-box."
        },
        {
            "code": "RET-1024",
            "order_id": "ORD-87390",
            "sku": "PRD-PULS-03",
            "customer": "Alexander Wright",
            "reason": "Missing components",
            "comment": "Magnetic charging cable was missing from box.",
            "days_ago": 9,
            "status": "Inspected",
            "inspect": True,
            "condition": "Missing components",
            "functionality": "Fully Functional",
            "packaging": "Opened Intact",
            "missing": "Magnetic USB Charging Cable",
            "notes": "Watch powers on with bench charger. Missing proprietary cable."
        },

        # --- PulseFit Active Tracker Band (ApexWear) ---
        {
            "code": "RET-1025",
            "order_id": "ORD-86104",
            "sku": "PRD-TRCK-04",
            "customer": "Emily Scott",
            "reason": "Customer changed mind",
            "comment": "Screen is too small for me to read comfortably.",
            "days_ago": 27,
            "status": "Inspected",
            "inspect": True,
            "condition": "Opened and working",
            "functionality": "Fully Functional",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "Full test pass. OLED bright and responsive."
        },
        {
            "code": "RET-1026",
            "order_id": "ORD-86210",
            "sku": "PRD-TRCK-04",
            "customer": "Daniel Torres",
            "reason": "Defective product",
            "comment": "Step counter does not record any steps.",
            "days_ago": 22,
            "status": "Inspected",
            "inspect": True,
            "condition": "Confirmed defective",
            "functionality": "Complete Failure / Dead",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "Internal 3-axis accelerometer sensor unresponsive."
        },
        {
            "code": "RET-1027",
            "order_id": "ORD-86280",
            "sku": "PRD-TRCK-04",
            "customer": "Elizabeth Nguyen",
            "reason": "Customer changed mind",
            "comment": "Unopened, returned within return policy.",
            "days_ago": 15,
            "status": "Inspected",
            "inspect": True,
            "condition": "Unopened",
            "functionality": "Untested",
            "packaging": "Original Sealed",
            "missing": "None",
            "notes": "Sealed in protective film. Immediate restock."
        },

        # --- NeoBass Portable Bluetooth Speaker (SoundCraft) ---
        {
            "code": "RET-1028",
            "order_id": "ORD-85102",
            "sku": "PRD-NEOB-02",
            "customer": "Matthew Hill",
            "reason": "Customer changed mind",
            "comment": "Wanted the black version instead of teal.",
            "days_ago": 25,
            "status": "Inspected",
            "inspect": True,
            "condition": "Unopened",
            "functionality": "Untested",
            "packaging": "Original Sealed",
            "missing": "None",
            "notes": "Sealed original packaging. Restock approved."
        },
        {
            "code": "RET-1029",
            "order_id": "ORD-85190",
            "sku": "PRD-NEOB-02",
            "customer": "Mila Flores",
            "reason": "Defective product",
            "comment": "Distorted sound at volume above 50%.",
            "days_ago": 19,
            "status": "Inspected",
            "inspect": True,
            "condition": "Confirmed defective",
            "functionality": "Intermittent Fault",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "Passive bass radiator rubber surround torn from chassis."
        },
        {
            "code": "RET-1030",
            "order_id": "ORD-85260",
            "sku": "PRD-NEOB-02",
            "customer": "Henry Green",
            "reason": "Customer changed mind",
            "comment": "Sound is good but needed something bigger for backyard.",
            "days_ago": 10,
            "status": "Inspected",
            "inspect": True,
            "condition": "Opened and working",
            "functionality": "Fully Functional",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "Passed audio frequency sweep test."
        },

        # --- OmniView 2K HDR Webcam (OptiCore) ---
        {
            "code": "RET-1031",
            "order_id": "ORD-84115",
            "sku": "PRD-OMNI-07",
            "customer": "Alex Rivera",
            "reason": "Incompatible product",
            "comment": "Doesn't work with my workplace Chromebook USB port.",
            "days_ago": 28,
            "status": "Inspected",
            "inspect": True,
            "condition": "Opened and working",
            "functionality": "Fully Functional",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "Tested on Windows, macOS, and ChromeOS via USB-C. Functions at 2K 60fps."
        },
        {
            "code": "RET-1032",
            "order_id": "ORD-84220",
            "sku": "PRD-OMNI-07",
            "customer": "David Miller",
            "reason": "Customer changed mind",
            "comment": "Company provided an official webcam right after I bought this.",
            "days_ago": 20,
            "status": "Inspected",
            "inspect": True,
            "condition": "Unopened",
            "functionality": "Untested",
            "packaging": "Original Sealed",
            "missing": "None",
            "notes": "Original factory seal untouched."
        },
        {
            "code": "RET-1033",
            "order_id": "ORD-84310",
            "sku": "PRD-OMNI-07",
            "customer": "Sophia Taylor",
            "reason": "Defective product",
            "comment": "Purple lines across camera image sensor.",
            "days_ago": 13,
            "status": "Inspected",
            "inspect": True,
            "condition": "Confirmed defective",
            "functionality": "Complete Failure / Dead",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "CMOS sensor row failure. Verified by video analyzer."
        },

        # --- PowerSync 9-in-1 Docking Station (OptiCore) ---
        {
            "code": "RET-1034",
            "order_id": "ORD-83110",
            "sku": "PRD-DOCK-08",
            "customer": "Liam Chen",
            "reason": "Incompatible product",
            "comment": "HDMI 2 port does not support dual 4K monitors on my laptop model.",
            "days_ago": 27,
            "status": "Inspected",
            "inspect": True,
            "condition": "Opened and working",
            "functionality": "Fully Functional",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "Customer laptop lacks DisplayPort 1.4 MST support. Dock hardware operates 100% to spec."
        },
        {
            "code": "RET-1035",
            "order_id": "ORD-83204",
            "sku": "PRD-DOCK-08",
            "customer": "Emma Wilson",
            "reason": "Missing components",
            "comment": "Host USB-C connection cable was missing in the package.",
            "days_ago": 17,
            "status": "Inspected",
            "inspect": True,
            "condition": "Missing components",
            "functionality": "Fully Functional",
            "packaging": "Opened Intact",
            "missing": "USB-C to USB-C Host Cable (1m)",
            "notes": "Main dock works on bench cable. Replenish with spare cable or liquidate."
        },
        {
            "code": "RET-1036",
            "order_id": "ORD-83290",
            "sku": "PRD-DOCK-08",
            "customer": "Noah Garcia",
            "reason": "Customer changed mind",
            "comment": "Decided on a monitor with built-in hub instead.",
            "days_ago": 8,
            "status": "Inspected",
            "inspect": True,
            "condition": "Unopened",
            "functionality": "Untested",
            "packaging": "Original Sealed",
            "missing": "None",
            "notes": "Grade-A sealed restock."
        },

        # --- ErgoType RGB Mechanical Keyboard (KeyForge Labs) ---
        {
            "code": "RET-1037",
            "order_id": "ORD-82109",
            "sku": "PRD-ERGO-09",
            "customer": "Olivia Brown",
            "reason": "Customer changed mind",
            "comment": "Switches are louder than I expected for office use.",
            "days_ago": 26,
            "status": "Inspected",
            "inspect": True,
            "condition": "Opened and working",
            "functionality": "Fully Functional",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "All 87 keys tested on matrix tester. Zero debounce or chattering issues."
        },
        {
            "code": "RET-1038",
            "order_id": "ORD-82195",
            "sku": "PRD-ERGO-09",
            "customer": "Ethan Patel",
            "reason": "Wrong item delivered",
            "comment": "Ordered tactile brown switches, box arrived with clicky blue switches.",
            "days_ago": 19,
            "status": "Inspected",
            "inspect": True,
            "condition": "Unopened",
            "functionality": "Untested",
            "packaging": "Original Sealed",
            "missing": "None",
            "notes": "Warehouse fulfillment pick error. Product is brand new sealed."
        },
        {
            "code": "RET-1039",
            "order_id": "ORD-82280",
            "sku": "PRD-ERGO-09",
            "customer": "Ava Martinez",
            "reason": "Defective product",
            "comment": "Spacebar keycap sticks down and does not bounce back.",
            "days_ago": 12,
            "status": "Inspected",
            "inspect": True,
            "condition": "Confirmed defective",
            "functionality": "Intermittent Fault",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "Spacebar stabilizer wire dislodged from plate clip."
        },

        # --- UltraGrip Pro Wireless Gaming Mouse (KeyForge Labs) ---
        {
            "code": "RET-1040",
            "order_id": "ORD-81112",
            "sku": "PRD-Mous-10",
            "customer": "Lucas Jones",
            "reason": "Customer changed mind",
            "comment": "Shape is too large for my hand grip style.",
            "days_ago": 25,
            "status": "Inspected",
            "inspect": True,
            "condition": "Opened and working",
            "functionality": "Fully Functional",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "Optical sensor tracking 100%. Skate pads immaculate."
        },
        {
            "code": "RET-1041",
            "order_id": "ORD-81205",
            "sku": "PRD-Mous-10",
            "customer": "Mia Anderson",
            "reason": "Missing components",
            "comment": "Wireless USB dongle receiver was missing inside battery compartment.",
            "days_ago": 16,
            "status": "Inspected",
            "inspect": True,
            "condition": "Missing components",
            "functionality": "Fully Functional",
            "packaging": "Opened Intact",
            "missing": "2.4GHz USB Nano Receiver",
            "notes": "Tested in Bluetooth mode - operates fine. Missing 2.4GHz dongle."
        },
        {
            "code": "RET-1042",
            "order_id": "ORD-81290",
            "sku": "PRD-Mous-10",
            "customer": "Mason Thomas",
            "reason": "Customer changed mind",
            "comment": "Never opened, bought two by accident.",
            "days_ago": 7,
            "status": "Inspected",
            "inspect": True,
            "condition": "Unopened",
            "functionality": "Untested",
            "packaging": "Original Sealed",
            "missing": "None",
            "notes": "Mint sealed package. Restock approved."
        },

        # --- AeroFlow Smart Desk Fan (BreezeTech Corp) ---
        {
            "code": "RET-1043",
            "order_id": "ORD-80104",
            "sku": "PRD-AERO-11",
            "customer": "Isabella Jackson",
            "reason": "Customer changed mind",
            "comment": "Summer ended before I used it.",
            "days_ago": 27,
            "status": "Inspected",
            "inspect": True,
            "condition": "Unopened",
            "functionality": "Untested",
            "packaging": "Original Sealed",
            "missing": "None",
            "notes": "Pristine sealed unit."
        },
        {
            "code": "RET-1044",
            "order_id": "ORD-80192",
            "sku": "PRD-AERO-11",
            "customer": "Oliver White",
            "reason": "Defective product",
            "comment": "Oscillation motor clicks loudly while rotating.",
            "days_ago": 18,
            "status": "Inspected",
            "inspect": True,
            "condition": "Confirmed defective",
            "functionality": "Intermittent Fault",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "Oscillating gearbox gear tooth stripped."
        },
        {
            "code": "RET-1045",
            "order_id": "ORD-80277",
            "sku": "PRD-AERO-11",
            "customer": "Charlotte Harris",
            "reason": "Customer changed mind",
            "comment": "A bit louder on turbo mode than I preferred.",
            "days_ago": 11,
            "status": "Inspected",
            "inspect": True,
            "condition": "Opened and working",
            "functionality": "Fully Functional",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "Airflow decibel reading is within manufacturer spec (44dB)."
        },

        # --- LuminaGlow Smart Desk Lamp (BreezeTech Corp) ---
        {
            "code": "RET-1046",
            "order_id": "ORD-79108",
            "sku": "PRD-LAMP-12",
            "customer": "Benjamin Clark",
            "reason": "Customer changed mind",
            "comment": "Color temperature doesn't match my room decor.",
            "days_ago": 26,
            "status": "Inspected",
            "inspect": True,
            "condition": "Opened and working",
            "functionality": "Fully Functional",
            "packaging": "Opened Intact",
            "missing": "None",
            "notes": "LED array tested across 2700K - 6500K spectrum. Pass."
        },
        {
            "code": "RET-1047",
            "order_id": "ORD-79214",
            "sku": "PRD-LAMP-12",
            "customer": "Amelia Lewis",
            "reason": "Damaged packaging",
            "comment": "Lamp arm was fine, but box was torn in shipping.",
            "days_ago": 15,
            "status": "Inspected",
            "inspect": True,
            "condition": "Damaged",
            "functionality": "Fully Functional",
            "packaging": "Torn / Distressed",
            "missing": "None",
            "notes": "Cosmetic packaging tear. Aluminum lamp base pristine."
        },

        # --- ADDITIONAL RECENT PENDING / MIXED RETURNS FOR REALISTIC FLEET ---
        {
            "code": "RET-1048",
            "order_id": "ORD-91001",
            "sku": "PRD-AURA-01",
            "customer": "Elijah Robinson",
            "reason": "Defective product",
            "comment": "Left ear speaker cutting out. Same issue as my colleague experienced.",
            "days_ago": 3,
            "status": "Pending Inspection",
            "inspect": False
        },
        {
            "code": "RET-1049",
            "order_id": "ORD-91012",
            "sku": "PRD-HYPR-05",
            "customer": "Harper Walker",
            "reason": "Customer changed mind",
            "comment": "Got a charger included with new laptop.",
            "days_ago": 4,
            "status": "Pending Inspection",
            "inspect": False
        },
        {
            "code": "RET-1050",
            "order_id": "ORD-91024",
            "sku": "PRD-PULS-03",
            "customer": "James Hall",
            "reason": "Customer changed mind",
            "comment": "Unopened returned item.",
            "days_ago": 5,
            "status": "Pending Inspection",
            "inspect": False
        },
        {
            "code": "RET-1051",
            "order_id": "ORD-91036",
            "sku": "PRD-ERGO-09",
            "customer": "Evelyn Allen",
            "reason": "Customer changed mind",
            "comment": "Keyboard layout didn't suit my workflow.",
            "days_ago": 2,
            "status": "Pending Inspection",
            "inspect": False
        },
        {
            "code": "RET-1052",
            "order_id": "ORD-91048",
            "sku": "PRD-OMNI-07",
            "customer": "Logan Young",
            "reason": "Wrong item delivered",
            "comment": "Received 1080p webcam model instead of 2K HDR model.",
            "days_ago": 2,
            "status": "Pending Inspection",
            "inspect": False
        },
        {
            "code": "RET-1053",
            "order_id": "ORD-91060",
            "sku": "PRD-SOLR-06",
            "customer": "Abigail King",
            "reason": "Incorrect product description",
            "comment": "Packaging says 10000mAh, web description states 20000mAh.",
            "days_ago": 1,
            "status": "Pending Inspection",
            "inspect": False
        },
        {
            "code": "RET-1054",
            "order_id": "ORD-91072",
            "sku": "PRD-NEOB-02",
            "customer": "Alexander Wright",
            "reason": "Customer changed mind",
            "comment": "Color didn't match.",
            "days_ago": 6,
            "status": "Pending Inspection",
            "inspect": False
        },
        {
            "code": "RET-1055",
            "order_id": "ORD-91084",
            "sku": "PRD-TRCK-04",
            "customer": "Emily Scott",
            "reason": "Customer changed mind",
            "comment": "Bought another brand.",
            "days_ago": 7,
            "status": "Pending Inspection",
            "inspect": False
        },
        {
            "code": "RET-1056",
            "order_id": "ORD-91096",
            "sku": "PRD-DOCK-08",
            "customer": "Daniel Torres",
            "reason": "Customer changed mind",
            "comment": "Don't need docking station anymore.",
            "days_ago": 6,
            "status": "Pending Inspection",
            "inspect": False
        },
        {
            "code": "RET-1057",
            "order_id": "ORD-91108",
            "sku": "PRD-Mous-10",
            "customer": "Elizabeth Nguyen",
            "reason": "Other",
            "comment": "Ordered duplicate during checkout.",
            "days_ago": 4,
            "status": "Pending Inspection",
            "inspect": False
        },
        {
            "code": "RET-1058",
            "order_id": "ORD-91120",
            "sku": "PRD-AERO-11",
            "customer": "Matthew Hill",
            "reason": "Customer changed mind",
            "comment": "Moving to air-conditioned apartment.",
            "days_ago": 5,
            "status": "Pending Inspection",
            "inspect": False
        },
        {
            "code": "RET-1059",
            "order_id": "ORD-91132",
            "sku": "PRD-LAMP-12",
            "customer": "Mila Flores",
            "reason": "Other",
            "comment": "Unopened item.",
            "days_ago": 3,
            "status": "Pending Inspection",
            "inspect": False
        },
        {
            "code": "RET-1060",
            "order_id": "ORD-91144",
            "sku": "PRD-AURA-01",
            "customer": "Henry Green",
            "reason": "Customer changed mind",
            "comment": "Found alternative on sale.",
            "days_ago": 1,
            "status": "Pending Inspection",
            "inspect": False
        }
    ]

    # Insert Return Records & Inspections & Recommendations
    for item in return_records:
        prd = product_map[item["sku"]]
        ret_date = (base_date - timedelta(days=item["days_ago"])).strftime("%Y-%m-%d")
        
        cursor.execute("""
            INSERT INTO returns (return_code, order_id, product_id, customer_name, customer_reason, customer_comment, return_date, status, financial_value)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item["code"],
            item["order_id"],
            prd["id"],
            item["customer"],
            item["reason"],
            item["comment"],
            ret_date,
            item["status"],
            prd["retail_price"]
        ))
        return_id = cursor.lastrowid

        # If pre-inspected, record inspection & generate recommendation
        if item.get("inspect", False):
            insp_date = (base_date - timedelta(days=max(0, item["days_ago"] - 1))).strftime("%Y-%m-%d")
            inspector = random.choice(INSPECTORS)
            cursor.execute("""
                INSERT INTO inspections (return_id, inspection_date, inspector_name, item_condition, functionality_status, packaging_condition, missing_components, inspection_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                return_id,
                insp_date,
                inspector,
                item["condition"],
                item["functionality"],
                item["packaging"],
                item.get("missing", "None"),
                item["notes"]
            ))

            # Run recommendation engine
            rec = evaluate_recovery(
                item_condition=item["condition"],
                functionality_status=item["functionality"],
                packaging_condition=item["packaging"],
                missing_components=item.get("missing", "None"),
                retail_price=prd["retail_price"],
                resale_eligible=bool(prd["resale_eligible"]),
                processing_cost_base=prd["processing_cost_base"],
                customer_reason=item["reason"],
                supplier_name=prd["supplier_name"],
                category=prd["category"]
            )

            cursor.execute("""
                INSERT INTO recovery_recommendations (
                    return_id, recommended_action, reason, rule_triggered, evidence_summary,
                    estimated_recovery_value, estimated_processing_cost, estimated_net_recovery,
                    confidence_score, confidence_pct, alternative_actions, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                return_id,
                rec["recommended_action"],
                rec["reason"],
                rec["rule_triggered"],
                rec["evidence_summary"],
                rec["estimated_recovery_value"],
                rec["estimated_processing_cost"],
                rec["estimated_net_recovery"],
                rec["confidence_score"],
                rec["confidence_pct"],
                rec["alternative_actions"],
                "Generated"
            ))

    # 4. Insert Prioritized Corrective Actions
    corrective_actions = [
        {
            "code": "ACT-101",
            "title": "Investigate AuraWave ANC Audio Driver Batch Failure",
            "related_type": "Supplier",
            "related_id": "SoundCraft Technologies",
            "priority": "Critical",
            "evidence": "5 bench-verified acoustic transducer failures out of 7 inspected returns. Defect rate 71.4% among returns. Concentrated in production batch #41.",
            "estimated_impact": "$1,199.92 recurring warranty exposure across active inventory",
            "assigned_to": "Sarah Chen (QA Lead)",
            "due_date": (base_date + timedelta(days=4)).strftime("%Y-%m-%d"),
            "status": "In Progress",
            "notes": "Sent formal 8D request to SoundCraft QA lead. Supplier acknowledged investigation of left-channel voice coil soldering line."
        },
        {
            "code": "ACT-102",
            "title": "Supplier Packaging Spec Revision for HyperDrive 100W GaN Charger",
            "related_type": "Supplier",
            "related_id": "VoltPeak Power Solutions",
            "priority": "High",
            "evidence": "4 returns reported crushed retail cartons. All chargers verified 100% functional upon bench testing. Carton burst strength under-spec.",
            "estimated_impact": "$340.00 saved in unnecessary repackaging & cosmetic liquidation losses",
            "assigned_to": "Marcus Vance (Packaging Eng)",
            "due_date": (base_date + timedelta(days=7)).strftime("%Y-%m-%d"),
            "status": "Open",
            "notes": "Drafted new packaging standard specifying 275lb double-wall corrugated outer master carton and molded pulp inner tray."
        },
        {
            "code": "ACT-103",
            "title": "Correct Website Product Specifications for SolarCharge PowerBank",
            "related_type": "Product",
            "related_id": "PRD-SOLR-06",
            "priority": "Critical",
            "evidence": "4 returns with 100% citing description mismatch. Supplier carton printed 10000mAh, GadgetBay PDP listing erroneously advertised 20000mAh.",
            "estimated_impact": "Prevents 100% of upcoming returns on remaining 450 units in fulfillment centers",
            "assigned_to": "Elena Rostova (E-Commerce Content)",
            "due_date": (base_date + timedelta(days=1)).strftime("%Y-%m-%d"),
            "status": "Open",
            "notes": "Emergency ticket created with CMS team to adjust PDP title and bullet points to 10,000mAh with price adjustment."
        },
        {
            "code": "ACT-104",
            "title": "Develop iOS 16+ Bluetooth Pairing Quick-Start Guide for PulseFit Pro",
            "related_type": "Product",
            "related_id": "PRD-PULS-03",
            "priority": "Medium",
            "evidence": "2 returns citing incompatibility. Inspection proved units are fully operational; customers faced iOS Bluetooth privacy permission prompt confusion.",
            "estimated_impact": "Reduces customer setup friction returns by ~35%",
            "assigned_to": "David Kim (Product Support)",
            "due_date": (base_date - timedelta(days=2)).strftime("%Y-%m-%d"),
            "status": "Resolved",
            "notes": "Resolved: Interactive pairing QR sticker added to warehouse outbound dispatch. Updated knowledge-base article published."
        },
        {
            "code": "ACT-105",
            "title": "Conduct Inbound Sample Inspection on KeyForge Keyboard Batch #88",
            "related_type": "Supplier",
            "related_id": "KeyForge Labs",
            "priority": "Medium",
            "evidence": "Spacebar stabilizer dislodgement noted on return RET-1039. Checking whether inbound warehouse shipment shares the same switch plate batch.",
            "estimated_impact": "Early containment of potential 150-unit keyboard inventory issue",
            "assigned_to": "Alex Chen (Inbound QA)",
            "due_date": (base_date + timedelta(days=10)).strftime("%Y-%m-%d"),
            "status": "Open",
            "notes": "Sample AQL level II inspection scheduled for next container arrival."
        }
    ]

    for act in corrective_actions:
        cursor.execute("""
            INSERT INTO corrective_actions (action_code, title, related_type, related_id, priority, evidence, estimated_impact, assigned_to, due_date, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            act["code"], act["title"], act["related_type"], act["related_id"], act["priority"],
            act["evidence"], act["estimated_impact"], act["assigned_to"], act["due_date"], act["status"], act["notes"]
        ))

    conn.commit()
    conn.close()
    print("Database successfully seeded with 60 returns, 12 products, 6 suppliers, and 5 corrective actions!")


if __name__ == "__main__":
    seed_database()
