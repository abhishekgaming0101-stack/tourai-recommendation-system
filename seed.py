from pymongo import MongoClient
from datetime import datetime
from passlib.context import CryptContext

client = MongoClient("mongodb://localhost:27017")
db = client["touristdb"]

PLACES = [
    {
        "name": "Taj Mahal",
        "state": "Uttar Pradesh", "city": "Agra", "category": "heritage",
        "description": "Iconic 17th century marble mausoleum built by Mughal emperor Shah Jahan for his wife Mumtaz Mahal. UNESCO World Heritage Site and one of the Seven Wonders of the World.",
        "tags": ["UNESCO", "mughal", "monument", "romantic", "architecture"],
        "budget": "medium", "best_season": "winter", "lat": 27.1751, "lng": 78.0421, "avg_rating": 4.8,
        "image": "/places/taj-mahal.jpg",
        "images": ["/places/taj-mahal.jpg"]
    },
    {
        "name": "Goa Beaches",
        "state": "Goa", "city": "Panaji", "category": "beach",
        "description": "Pristine beaches with golden sand, clear waters, vibrant nightlife, Portuguese heritage architecture and fresh seafood. Perfect for relaxation and water sports.",
        "tags": ["beach", "nightlife", "water-sports", "seafood", "party"],
        "budget": "medium", "best_season": "winter", "lat": 15.2993, "lng": 74.1240, "avg_rating": 4.5,
        "image": "/places/goa-beaches.jpg",
        "images": ["/places/goa-beaches.jpg"]
    },
    {
        "name": "Kerala Backwaters",
        "state": "Kerala", "city": "Alleppey", "category": "nature",
        "description": "Network of lagoons, lakes, and canals parallel to the Arabian Sea coast. Houseboat cruises through coconut palm-lined waterways offer a unique experience.",
        "tags": ["houseboat", "backwaters", "nature", "serene", "coconut", "ayurveda"],
        "budget": "high", "best_season": "winter", "lat": 9.4981, "lng": 76.3388, "avg_rating": 4.7,
        "image": "/places/kerala-backwaters.jpg",
        "images": ["/places/kerala-backwaters.jpg"]
    },
    {
        "name": "Jaipur Pink City",
        "state": "Rajasthan", "city": "Jaipur", "category": "heritage",
        "description": "The Pink City of India with magnificent forts, palaces, and vibrant bazaars. Hawa Mahal, Amber Fort, and City Palace are must-visit landmarks.",
        "tags": ["fort", "palace", "rajput", "pink-city", "bazaar", "architecture"],
        "budget": "medium", "best_season": "winter", "lat": 26.9124, "lng": 75.7873, "avg_rating": 4.6,
        "image": "/places/jaipur-pink-city.jpg",
        "images": ["/places/jaipur-pink-city.jpg"]
    },
    {
        "name": "Manali Hill Station",
        "state": "Himachal Pradesh", "city": "Manali", "category": "hill",
        "description": "Popular hill station in Kullu valley surrounded by snow-capped Himalayan peaks. Adventure sports, Rohtang Pass, and Hadimba Temple attract millions of tourists.",
        "tags": ["mountains", "snow", "adventure", "trekking", "skiing", "himalaya"],
        "budget": "medium", "best_season": "summer", "lat": 32.2396, "lng": 77.1887, "avg_rating": 4.6,
        "image": "/places/manali-hill-station.jpg",
        "images": ["/places/manali-hill-station.jpg"]
    },
    {
        "name": "Varanasi Ghats",
        "state": "Uttar Pradesh", "city": "Varanasi", "category": "religious",
        "description": "One of the oldest living cities in the world. Sacred Ganges river, ancient temples, spiritual ceremonies, and the famous Ganga Aarti make it deeply mystical.",
        "tags": ["spiritual", "temples", "ganga", "aarti", "holy", "ancient"],
        "budget": "low", "best_season": "winter", "lat": 25.3176, "lng": 82.9739, "avg_rating": 4.5,
        "image": "/places/varanasi-ghats.jpg",
        "images": ["/places/varanasi-ghats.jpg"]
    },
    {
        "name": "Ranthambore National Park",
        "state": "Rajasthan", "city": "Sawai Madhopur", "category": "wildlife",
        "description": "Famous tiger reserve and national park in Rajasthan. One of the best places in India to spot Bengal tigers in their natural habitat alongside leopards and crocodiles.",
        "tags": ["tiger", "wildlife", "safari", "jungle", "nature", "photography"],
        "budget": "high", "best_season": "winter", "lat": 26.0173, "lng": 76.5026, "avg_rating": 4.4,
        "image": "/places/ranthambore.jpg",
        "images": ["/places/ranthambore.jpg"]
    },
    {
        "name": "Darjeeling Tea Gardens",
        "state": "West Bengal", "city": "Darjeeling", "category": "hill",
        "description": "Queen of Hill Stations with world-famous tea gardens, stunning views of Kanchenjunga, and the historic Toy Train. Sunrise at Tiger Hill is unforgettable.",
        "tags": ["tea", "mountains", "toy-train", "sunrise", "himalaya", "colonial"],
        "budget": "medium", "best_season": "spring", "lat": 27.0360, "lng": 88.2627, "avg_rating": 4.5,
        "image": "/places/darjeeling.jpg",
        "images": ["/places/darjeeling.jpg"]
    },
    {
        "name": "Rishikesh Adventure Hub",
        "state": "Uttarakhand", "city": "Rishikesh", "category": "adventure",
        "description": "Yoga capital of the world and adventure sports destination. White water rafting on Ganga, bungee jumping, camping, and spiritual ashrams attract diverse travelers.",
        "tags": ["yoga", "rafting", "adventure", "spiritual", "camping", "bungee"],
        "budget": "low", "best_season": "summer", "lat": 30.0869, "lng": 78.2676, "avg_rating": 4.4,
        "image": "/places/rishikesh.jpg",
        "images": ["/places/rishikesh.jpg"]
    },
    {
        "name": "Munnar Tea Valleys",
        "state": "Kerala", "city": "Munnar", "category": "hill",
        "description": "Beautiful hill station in the Western Ghats covered with lush tea plantations, spice gardens, and wildlife sanctuaries. Misty valleys and rare Neelakurinji flowers.",
        "tags": ["tea", "hills", "nature", "western-ghats", "spice", "peaceful"],
        "budget": "medium", "best_season": "winter", "lat": 10.0889, "lng": 77.0595, "avg_rating": 4.6,
        "image": "/places/munnar.jpg",
        "images": ["/places/munnar.jpg"]
    },
    {
        "name": "Hampi Ruins",
        "state": "Karnataka", "city": "Hampi", "category": "heritage",
        "description": "UNESCO World Heritage Site and former capital of the Vijayanagara Empire. Stunning boulder-strewn landscape with ancient temples, market ruins, and royal enclosures.",
        "tags": ["UNESCO", "ruins", "history", "vijayanagara", "boulders", "temples"],
        "budget": "low", "best_season": "winter", "lat": 15.3350, "lng": 76.4600, "avg_rating": 4.7,
        "image": "/places/hampi.jpg",
        "images": ["/places/hampi.jpg"]
    },
    {
        "name": "Ladakh High Desert",
        "state": "Ladakh", "city": "Leh", "category": "adventure",
        "description": "High altitude desert with breathtaking landscapes, ancient monasteries, Pangong Lake, and Nubra Valley. Ultimate destination for bikers and adventure enthusiasts.",
        "tags": ["desert", "monastery", "pangong", "biking", "altitude", "Buddhist", "adventure"],
        "budget": "high", "best_season": "summer", "lat": 34.1526, "lng": 77.5771, "avg_rating": 4.8,
        "image": "/places/ladakh.jpg",
        "images": ["/places/ladakh.jpg"]
    },
    {
        "name": "Ajanta Ellora Caves",
        "state": "Maharashtra", "city": "Aurangabad", "category": "heritage",
        "description": "UNESCO World Heritage rock-cut caves featuring extraordinary Buddhist, Hindu and Jain paintings and sculptures dating from 2nd century BCE to 650 CE.",
        "tags": ["UNESCO", "caves", "Buddhist", "paintings", "ancient", "rock-cut"],
        "budget": "low", "best_season": "winter", "lat": 20.5519, "lng": 75.7033, "avg_rating": 4.6,
        "image": "/places/ajanta-ellora.jpg",
        "images": ["/places/ajanta-ellora.jpg"]
    },
    {
        "name": "Andaman Islands",
        "state": "Andaman & Nicobar", "city": "Port Blair", "category": "beach",
        "description": "Pristine tropical islands with crystal-clear turquoise waters, coral reefs, and dense rainforests. Scuba diving, snorkeling at Radhanagar Beach and Havelock Island.",
        "tags": ["beach", "island", "scuba", "coral", "snorkeling", "tropical", "underwater"],
        "budget": "high", "best_season": "winter", "lat": 11.7401, "lng": 92.6586, "avg_rating": 4.7,
        "image": "/places/andaman.jpg",
        "images": ["/places/andaman.jpg"]
    },
    {
        "name": "Jim Corbett National Park",
        "state": "Uttarakhand", "city": "Ramnagar", "category": "wildlife",
        "description": "India's oldest national park and Project Tiger reserve. Dense forests, rivers and grasslands are home to Bengal tigers, leopards, elephants and diverse bird species.",
        "tags": ["tiger", "wildlife", "jungle", "safari", "elephant", "birds", "nature"],
        "budget": "high", "best_season": "winter", "lat": 29.5300, "lng": 78.7747, "avg_rating": 4.5,
        "image": "/places/jim-corbett.jpg",
        "images": ["/places/jim-corbett.jpg"]
    },
    {
        "name": "Mysore Palace",
        "state": "Karnataka", "city": "Mysore", "category": "heritage",
        "description": "Magnificent Indo-Saracenic palace that was the royal residence of the Wadiyar dynasty. Illuminated with 97,000 bulbs on weekends. Dasara festival here is spectacular.",
        "tags": ["palace", "royal", "architecture", "festival", "lights", "heritage"],
        "budget": "low", "best_season": "winter", "lat": 12.3052, "lng": 76.6552, "avg_rating": 4.6,
        "image": "/places/mysore-palace.jpg",
        "images": ["/places/mysore-palace.jpg"]
    },
    {
        "name": "Shimla Queen of Hills",
        "state": "Himachal Pradesh", "city": "Shimla", "category": "hill",
        "description": "Former summer capital of British India with Victorian architecture, Mall Road, and panoramic Himalayan views. Nearby Kufri offers skiing and apple orchards.",
        "tags": ["hills", "colonial", "mall-road", "snow", "apple", "trekking"],
        "budget": "medium", "best_season": "summer", "lat": 31.1048, "lng": 77.1734, "avg_rating": 4.3,
        "image": "/places/shimla.jpg",
        "images": ["/places/shimla.jpg"]
    },
    {
        "name": "Coorg Coffee Estates",
        "state": "Karnataka", "city": "Madikeri", "category": "nature",
        "description": "Scotland of India covered with coffee and spice plantations, waterfalls, and mist-covered hills. Trekking, wildlife, and the Kodava culture make it unique.",
        "tags": ["coffee", "nature", "waterfall", "trekking", "mist", "spice", "peaceful"],
        "budget": "medium", "best_season": "winter", "lat": 12.4244, "lng": 75.7382, "avg_rating": 4.5,
        "image": "/places/coorg.jpg",
        "images": ["/places/coorg.jpg"]
    },
    {
        "name": "Sundarbans Mangroves",
        "state": "West Bengal", "city": "South 24 Parganas", "category": "wildlife",
        "description": "Largest mangrove forest in the world and UNESCO site. Home to the Royal Bengal Tiger, Irrawaddy dolphins, estuarine crocodiles and diverse migratory birds.",
        "tags": ["mangrove", "tiger", "UNESCO", "delta", "wildlife", "boat", "unique"],
        "budget": "medium", "best_season": "winter", "lat": 21.9497, "lng": 88.9468, "avg_rating": 4.3,
        "image": "/places/sundarbans.jpg",
        "images": ["/places/sundarbans.jpg"]
    },
    {
        "name": "Pushkar Lake & Fair",
        "state": "Rajasthan", "city": "Pushkar", "category": "religious",
        "description": "Sacred town with the only Brahma temple in India. Famous Pushkar Camel Fair draws thousands. Sacred lake surrounded by 52 ghats and 400 temples.",
        "tags": ["camel", "fair", "brahma", "temple", "ghats", "spiritual", "desert"],
        "budget": "low", "best_season": "winter", "lat": 26.4899, "lng": 74.5511, "avg_rating": 4.4,
        "image": "/places/pushkar.jpg",
        "images": ["/places/pushkar.jpg"]
    },
    {
        "name": "Khajuraho Temples",
        "state": "Madhya Pradesh", "city": "Khajuraho", "category": "heritage",
        "description": "UNESCO World Heritage temples famous for their Nagara-style architectural symbolism and erotic sculptures. Built by Chandela dynasty between 950-1050 CE.",
        "tags": ["UNESCO", "temples", "sculpture", "medieval", "art", "chandela"],
        "budget": "low", "best_season": "winter", "lat": 24.8318, "lng": 79.9199, "avg_rating": 4.5,
        "image": "/places/khajuraho.jpg",
        "images": ["/places/khajuraho.jpg"]
    },
    {
        "name": "Ooty Nilgiris",
        "state": "Tamil Nadu", "city": "Ooty", "category": "hill",
        "description": "Queen of hill stations in the Nilgiri Hills with lush gardens, tea estates, and the famous Nilgiri Mountain Railway. Boating on Ooty Lake is popular.",
        "tags": ["hills", "tea", "garden", "toy-train", "lake", "peaceful", "nature"],
        "budget": "low", "best_season": "summer", "lat": 11.4102, "lng": 76.6950, "avg_rating": 4.2,
        "image": "/places/ooty.jpg",
        "images": ["/places/ooty.jpg"]
    },
    {
        "name": "Amritsar Golden Temple",
        "state": "Punjab", "city": "Amritsar", "category": "religious",
        "description": "Harmandir Sahib, the holiest shrine in Sikhism. The gilded sanctuary surrounded by the sacred Amrit Sarovar pool. Community langar serves 100,000 people daily.",
        "tags": ["sikh", "temple", "golden", "spiritual", "peaceful", "langar", "holy"],
        "budget": "low", "best_season": "winter", "lat": 31.6200, "lng": 74.8765, "avg_rating": 4.9,
        "image": "/places/golden-temple.jpg",
        "images": ["/places/golden-temple.jpg"]
    },
    {
        "name": "Kaziranga National Park",
        "state": "Assam", "city": "Kaziranga", "category": "wildlife",
        "description": "UNESCO World Heritage Site and home to two-thirds of the world's one-horned rhinoceroses. Also has tigers, elephants, and wild water buffalo.",
        "tags": ["rhino", "UNESCO", "wildlife", "safari", "elephant", "tiger", "grassland"],
        "budget": "medium", "best_season": "winter", "lat": 26.5775, "lng": 93.1712, "avg_rating": 4.6,
        "image": "/places/kaziranga.jpg",
        "images": ["/places/kaziranga.jpg"]
    },
    {
        "name": "Nainital Lake Town",
        "state": "Uttarakhand", "city": "Nainital", "category": "hill",
        "description": "Beautiful lake district town in the Kumaon Himalayas. Naini Lake boating, Mall Road, Snow View Point, and trekking trails make it a favourite hill escape.",
        "tags": ["lake", "hills", "boating", "himalaya", "peaceful", "nature", "family"],
        "budget": "medium", "best_season": "summer", "lat": 29.3803, "lng": 79.4636, "avg_rating": 4.3,
        "image": "/places/nainital.jpg",
        "images": ["/places/nainital.jpg"]
    },
    {
        "name": "Udaipur City of Lakes",
        "state": "Rajasthan", "city": "Udaipur", "category": "heritage",
        "description": "City of Lakes with magnificent palaces, temples, and serene lakes. Lake Palace floating on Pichola Lake, City Palace, and Jagdish Temple are iconic landmarks.",
        "tags": ["palace", "lake", "romantic", "rajput", "heritage", "architecture", "luxury"],
        "budget": "high", "best_season": "winter", "lat": 24.5854, "lng": 73.7125, "avg_rating": 4.7,
        "image": "/places/udaipur.jpg",
        "images": ["/places/udaipur.jpg"]
    },
    {
        "name": "Valley of Flowers",
        "state": "Uttarakhand", "city": "Chamoli", "category": "nature",
        "description": "UNESCO World Heritage Site and national park in Garhwal Himalayas. Meadows of endemic alpine flowers, glaciers, and the Hemkund Sahib Gurudwara.",
        "tags": ["flowers", "UNESCO", "trekking", "himalaya", "nature", "alpine", "sikh"],
        "budget": "medium", "best_season": "summer", "lat": 30.7283, "lng": 79.6050, "avg_rating": 4.7,
        "image": "/places/valley-of-flowers.jpg",
        "images": ["/places/valley-of-flowers.jpg"]
    },
    {
        "name": "Mahabalipuram Shore Temple",
        "state": "Tamil Nadu", "city": "Mahabalipuram", "category": "heritage",
        "description": "UNESCO World Heritage Site with 7th century stone carvings and the famous Shore Temple on the Bay of Bengal. Pallava dynasty rock-cut monuments.",
        "tags": ["UNESCO", "temple", "pallava", "ancient", "beach", "sculpture", "shore"],
        "budget": "low", "best_season": "winter", "lat": 12.6269, "lng": 80.1927, "avg_rating": 4.4,
        "image": "/places/mahabalipuram.jpg",
        "images": ["/places/mahabalipuram.jpg"]
    },
    {
        "name": "Spiti Valley Cold Desert",
        "state": "Himachal Pradesh", "city": "Kaza", "category": "adventure",
        "description": "Remote cold desert mountain valley in the Himalayas. Ancient Buddhist monasteries, traditional villages, stunning landscapes and the Pin Valley National Park.",
        "tags": ["desert", "monastery", "buddhist", "remote", "adventure", "himalaya", "photography"],
        "budget": "medium", "best_season": "summer", "lat": 32.2317, "lng": 78.0680, "avg_rating": 4.6,
        "image": "/places/spiti-valley.jpg",
        "images": ["/places/spiti-valley.jpg"]
    },
    {
        "name": "Kodaikanal Princess of Hills",
        "state": "Tamil Nadu", "city": "Kodaikanal", "category": "hill",
        "description": "Princess of Hill Stations in Tamil Nadu with star-shaped Kodai Lake, Bear Shola Falls, and Pillar Rocks. Famous for chocolates and Kurinji flowers.",
        "tags": ["lake", "hills", "waterfall", "chocolate", "peaceful", "nature", "romantic"],
        "budget": "low", "best_season": "summer", "lat": 10.2381, "lng": 77.4892, "avg_rating": 4.3,
        "image": "/places/kodaikanal.jpg",
        "images": ["/places/kodaikanal.jpg"]
    },
]

def seed():
    places_col = db["places"]
    places_col.delete_many({})
    inserted = 0
    for p in PLACES:
        p["created_at"] = datetime.utcnow()
        p["rating_count"] = 0
        places_col.insert_one(p)
        inserted += 1
    print("Seeded " + str(inserted) + " places into MongoDB")

    pwd = CryptContext(schemes=["bcrypt"])
    users_col = db["users"]
    if not users_col.find_one({"email": "admin@tourist.com"}):
        users_col.insert_one({
            "name": "Admin",
            "email": "admin@tourist.com",
            "password": pwd.hash("admin123"),
            "role": "admin",
            "preferred_categories": ["heritage", "beach", "wildlife"],
            "budget": "high",
            "travel_type": "solo",
            "wishlist": [],
            "liked_places": [],
            "created_at": datetime.utcnow()
        })
        print("Admin user created: admin@tourist.com / admin123")

if __name__ == "__main__":
    seed()