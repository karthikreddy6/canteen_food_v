-- Auto-generated SQL insert script for Indian Dishes
CREATE TABLE IF NOT EXISTS indian_dishes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item VARCHAR(255) NOT NULL UNIQUE,
    region VARCHAR(100),
    description TEXT,
    vegetarian_or_non_vegetarian VARCHAR(100),
    dish_type VARCHAR(100),
    image_filename VARCHAR(255),
    image_url TEXT,
    source_page TEXT,
    local_image_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Machher Jhol', 'North-East India', 'Fish with potol, tomato, chillies, ginger and garlic from Assam', 'Non-Vegetarian', '', 'Machher Jhol.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Alu_ar_dhonepata_diye_Boyal_machher_jhol.jpg/120px-Alu_ar_dhonepata_diye_Boyal_machher_jhol.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Machher%20Jhol.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Chak-Hao Kheer', 'North-East India', 'Purple rice porridge from Manipur', 'Vegetarian', '', 'Chak-Hao Kheer.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/Chahao_kheer.jpg/120px-Chahao_kheer.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Chak-Hao%20Kheer.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Achari baingan', 'North India', 'Brinjal cooked with pickle spices in gravy', 'Vegetarian', '', 'Achari baingan.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Baigan_Ka_Salan.JPG/120px-Baigan_Ka_Salan.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Achari%20baingan.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Aloo gobi', 'North India', 'Cauliflower with potatoes sautéed with garam masala, turmeric, sometimes kalonji and curry leaves.', 'Vegetarian', '', 'Aloo gobi.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Aloo_gobi.jpg/120px-Aloo_gobi.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Aloo%20gobi.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Aloo tikki', 'North India', 'Patties of potato mixed with some vegetables fried', 'Vegetarian', '', 'Aloo tikki.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Aloo_Tikki_served_with_chutneys.jpg/120px-Aloo_Tikki_served_with_chutneys.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Aloo%20tikki.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Aloo matar', 'North India', 'Potatoes and peas in curry', 'Vegetarian', '', 'Aloo matar.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Aloo_Mattar.jpg/120px-Aloo_Mattar.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Aloo%20matar.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Aloo kulcha', 'North India', 'Mildly leavened flatbread stuffed with potatoes', 'Vegetarian', '', 'Aloo kulcha.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Amritsari_Kulcha.jpg/120px-Amritsari_Kulcha.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Aloo%20kulcha.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Aloo methi', 'North India', 'Sautéed potatoes (aloo) and chopped fenugreek leaves (methi) with chopped onions, garlic, and a blend of spices such as cumin, coriander, turmeric, and chili powder.', 'Vegetarian', '', 'Aloo methi.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Aloo_Methi_%28Aaloo_Methi%29.JPG/120px-Aloo_Methi_%28Aaloo_Methi%29.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Aloo%20methi.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Aloo shimla mirch', 'North India', 'Green capsicum with potatoes sautéed with cumin seeds, onions, tomatoes, ginger-garlic paste, turmeric, red chilli powder and garam masala', 'Vegetarian', '', 'Aloo shimla mirch.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Spicy_alloo_with_tadka_mirchi.jpg/120px-Spicy_alloo_with_tadka_mirchi.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Aloo%20shimla%20mirch.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Baati', 'North India', 'Hard, unleavened bread cooked in most of areas of Rajasthan, and in some parts of Madhya Pradesh, and Gujarat states of India.', 'Vegetarian', '', 'Baati.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Baati.jpg/120px-Baati.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Baati.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Bhatura', 'North India', 'A fluffy deep-fried leavened bread originating from the Indian subcontinent.', 'Vegetarian', '', 'Bhatura.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Bhatura.jpg/120px-Bhatura.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Bhatura.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Bhindi masala', 'North India', 'Okra sautéed with onions and tomatoes', 'Vegetarian', '', 'Bhindi masala.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Fresh_Bhindi_Masala.jpg/120px-Fresh_Bhindi_Masala.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Bhindi%20masala.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Biryani', 'North India', 'Mixed rice dish, optional spices, optional vegetables, meats or seafood. Can be served with plain yogurt.', 'Non-Vegetarian', '', 'Biryani.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/India_food.jpg/120px-India_food.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Biryani.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Butter chicken, murgh mahal', 'North India', 'Chicken in a mildly spiced tomato sauce.', 'Non-Vegetarian', '', 'Butter chicken, murgh mahal.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Chicken_makhani.jpg/120px-Chicken_makhani.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Butter%20chicken%2C%20murgh%20mahal.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Chaat', 'North India', 'Usually containing potato patty fried in oil, topped with sweet yogurt, and other sauces and spices', 'Vegetarian, Street food.', '', 'Chaat.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Delhi_Chaat_with_saunth_chutney.jpg/120px-Delhi_Chaat_with_saunth_chutney.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Chaat.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Chana masala', 'North India', 'Chickpeas of the Chana type in tomato based sauce.', 'Vegetarian', '', 'Chana masala.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Choleindia.jpg/120px-Choleindia.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Chana%20masala.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Chapati', 'North India', 'Unleavened flatbread originating from the Indian subcontinent and staple in India, Nepal, Bangladesh, Pakistan, Sri Lanka, East Africa and the Caribbean.', 'Vegetarian', '', 'Chapati.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Chapatiroll.jpg/120px-Chapatiroll.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Chapati.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Chicken rezala', 'North India', 'Bhopali style chicken cooked in a rich gravy with mint', 'Non-Vegetarian', '', 'Chicken rezala.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Chicken_Rezala_-_Kolkata_2011-08-02_4546.JPG/120px-Chicken_Rezala_-_Kolkata_2011-08-02_4546.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Chicken%20rezala.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Chicken Tikka', 'North India', 'Chicken with spices served on a skewer', 'Non-Vegetarian', '', 'Chicken Tikka.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Chicken_tikka_by_fatima.jpg/120px-Chicken_tikka_by_fatima.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Chicken%20Tikka.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Chicken tikka masala', 'North India', 'Chicken marinated in a Yogurt tomato sauce. It is known to have a creamy texture.', 'Non-Vegetarian', '', 'Chicken tikka masala.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Chicken_tikka_masala.jpg/120px-Chicken_tikka_masala.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Chicken%20tikka%20masala.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Chole bhature', 'North India', 'Main course with chickpeas, assorted spices, wheat flour and bhatura yeast.', 'Vegetarian', '', 'Chole bhature.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Chana_masala.jpg/120px-Chana_masala.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Chole%20bhature.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Daal baati churma', 'North India', 'A Rajasthani specialty', 'Vegetarian', '', 'Daal baati churma.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Rajasthani_Dal_Bati_Churma_-_Gurugram_-_Haryana_-_03.jpg/120px-Rajasthani_Dal_Bati_Churma_-_Gurugram_-_Haryana_-_03.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Daal%20baati%20churma.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Dal makhani (kali dal)', 'North India', 'Lentils in a creamy and aromatic sauce made of butter, tomato sauce, and a blend of spices', 'Vegetarian', '', 'Dal makhani (kali dal).jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Dal_Makhani.jpg/120px-Dal_Makhani.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Dal%20makhani%20%28kali%20dal%29.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Dalpuri', 'North India', 'Stuffed dal in parathas', 'Vegetarian', '', 'Dalpuri.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Dal_Puri.JPG/120px-Dal_Puri.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Dalpuri.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Dal tadka', 'North India', 'Typical north Indian tadka', 'Vegetarian', '', 'Dal tadka.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Dal_Fry_Tadka%2C_Cumin_Rice%2C_Roasted_Papad_on_the_side.jpg/120px-Dal_Fry_Tadka%2C_Cumin_Rice%2C_Roasted_Papad_on_the_side.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Dal%20tadka.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Dum aloo', 'North India', 'Potatoes cooked in curry', 'Vegetarian', '', 'Dum aloo.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Kashmiri_Dum_aloo.jpeg/120px-Kashmiri_Dum_aloo.jpeg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Dum%20aloo.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Poha', 'North India', 'Specialty from Madhya Pradesh. Common snack in central part of India. Flattened rice, potato, turmeric.', 'Vegetarian', '', 'Poha.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Poha%2C_a_snack_made_of_flattened_rice.jpg/120px-Poha%2C_a_snack_made_of_flattened_rice.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Poha.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Gajar Pak', 'North India', 'Sweet dish made using carrot, milk, ghee, dry fruits.', 'Vegetarian', '', 'Gajar Pak.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Gajjar_ka_halwa_%28carrot_halwa%29.JPG/120px-Gajjar_ka_halwa_%28carrot_halwa%29.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Gajar%20Pak.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Gatte ki Sabzi', 'North India', 'Gatte (made up of besan) are added to spice gravy made of curd.', '', '', 'Gatte ki Sabzi.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Besan_Gatta_curry03.jpg/120px-Besan_Gatta_curry03.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Gatte%20ki%20Sabzi.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Gobhi matar', 'North India', 'Cauliflower in a tomato sauce', 'Vegetarian', '', 'Gobhi matar.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Aloo_gobi_matar_ki_sabji.jpg/120px-Aloo_gobi_matar_ki_sabji.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Gobhi%20matar.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Imarti', 'North India', 'spherically meshed sweet dish from North India made up of batter from moong dal dipped in sugary syrup', 'Vegetarian', '', 'Imarti.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/JalebiIndia.jpg/120px-JalebiIndia.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Imarti.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Jalebi', 'North India', 'A North Indian twisted noodle like sweet dish dipped in sugary syrup', 'Vegetarian', '', 'Jalebi.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Awadhi_jalebi.jpg/120px-Awadhi_jalebi.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Jalebi.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Jalfrezi', 'North India', 'Meat and spices fried in a pan. Can be vegetarian as well.', 'Vegetarian', '', 'Jalfrezi.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Vegetable_jalfrezi_-_2902442562.jpg/120px-Vegetable_jalfrezi_-_2902442562.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Jalfrezi.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Kachori', 'North India', 'Rajasthani / Marwari special', 'Vegetarian', '', 'Kachori.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Cachuri2_flipped.jpg/120px-Cachuri2_flipped.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Kachori.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Kadai paneer', 'North India', 'Paneer and green peppers in tomato gravy', 'Vegetarian', '', 'Kadai paneer.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Kadai_Paneer_Recipe.JPG/120px-Kadai_Paneer_Recipe.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Kadai%20paneer.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Katha meetha petha / kaddu halwa', 'North India', 'Pumpkin cooked in spices', 'Vegetarian', '', 'Katha meetha petha - kaddu halwa.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Halwa_Kashi_Sweets_of_India.jpg/120px-Halwa_Kashi_Sweets_of_India.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Katha%20meetha%20petha%20-%20kaddu%20halwa.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Kheer', 'North India', 'Rice cooked with milk and dry fruits', 'Vegetarian', '', 'Kheer.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Kheer.jpg/120px-Kheer.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Kheer.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Khichdi', 'North India', 'Rice cooked with daal and veggies and sauteed', 'Vegetarian', '', 'Khichdi.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Khichuri-edit.jpg/120px-Khichuri-edit.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Khichdi.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Kadhi and Khichdi', 'North India', 'Khichdi mixed with kadhi, found mostly in Gujarat. Also referred to as khichdi and kadhi, khichdi-kadhi, and kadhi-khichdi.', 'Vegetarian', '', 'Kadhi and Khichdi.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Kadhi_and_Khichdi_of_Bardoli%2C_gujarat.jpg/120px-Kadhi_and_Khichdi_of_Bardoli%2C_gujarat.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Kadhi%20and%20Khichdi.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Khoya paneer', 'North India', 'cube of paneer cheese in a gravy made of thickened milk (khoya), onion, garlic, ginger, tomato and spices', 'Vegetarian', '', 'Khoya paneer.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Kadai_Paneer.JPG/120px-Kadai_Paneer.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Khoya%20paneer.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Kofta', 'North India', 'Gram flour balls fried with vegetables. Gram flour, veggies, rolled into balls with gram flour and fried in oil and then cooked with curry.', 'Vegetarian', '', 'Kofta.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Paneer_Kofta_Curry_-_Kolkata_2011-09-20_5426.JPG/120px-Paneer_Kofta_Curry_-_Kolkata_2011-09-20_5426.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Kofta.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Kulfi falooda', 'North India', 'dessert to ward off sweltering heat of summers', 'Vegetarian', '', 'Kulfi falooda.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Matkakulfi.jpg/120px-Matkakulfi.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Kulfi%20falooda.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Laapsi', 'North India', 'Dessert made up of broken wheat', 'Vegetarian', '', 'Laapsi.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Moong_dal_ka_halwa.jpg/120px-Moong_dal_ka_halwa.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Laapsi.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Lauki ke kofte', 'North India', 'a way to serve bottle gourd', 'Vegetarian', '', 'Lauki ke kofte.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Lauki_ke_Kofte.jpg/120px-Lauki_ke_Kofte.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Lauki%20ke%20kofte.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Litti chokha', 'North India', 'A baked salted wheat flour cake filled with sattu (baked chickpea flour) and some special spices', 'Vegetarian', '', 'Litti chokha.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Litti_Chokha.jpg/120px-Litti_Chokha.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Litti%20chokha.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Lobiya', 'North India', 'Black eyes peas, onions and tomatoes in a curry sauce', 'Vegetarian', '', 'Lobiya.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Lobia_Curry.JPG/120px-Lobia_Curry.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Lobiya.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Makhaan ka kheer', 'North India', 'Sweet, made up with makhana, milk, sugar, cashew and other savor. Popular in Mithilanchal region of Bihar', 'Vegetarian', '', 'Makhaan ka kheer.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Makhana_kheer.jpg/120px-Makhana_kheer.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Makhaan%20ka%20kheer.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Makki ki roti, sarson ka saag', 'North India', 'Creamed sarson mustard leaves, with heavily buttered roti made from corn flour. North Indian winter favorite.', 'Vegetarian', '', 'Makki ki roti, sarson ka saag.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Saagroti.jpg/120px-Saagroti.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Makki%20ki%20roti%2C%20sarson%20ka%20saag.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Matar paneer', 'North India', 'green peas and cube of paneer cheese in a spiced tomato-based sauce', 'Vegetarian', '', 'Matar paneer.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Matar_Paneer_2.jpg/120px-Matar_Paneer_2.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Matar%20paneer.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Mathura peda', 'North India', 'a sort of a confection', 'Vegetarian', '', 'Mathura peda.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Mathura_Peda.jpg/120px-Mathura_Peda.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Mathura%20peda.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Mirchi bada', 'North India', 'Green Chili stuffed with mashed potato, coated with besan batter and fried, it is native to Jodhpur.', 'Vegetarian', '', 'Mirchi bada.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Mirchi_Bada_from_Jodhpur_1.jpg/120px-Mirchi_Bada_from_Jodhpur_1.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Mirchi%20bada.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Missi roti', 'North India', 'Whole wheat & gram flour dough ground masalas, pan fried', 'Vegetarian', '', 'Missi roti.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Missi_Roti.jpg/120px-Missi_Roti.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Missi%20roti.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Moong dal ki Lapsi', 'North India', 'a dish made with yellow lentils, milk, sugar, and nuts', 'Vegetarian Dessert', '', 'Moong dal ki Lapsi.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Moong_dal_ka_halwa.jpg/120px-Moong_dal_ka_halwa.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Moong%20dal%20ki%20Lapsi.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Murgh musallam', 'North India', '', 'Non-Vegetarian', '', 'Murgh musallam.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Murgh_Musallam.JPG/120px-Murgh_Musallam.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Murgh%20musallam.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Naan', 'North India', 'Tandoor-baked soft flatbread made with refined wheat flour.', 'Vegetarian', '', 'Naan.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Annapurna_Naan.jpg/120px-Annapurna_Naan.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Naan.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Naan Khatai', 'North India', 'Shortbread biscuits', 'Vegetarian', '', 'Naan Khatai.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Nankhatai.jpg/120px-Nankhatai.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Naan%20Khatai.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Navrattan korma', 'North India', 'Vegetables, Nuts, Paneer cheese in a tomato cream sauce', 'Vegetarian', '', 'Navrattan korma.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Navratan_Korma_%28Mughal_Kitchen%29.JPG/120px-Navratan_Korma_%28Mughal_Kitchen%29.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Navrattan%20korma.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Pakhala', 'North India', 'Cooked rice with water', 'Vegetarian', '', 'Pakhala.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Pakhala_01.jpg/120px-Pakhala_01.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Pakhala.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Palak paneer', 'North India', 'fresh spinach leaves (palak) cooked with cubes of paneer cheese in a rich and creamy tomato-based sauce', 'Vegetarian', '', 'Palak paneer.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Palakpaneer.jpg/120px-Palakpaneer.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Palak%20paneer.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Paneer butter masala, paneer makhani', 'North India', 'curry made with soft cubes of paneer cheese in a creamy and aromatic sauce made of butter, tomato sauce, and a blend of spices', 'Vegetarian', '', 'Paneer butter masala, paneer makhani.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Popular_Indian_dish%2C_Paneer_Butter_Masala.jpg/120px-Popular_Indian_dish%2C_Paneer_Butter_Masala.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Paneer%20butter%20masala%2C%20paneer%20makhani.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Paneer tikka masala', 'North India', 'vegetarian alternative to chicken tikka masala, with paneer instead of chicken', 'Vegetarian', '', 'Paneer tikka masala.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Paneer_Tikka_masala.JPG/120px-Paneer_Tikka_masala.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Paneer%20tikka%20masala.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Pani puri', 'North India', 'a typical Indian tadka', 'Vegetarian', '', 'Pani puri.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Indian_cuisine-Panipuri-03.jpg/120px-Indian_cuisine-Panipuri-03.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Pani%20puri.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Panjeeri', 'North India', 'a mixture of butter, dried fruits and whole wheat flour served as a dessert.', 'Vegetarian', '', 'Panjeeri.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Panjeeri.JPG/120px-Panjeeri.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Panjeeri.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Papad', 'North India', 'A crispy add on to Lunch and Dinner, for adding a spicy and crunchier taste to food.', 'Vegetarian', '', 'Papad.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Onion_Masala_Papad.jpg/120px-Onion_Masala_Papad.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Papad.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Paratha', 'North India', 'flatbread native to the Indian subcontinent, prevalent throughout the modern-day nations of India, Sri Lanka, Pakistan, Nepal, Bangladesh, Maldives, and Myanmar, where wheat is the traditional staple', 'Vegetarian', '', 'Paratha.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Mintparatha2.0.jpg/120px-Mintparatha2.0.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Paratha.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Patrode', 'North India', 'A steamed vegetarian dish made from colocasia leaves (chevu in Tulu, taro, kesuve or arbi)', 'Vegetarian', '', 'Patrode.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Arbi-colocasia-pakoda-fritters.jpg/120px-Arbi-colocasia-pakoda-fritters.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Patrode.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Phirni', 'North India', 'Sweet rice pudding, cooked in milk, flavoured with cardamom, saffron, and rose water, and garnished with nuts like almonds and pistachios.', 'Vegetarian', '', 'Phirni.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Phirni.jpg/120px-Phirni.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Phirni.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Pinni', 'North India', 'A type of Punjabi and North Indian cuisine dish that is eaten mostly in winters. It is served as a dessert and is made from desi ghee, wheat flour, jaggery and almonds. Raisins may also be used.', 'Vegetarian', '', 'Pinni.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Pinni_cropped.JPG/120px-Pinni_cropped.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Pinni.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Rajma', 'North India', 'Main. Kidney beans & assorted spices.', 'Vegetarian', '', 'Rajma.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Rajma%2C_kidney_beans%2C_served_with_chawal%2C_rice.jpg/120px-Rajma%2C_kidney_beans%2C_served_with_chawal%2C_rice.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Rajma.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Samosa', 'North India', 'Normally served as an entree or appetiser. Potatoes, onions, peas, coriander, and lentils, may be served with a mint or tamarind sauce', 'Vegetarian/meat varieties', '', 'Samosa.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Samosachutney.jpg/120px-Samosachutney.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Samosa.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Shahi paneer or Rajwadi Chhena/Paneer', 'North India', 'A popular Indian as well as Nepalese dish, made with chhena or paneer in a thick cream and tomato gravy that is sweeter and spicier than paneer makhani', 'Vegetarian', '', 'Shahi paneer or Rajwadi Chhena-Paneer.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/Shahi_paneer.jpg/120px-Shahi_paneer.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Shahi%20paneer%20or%20Rajwadi%20Chhena-Paneer.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Shahi tukra', 'North India', 'A bread pudding in a rich gravy of thickened milk, garnished with sliced almonds', 'Vegetarian', '', 'Shahi tukra.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Shahi_Tukray_%28Shahi_Tukda%29.JPG/120px-Shahi_Tukray_%28Shahi_Tukda%29.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Shahi%20tukra.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Sooji halwa (Suji Lapsi)', 'North India', 'Semolina cooked with clarified butter and dry fruits. Semolina (Suji), clarified butter, cashew nuts.', 'Vegetarian', '', 'Sooji halwa (Suji Lapsi).jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Sooji_Halwa_%28Semolina_Pudding%29.JPG/120px-Sooji_Halwa_%28Semolina_Pudding%29.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Sooji%20halwa%20%28Suji%20Lapsi%29.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Tamatar Chaat', 'North India', 'Tamatar Chaat is an Indian street food which is most popular in north India specially in Varanasi.', 'Vegetarian', '', 'Tamatar Chaat.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Tamatar-chat-recipe-removebg-preview.png/120px-Tamatar-chat-recipe-removebg-preview.png?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Tamatar%20Chaat.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Tandoori Chicken', 'North India', 'Tandoori chicken as a dish originated in the Punjab before the independence of India and Pakistan.', 'Non-Vegetarian', '', 'Tandoori Chicken.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/A_piece_of_a_tandoori_chicken.JPG/120px-A_piece_of_a_tandoori_chicken.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Tandoori%20Chicken.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Tandoori Fish Tikka', 'North India', 'Fish marinated in lime and ginger and cooked over an open fire.', 'Non-Vegetarian', '', 'Tandoori Fish Tikka.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Tandoori_Fish_tikka.jpg/120px-Tandoori_Fish_tikka.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Tandoori%20Fish%20Tikka.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Ananas menaskai', 'South India', 'Pineapple cooked in jaggery and tamarind gravy', 'Vegetarian', '', 'Ananas menaskai.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Pineapple_%28Ananas%29_Gojju.jpg/120px-Pineapple_%28Ananas%29_Gojju.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Ananas%20menaskai.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Kesari bat', 'South India', 'Roasted flat rice flour cooked with sugar and dry fruits.', 'Vegetarian', '', 'Kesari bat.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/KEsari_baat.jpg/120px-KEsari_baat.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Kesari%20bat.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Avial', 'South India', 'Coconut paste, curd mixed with vegetables and some spices.', 'Vegetarian', 'Accompaniment with Staple food', 'Avial.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Sambar%26Avial.jpg/120px-Sambar%26Avial.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Avial.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Baida roti', 'South India', 'fried minced chicken stuffed in Egg roll', 'Non Vegetarian', 'Snacks', 'Baida roti.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/Chicken_baida_roti.jpg/120px-Chicken_baida_roti.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Baida%20roti.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Bhajji', 'South India', 'Vegetable or onion fritters which are known as Pakodas in North India and Pakistani cuisine', 'Vegetarian', 'Snack/ meal accompaniment', 'Bhajji.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Chilli_Bites_%28Bhaji%29.jpg/120px-Chilli_Bites_%28Bhaji%29.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Bhajji.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Bisi bele bath (Karnataka)', 'South India', 'Rice preparation with vegetables.', 'Vegetarian', 'main course', 'Bisi bele bath (Karnataka).jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Bisi_Bele_Bath.jpg/120px-Bisi_Bele_Bath.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Bisi%20bele%20bath%20%28Karnataka%29.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Bonda', 'South India', 'Potatoes, gram flour.', 'Vegetarian', 'Snack', 'Bonda.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Bonda2.jpg/120px-Bonda2.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Bonda.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Chettinadu Chicken', 'South India', 'Dish made chicken and spices', 'Non-Vegetarian', '', 'Chettinadu Chicken.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/db/Chettinad_Chicken_Fry-Home-AndhraPradesh-005.jpg/120px-Chettinad_Chicken_Fry-Home-AndhraPradesh-005.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Chettinadu%20Chicken.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Chicken 65', 'South India', 'Popular deep fried chicken preparation. Chicken, onion, ginger', 'Non-Vegetarian', '', 'Chicken 65.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Chicken_65.jpg/120px-Chicken_65.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Chicken%2065.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Dosa', 'South India', 'Pancake/Hopper. Ground rice, urad dal', 'Vegetarian', 'Breakfast dish', 'Dosa.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Dosa-chutney-sambhar.jpg/120px-Dosa-chutney-sambhar.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Dosa.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Double ka meetha', 'South India', 'Bread crumbs fried in ghee and dipped in milk and sugar syrup', 'Sweet', '', 'Double ka meetha.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/DoubleKaMeetha.JPG/120px-DoubleKaMeetha.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Double%20ka%20meetha.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Idiyappam', 'South India', 'Steamed rice noodles or vermicelli with Ground rice', 'Vegetarian', '', 'Idiyappam.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Idiyappam.jpg/120px-Idiyappam.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Idiyappam.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Idli', 'South India', 'Steamed cake of fermented rice and pulse flour. Rice, urad dal', 'Vegetarian', '', 'Idli.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Idli_Sambar.JPG/120px-Idli_Sambar.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Idli.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Indian omelette', 'South India', 'Egg omelette or veg omelette', '', '', 'Indian omelette.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Indian_Omelette.jpg/120px-Indian_Omelette.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Indian%20omelette.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Kanji', 'South India', 'a rice porridge', 'Vegetarian', '', 'Kanji.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/58/Chinese_rice_congee.jpg/120px-Chinese_rice_congee.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Kanji.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Kerala Beef Fry', 'South India', 'Beef, onions, spices, coconut, curry leaves', 'Non-vegetarian', '', 'Kerala Beef Fry.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/%E0%B4%AC%E0%B5%80%E0%B4%AB%E0%B5%8D%E0%B4%AB%E0%B5%8D%E0%B4%B0%E0%B5%88.jpg/120px-%E0%B4%AC%E0%B5%80%E0%B4%AB%E0%B5%8D%E0%B4%AB%E0%B5%8D%E0%B4%B0%E0%B5%88.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Kerala%20Beef%20Fry.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Koottu', 'South India', 'Vegetable, daal or lentil mixture boiled in water', 'Vegetarian', '', 'Koottu.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Cabbage_kootu.jpg/120px-Cabbage_kootu.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Koottu.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Kuzhakkattai', 'South India', 'Dumplings with Rice flour, jaggery, and coconut', 'Vegetarian', 'Snack', 'Kuzhakkattai.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Kozhukkatta.jpg/120px-Kozhukkatta.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Kuzhakkattai.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Masala Dosa', 'South India', 'Dosa with masala and potato.', 'Vegetarian', 'Breakfast', 'Masala Dosa.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Masala_Dosa_with_Aloo_masala.jpg/120px-Masala_Dosa_with_Aloo_masala.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Masala%20Dosa.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Obbattu (holige, bobbattu, pooran-poli)', 'South India', 'A stuffed (moong gram dal and jaggery or coconut poornam) paratha. Dish native to South and West India in the states of |- Karnataka, Andhra Pradesh and Maharashtra || Vegetarian|| Festival Sweet dish', '', '', 'Obbattu (holige, bobbattu, pooran-poli).jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Obbattu.jpg/120px-Obbattu.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Obbattu%20%28holige%2C%20bobbattu%2C%20pooran-poli%29.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Olan (dish)', 'South India', 'Light and subtle-flavored Kerala dish prepared from white gourd, ash-gourd or black-eyed peas, coconut milk and ginger seasoned with coconut oil.', 'Vegetarian', '', 'Olan (dish).jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Olan.jpg/120px-Olan.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Olan%20%28dish%29.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Papadum', 'South India', 'Thin deep fried disk served as meal accompaniment', 'Vegetarian', 'Fryums accompaniment', 'Papadum.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Pappadum.tif/lossless-page1-120px-Pappadum.tif.png?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Papadum.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Parotta', 'South India', 'a layered kerala parotta made with maida and dalda.', 'Vegetarian', '', 'Parotta.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Parotta.jpg/120px-Parotta.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Parotta.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Payasam', 'South India', 'Rice dessert. Rice, milk.', 'Vegetarian', '', 'Payasam.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Kheer.jpg/120px-Kheer.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Payasam.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Pesarattu', 'South India', 'Dosa (pancake or crepe) of Andhra Pradesh made from moong dal (lentils), grains and spice batter.', 'Vegetarian', '', 'Pesarattu.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Pesarattu.jpg/120px-Pesarattu.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Pesarattu.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Pongal', 'South India', 'Pulao', 'Vegetarian', 'Breakfast dish', 'Pongal.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Pongali.JPG/120px-Pongali.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Pongal.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Puttu', 'South India', 'Ground rice, jaggery, cardamom powder, mixed and steam cooked', 'Vegetarian', 'Breakfast/Snack', 'Puttu.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Puttu.jpg/120px-Puttu.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Puttu.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Sambar', 'South India', 'Lentil soup cooked with vegetables and a blend of south Indian spices (masala). Usually taken with rice, idli, dosa, pongal or upma.', 'Vegetarian', '', 'Sambar.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Sambaar_kadamba.jpg/120px-Sambaar_kadamba.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Sambar.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Sandige (Karnataka), Vattral', 'South India', 'Deep fried meal accompaniment made with rice, sago and ash gourd', 'Vegetarian', 'Fryums-accompaniment', 'Sandige (Karnataka), Vattral.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Aralu_Sandige.jpg/120px-Aralu_Sandige.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Sandige%20%28Karnataka%29%2C%20Vattral.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Sevai', 'South India', 'Kind of rice vermicelli used for breakfast', '', '', 'Sevai.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Sevai_plain320.jpg/120px-Sevai_plain320.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Sevai.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Sponge dosa', 'South India', 'dosa made of fermented poha and rice', 'Vegetarian', '', 'Sponge dosa.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Sponge_dosa%2C_media_wada%2C_sambar%2C_chutney_and_potato_bhaji.jpg/120px-Sponge_dosa%2C_media_wada%2C_sambar%2C_chutney_and_potato_bhaji.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Sponge%20dosa.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Thattai', 'South India', 'Type of puri made with rice, gram, urad dal flour', 'Vegetarian', '', 'Thattai.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Box_with_savories_and_sweets_on_a_plain_background.jpg/120px-Box_with_savories_and_sweets_on_a_plain_background.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Thattai.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Thayir sadam, mosaranna, perugannam', 'South India', 'a curd rice dish', 'Vegetarian', '', 'Thayir sadam, mosaranna, perugannam.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Curd_rice_and_hummus.jpg/120px-Curd_rice_and_hummus.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Thayir%20sadam%2C%20mosaranna%2C%20perugannam.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Uttapam Tamil Nadu', 'South India', 'Rice pancake/hopper with a topping of onions / tomatoes / coconut', 'Vegetarian', 'Breakfast dish', 'Uttapam Tamil Nadu.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Indian_Pancake.jpg/120px-Indian_Pancake.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Uttapam%20Tamil%20Nadu.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Vada', 'South India', 'Savory donut. Urad dal.', 'Vegetarian', 'accompaniment', 'Vada.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Vada_2.jpg/120px-Vada_2.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Vada.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Wheat upma, Uppittu', 'South India', 'A breakfast dish and snack. Upma prepared from wheat dhalia rava.', 'Vegetarian', 'Breakfast dish', 'Wheat upma, Uppittu.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Upma.jpg/120px-Upma.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Wheat%20upma%2C%20Uppittu.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Barfi', 'West India', 'Sweet', 'Vegetarian Desert', '', 'Barfi.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Barfi-Diwali_sweet.jpg/120px-Barfi-Diwali_sweet.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Barfi.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Bhakri', 'West India', 'Whole wheat flour bread, thicker than rotli, crispy.', '', '', 'Bhakri.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Another_Vegetarian_Meal.jpg/120px-Another_Vegetarian_Meal.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Bhakri.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Bombil fry', 'West India', 'Main Course; Bombay Duck (Fish).', 'Non-Vegetarian', '', 'Bombil fry.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Bombil.jpg/120px-Bombil.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Bombil%20fry.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Chaat', 'West India', 'Snack', 'Vegetarian', '', 'Chaat_2.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Bhalla_Papri_Chaat_with_saunth_chutney.jpg/120px-Bhalla_Papri_Chaat_with_saunth_chutney.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Chaat_2.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Chevdo', 'West India', 'Mixture of Flattened rice, groundnut, chana, masala.', '', '', 'Chevdo.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/Bombaymix.jpg/120px-Bombaymix.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Chevdo.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Dabeli', 'West India', 'Snack made by mixing boiled potatoes with a special dabeli masala, putting the mixture in a ladi pav', 'Vegetarian', '', 'Dabeli.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Dabeli.jpg/120px-Dabeli.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Dabeli.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Dahi vada', 'West India', 'Fried lentil balls in a yogurt sauce. Lentils, yogurt.', 'Vegetarian', '', 'Dahi vada.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Dahi_Vadas_%28Dhai_Bhalla%29.JPG/120px-Dahi_Vadas_%28Dhai_Bhalla%29.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Dahi%20vada.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Dhokla', 'West India', 'Lentil snack. Gram.', 'Vegetarian', '', 'Dhokla.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Khaman_dhokla.jpg/120px-Khaman_dhokla.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Dhokla.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Dum aaloo', 'West India', 'Main dish. Potatoes deep fry, yogurt, coriander powder, ginger powder.', 'Vegetarian', '', 'Dum aaloo.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Kashmiri_Dum_Aaloo.JPG/120px-Kashmiri_Dum_Aaloo.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Dum%20aaloo.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Gajar halwo', 'West India', 'Sweet. Carrot Halwa', '', '', 'Gajar halwo.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Gajjar_ka_halwa_%28carrot_halwa%29.JPG/120px-Gajjar_ka_halwa_%28carrot_halwa%29.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Gajar%20halwo.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Gulab jamun', 'West India', 'Sweet', '', '', 'Gulab jamun.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Gulab_Jamun.jpg/120px-Gulab_Jamun.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Gulab%20jamun.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Gur', 'West India', 'Sweet unrefined brown sugar sold in blocks.', '', '', 'Gur.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Sa-indian-gud.jpg/120px-Sa-indian-gud.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Gur.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Jalebi', 'West India', 'Sweet maida & grained semolina flour, baking powder, curd, sugar.', 'Sweet', '', 'Jalebi_2.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Jalebi_%28sweet%29.jpg/120px-Jalebi_%28sweet%29.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Jalebi_2.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Jeera Aloo', 'West India', 'Typical West Indian dish', 'Vegetarian', '', 'Jeera Aloo.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/Jeera_aloo_served_with_sprouts_and_dal.jpg/120px-Jeera_aloo_served_with_sprouts_and_dal.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Jeera%20Aloo.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Khakhra', 'West India', 'Gujarati Snack. Wheat flour, methi.', '', '', 'Khakhra.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Gujarati_khakhra.jpg/120px-Gujarati_khakhra.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Khakhra.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Khandvi', 'West India', 'Snack. Besan.', '', '', 'Khandvi.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Khandvi%2C_Gujarati_snack.jpg/120px-Khandvi%2C_Gujarati_snack.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Khandvi.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Kombdi vade', 'West India', 'Chicken Curry with Bread. Chicken.', '', '', 'Kombdi vade.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Komdi_vade.jpg/120px-Komdi_vade.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Kombdi%20vade.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Laddu', 'West India', 'Sweet', '', '', 'Laddu.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Laddu1.JPG/120px-Laddu1.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Laddu.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Malpua', 'West India', 'Sweet', '', '', 'Malpua.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Malapua_Odia_cuisine.jpg/120px-Malapua_Odia_cuisine.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Malpua.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Chakri (chakali)', 'West India', 'a Savoury snack. Mixed grain flour.', 'Vegetarian', '', 'Chakri (chakali).jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Chakali.JPG/120px-Chakali.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Chakri%20%28chakali%29.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Panipuri', 'West India', 'Snack', '', '', 'Panipuri.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Indian_cuisine-Panipuri-03.jpg/120px-Indian_cuisine-Panipuri-03.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Panipuri.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Pav Bhaji', 'West India', 'Mixed curry of onion, capsicum, peas, cauliflower potatoes.', '', '', 'Pav Bhaji.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Pav_Bhaji.jpg/120px-Pav_Bhaji.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Pav%20Bhaji.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Pooran-poli', 'West India', 'Sweet stuffed bread. Wheat flour, gram.', '', '', 'Pooran-poli.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/Coconut_holige.jpg/120px-Coconut_holige.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Pooran-poli.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Poori', 'West India', 'Bread. Wheat flour.', '', '', 'Poori.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Puri.jpg/120px-Puri.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Poori.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Puri Bhaji', 'West India', 'Breakfast or Snack', '', '', 'Puri Bhaji.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Puri_Bhaji.JPG/120px-Puri_Bhaji.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Puri%20Bhaji.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Shankarpali', 'West India', 'Sweet or savoury snack. Plain flour, sugar.', '', '', 'Shankarpali.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Shankarpali_sweets_mithai_Western_India_2012.jpg/120px-Shankarpali_sweets_mithai_Western_India_2012.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Shankarpali.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Shiro', 'West India', 'Sweet roasted semolina/flour/dal with milk, butter, sugar, nuts and raisins.', '', '', 'Shiro.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Taita_and_shiro.jpg/120px-Taita_and_shiro.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Shiro.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Shrikhand', 'West India', 'A thick yogurt-based sweet dessert garnished with ground nuts, cardamom, and saffron.', '', '', 'Shrikhand.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Shrikhand_london_kastoori.jpg/120px-Shrikhand_london_kastoori.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Shrikhand.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Sohan papdi', 'West India', 'Sweet', '', '', 'Sohan papdi.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/Soanpapdi.JPG/120px-Soanpapdi.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Sohan%20papdi.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Sukhdi', 'West India', 'Sweet', '', '', 'Sukhdi.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Sukhdi.jpg/120px-Sukhdi.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Sukhdi.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Upmaa', 'West India', 'a dish originating from the Indian subcontinent, cooked as a thick porridge from dry-roasted semolina or coarse rice flour.', '', '', 'Upmaa.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Upma.jpg/120px-Upma.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Upmaa.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Vada pav', 'West India', 'Burger. Gram flour, potatoes, chilli, garlic, ginger.', '', '', 'Vada pav.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/Jumbo_Vada_Pav_%28dodged%29.jpg/120px-Jumbo_Vada_Pav_%28dodged%29.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Vada%20pav.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Vindaloo', 'West India', 'Goan pork vindaloo. Pork, goan red chilli paste.', 'Non-Vegetarian', '', 'Vindaloo.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/Vindalho.jpg/120px-Vindalho.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Vindaloo.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Ghebar or Ghevar', 'West India', 'Sweet from Surat', '', '', 'Ghebar or Ghevar.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/GhevarRajasthaniSweet.jpg/120px-GhevarRajasthaniSweet.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Ghebar%20or%20Ghevar.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Lilva Kachori', 'West India', 'Snack. Lilva and whole wheat flour.', '', '', 'Lilva Kachori.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Cachuri2_flipped.jpg/120px-Cachuri2_flipped.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Lilva%20Kachori.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Maghaz', 'West India', '', '', '', 'Maghaz.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Magaj.jpg/120px-Magaj.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Maghaz.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Daab chingri', 'East India', 'Prawn curry cooked in green coconut.', 'Non-vegetarian', '', 'Daab chingri.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Daab_Chingri.jpg/120px-Daab_Chingri.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Daab%20chingri.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Luchi', 'East India', 'A Puffed bread, fried in oil, made from flour. A Bengali speciality.', 'Vegetarian', '', 'Luchi.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Luchi_Thali.jpg/120px-Luchi_Thali.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Luchi.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Malpua/Malpoa', 'East India', 'Sweet snacks notable in Northeast and East India, specially in Odisha.', 'Sweet', '', 'Malpua-Malpoa.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Malapua.jpg/120px-Malapua.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Malpua-Malpoa.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Momo', 'East India', 'Originally from Tibet, it is a popular snack/ food item in India specially within Indo-Nepalese community.', '', '', 'Momo.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Momo101.jpg/120px-Momo101.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Momo.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Black rice', 'East India', 'A special local variety of rice', '', '', 'Black rice.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Black_rice_01.JPG/120px-Black_rice_01.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Black%20rice.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Brown Rice', 'East India', 'A special local variety of rice.', '', '', 'Brown Rice.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Brun_ris.jpg/120px-Brun_ris.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Brown%20Rice.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Chhenagaja', 'East India', 'Odia Dessert. Cottage cheese, flour, sugar syrup.', '', '', 'Chhenagaja.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Chena_gaja_Odia_cuisine.jpg/120px-Chena_gaja_Odia_cuisine.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Chhenagaja.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Chhenapoda', 'East India', 'Dessert. Cottage cheese, flour, sugar syrup. Odia Specialty.', '', '', 'Chhenapoda.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Chennapoda.jpg/120px-Chennapoda.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Chhenapoda.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Chingri malai curry', 'East India', 'Curry. Prawn, coconut, mustard, steamed. Traditional Bengali Dish.', 'Non-vegetarian', '', 'Chingri malai curry.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Chingri_Malai_Curry.jpg/120px-Chingri_Malai_Curry.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Chingri%20malai%20curry.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Dal', 'East India', 'Lentils.', 'Vegetarian', '', 'Dal.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Dal_Makhani.jpg/120px-Dal_Makhani.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Dal.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Goja', 'East India', 'A sweet Bengali speciality.', '', '', 'Goja.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Goja_of_Burdwan.jpg/120px-Goja_of_Burdwan.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Goja.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Ilish or Chingri Bhape', 'East India', 'Curry. Ilish (Hilsha fish) or prawn, coconut, mustard, steamed. Traditional Bengali Dish.', 'Non-vegetarian', '', 'Ilish or Chingri Bhape.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Ilish.JPG/120px-Ilish.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Ilish%20or%20Chingri%20Bhape.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Machher Jhol', 'East India', 'A curry of fish, and various spices.', '', '', 'Machher Jhol_2.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/MACHHA_HALADI.jpg/120px-MACHHA_HALADI.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Machher%20Jhol_2.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Mishti Doi', 'East India', 'A dessert with curd, sugar syrup or jaggery. Bengali Sweet curd.', '', '', 'Mishti Doi.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Mishti_Doi.jpg/120px-Mishti_Doi.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Mishti%20Doi.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Pakhala', 'East India', 'Odia dish with fermented rice, yoghurt, salt & seasonings.', '', '', 'Pakhala_2.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Pakhala.jpg/120px-Pakhala.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Pakhala_2.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Bhaji', 'East India', 'Fried Vegetables.', '', '', 'Bhaji.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Chilli_Bites_%28Bhaji%29.jpg/120px-Chilli_Bites_%28Bhaji%29.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Bhaji.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Pantua', 'East India', 'It is a traditional Bengali sweet made of deep-fried balls of semolina, chhena, milk, ghee and sugar syrup. Notable in West Bengal, Eastern India and Bangladesh.', '', '', 'Pantua.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Pantua_-_Kolkata_2011-09-20_5431.JPG/120px-Pantua_-_Kolkata_2011-09-20_5431.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Pantua.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Peda', 'East India', 'Sweet', '', '', 'Peda.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Dharwad_peda.jpg/120px-Dharwad_peda.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Peda.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Red Rice', 'East India', 'Special local variety of rice.', '', '', 'Red Rice.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Rice%2C_red-rice%2C_AIVANAM-like.JPG/120px-Rice%2C_red-rice%2C_AIVANAM-like.JPG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Red%20Rice.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Rice', 'East India', 'Staple Food.', '', '', 'Rice.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/White%2C_Brown%2C_Red_%26_Wild_rice.jpg/120px-White%2C_Brown%2C_Red_%26_Wild_rice.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Rice.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Rasagola/Roshogolla', 'East India', 'A sweet dessert using cottage cheese, flour and sugar syrup. Originated independently in different versions and taste in Odisha and West Bengal, Eastern India.', 'Sweet', '', 'Rasagola-Roshogolla.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/%22Fluffy_Rasgulla%22.jpg/120px-%22Fluffy_Rasgulla%22.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Rasagola-Roshogolla.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Shondesh', 'East India', 'A dessert with milk and sugar. A signature Bengali dish.', 'Sweet', '', 'Shondesh.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Sondeshnolen.jpg/120px-Sondeshnolen.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Shondesh.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;
INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('Shukto', 'East India', 'A Bengali cuisine. Diced potatoes, sweet potatoes, broad beans, eggplant, drumsticks, raw bananas, radish cooked together and sautéed with mustard seeds. This culinary cooked in mustard oil and sometimes shredded coconut can also be used.', '', '', 'Shukto.jpg', 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Shukto_-_Behala_Manton%2C_Kolkata_-_West_Bengal_-_IMG-20210322-WA0013.jpg/120px-Shukto_-_Behala_Manton%2C_Kolkata_-_West_Bengal_-_IMG-20210322-WA0013.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail', 'https://en.wikipedia.org/wiki/List_of_Indian_dishes', '/images/Shukto.jpg')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;