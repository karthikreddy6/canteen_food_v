-- Standalone SQL script: Insert categories and equally distribute menu items across canteens
-- Assumes canteens table is populated. Matches canteens by row number / name.


DO $$
DECLARE
    canteens_list UUID[];
    num_canteens INT;
    c_idx INT;
    cat_id UUID;
    cant_id UUID;
BEGIN
    -- Collect all active canteen IDs into an array
    SELECT array_agg(id ORDER BY name) INTO canteens_list FROM canteens WHERE is_active = true;
    num_canteens := array_length(canteens_list, 1);

    IF num_canteens IS NULL OR num_canteens = 0 THEN
        RAISE NOTICE 'No active canteens found in database. Please add canteens first.';
        RETURN;
    END IF;


    -- Dish 1: Machher Jhol
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Machher Jhol' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Machher Jhol', '/images/Machher%20Jhol.jpg', 1, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (0 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Machher Jhol') THEN
        UPDATE menu_items SET
            price = 140.00,
            original_price = 160.00,
            discount_percent = 12.50,
            category_id = cat_id,
            image_url = '/images/Machher%20Jhol.jpg',
            description = 'Fish with potol, tomato, chillies, ginger and garlic from Assam',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Machher Jhol';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Machher Jhol', 140.00, 160.00, 12.50, cat_id, cant_id, '/images/Machher%20Jhol.jpg', 'Fish with potol, tomato, chillies, ginger and garlic from Assam', 50, true, false, true, 12);
    END IF;


    -- Dish 2: Chak-Hao Kheer
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Chak-Hao Kheer' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Chak-Hao Kheer', '/images/Chak-Hao%20Kheer.jpg', 2, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (1 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Chak-Hao Kheer') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Chak-Hao%20Kheer.jpg',
            description = 'Purple rice porridge from Manipur',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Chak-Hao Kheer';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Chak-Hao Kheer', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Chak-Hao%20Kheer.jpg', 'Purple rice porridge from Manipur', 50, true, false, true, 12);
    END IF;


    -- Dish 3: Achari baingan
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Achari baingan' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Achari baingan', '/images/Achari%20baingan.jpg', 3, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (2 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Achari baingan') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Achari%20baingan.jpg',
            description = 'Brinjal cooked with pickle spices in gravy',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Achari baingan';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Achari baingan', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Achari%20baingan.jpg', 'Brinjal cooked with pickle spices in gravy', 50, true, false, true, 12);
    END IF;


    -- Dish 4: Aloo gobi
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Aloo gobi' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Aloo gobi', '/images/Aloo%20gobi.jpg', 4, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (3 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Aloo gobi') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Aloo%20gobi.jpg',
            description = 'Cauliflower with potatoes sautéed with garam masala, turmeric, sometimes kalonji and curry leaves.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Aloo gobi';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Aloo gobi', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Aloo%20gobi.jpg', 'Cauliflower with potatoes sautéed with garam masala, turmeric, sometimes kalonji and curry leaves.', 50, true, false, true, 12);
    END IF;


    -- Dish 5: Aloo tikki
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Aloo tikki' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Aloo tikki', '/images/Aloo%20tikki.jpg', 5, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (4 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Aloo tikki') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Aloo%20tikki.jpg',
            description = 'Patties of potato mixed with some vegetables fried',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Aloo tikki';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Aloo tikki', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Aloo%20tikki.jpg', 'Patties of potato mixed with some vegetables fried', 50, true, false, true, 12);
    END IF;


    -- Dish 6: Aloo matar
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Aloo matar' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Aloo matar', '/images/Aloo%20matar.jpg', 6, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (5 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Aloo matar') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Aloo%20matar.jpg',
            description = 'Potatoes and peas in curry',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Aloo matar';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Aloo matar', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Aloo%20matar.jpg', 'Potatoes and peas in curry', 50, true, false, true, 12);
    END IF;


    -- Dish 7: Aloo kulcha
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Aloo kulcha' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Aloo kulcha', '/images/Aloo%20kulcha.jpg', 7, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (6 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Aloo kulcha') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Aloo%20kulcha.jpg',
            description = 'Mildly leavened flatbread stuffed with potatoes',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Aloo kulcha';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Aloo kulcha', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Aloo%20kulcha.jpg', 'Mildly leavened flatbread stuffed with potatoes', 50, true, false, true, 12);
    END IF;


    -- Dish 8: Aloo methi
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Aloo methi' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Aloo methi', '/images/Aloo%20methi.jpg', 8, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (7 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Aloo methi') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Aloo%20methi.jpg',
            description = 'Sautéed potatoes (aloo) and chopped fenugreek leaves (methi) with chopped onions, garlic, and a blend of spices such as cumin, coriander, turmeric, and chili powder.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Aloo methi';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Aloo methi', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Aloo%20methi.jpg', 'Sautéed potatoes (aloo) and chopped fenugreek leaves (methi) with chopped onions, garlic, and a blend of spices such as cumin, coriander, turmeric, and chili powder.', 50, true, false, true, 12);
    END IF;


    -- Dish 9: Aloo shimla mirch
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Aloo shimla mirch' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Aloo shimla mirch', '/images/Aloo%20shimla%20mirch.jpg', 9, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (8 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Aloo shimla mirch') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Aloo%20shimla%20mirch.jpg',
            description = 'Green capsicum with potatoes sautéed with cumin seeds, onions, tomatoes, ginger-garlic paste, turmeric, red chilli powder and garam masala',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Aloo shimla mirch';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Aloo shimla mirch', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Aloo%20shimla%20mirch.jpg', 'Green capsicum with potatoes sautéed with cumin seeds, onions, tomatoes, ginger-garlic paste, turmeric, red chilli powder and garam masala', 50, true, false, true, 12);
    END IF;


    -- Dish 10: Baati
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Baati' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Baati', '/images/Baati.jpg', 10, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (9 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Baati') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Baati.jpg',
            description = 'Hard, unleavened bread cooked in most of areas of Rajasthan, and in some parts of Madhya Pradesh, and Gujarat states of India.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Baati';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Baati', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Baati.jpg', 'Hard, unleavened bread cooked in most of areas of Rajasthan, and in some parts of Madhya Pradesh, and Gujarat states of India.', 50, true, false, true, 12);
    END IF;


    -- Dish 11: Bhatura
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Bhatura' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Bhatura', '/images/Bhatura.jpg', 11, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (10 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Bhatura') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Bhatura.jpg',
            description = 'A fluffy deep-fried leavened bread originating from the Indian subcontinent.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Bhatura';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Bhatura', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Bhatura.jpg', 'A fluffy deep-fried leavened bread originating from the Indian subcontinent.', 50, true, false, true, 12);
    END IF;


    -- Dish 12: Bhindi masala
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Bhindi masala' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Bhindi masala', '/images/Bhindi%20masala.jpg', 12, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (11 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Bhindi masala') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Bhindi%20masala.jpg',
            description = 'Okra sautéed with onions and tomatoes',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Bhindi masala';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Bhindi masala', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Bhindi%20masala.jpg', 'Okra sautéed with onions and tomatoes', 50, true, false, true, 12);
    END IF;


    -- Dish 13: Biryani
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Biryani' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Biryani', '/images/Biryani.jpg', 13, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (12 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Biryani') THEN
        UPDATE menu_items SET
            price = 140.00,
            original_price = 160.00,
            discount_percent = 12.50,
            category_id = cat_id,
            image_url = '/images/Biryani.jpg',
            description = 'Mixed rice dish, optional spices, optional vegetables, meats or seafood. Can be served with plain yogurt.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Biryani';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Biryani', 140.00, 160.00, 12.50, cat_id, cant_id, '/images/Biryani.jpg', 'Mixed rice dish, optional spices, optional vegetables, meats or seafood. Can be served with plain yogurt.', 50, true, false, true, 12);
    END IF;


    -- Dish 14: Butter chicken, murgh mahal
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Butter chicken, murgh mahal' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Butter chicken, murgh mahal', '/images/Butter%20chicken%2C%20murgh%20mahal.jpg', 14, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (13 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Butter chicken, murgh mahal') THEN
        UPDATE menu_items SET
            price = 140.00,
            original_price = 160.00,
            discount_percent = 12.50,
            category_id = cat_id,
            image_url = '/images/Butter%20chicken%2C%20murgh%20mahal.jpg',
            description = 'Chicken in a mildly spiced tomato sauce.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Butter chicken, murgh mahal';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Butter chicken, murgh mahal', 140.00, 160.00, 12.50, cat_id, cant_id, '/images/Butter%20chicken%2C%20murgh%20mahal.jpg', 'Chicken in a mildly spiced tomato sauce.', 50, true, false, true, 12);
    END IF;


    -- Dish 15: Chaat
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Chaat' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Chaat', '/images/Chaat.jpg', 15, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (14 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Chaat') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Chaat.jpg',
            description = 'Usually containing potato patty fried in oil, topped with sweet yogurt, and other sauces and spices',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Chaat';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Chaat', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Chaat.jpg', 'Usually containing potato patty fried in oil, topped with sweet yogurt, and other sauces and spices', 50, true, false, true, 12);
    END IF;


    -- Dish 16: Chana masala
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Chana masala' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Chana masala', '/images/Chana%20masala.jpg', 16, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (15 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Chana masala') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Chana%20masala.jpg',
            description = 'Chickpeas of the Chana type in tomato based sauce.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Chana masala';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Chana masala', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Chana%20masala.jpg', 'Chickpeas of the Chana type in tomato based sauce.', 50, true, false, true, 12);
    END IF;


    -- Dish 17: Chapati
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Chapati' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Chapati', '/images/Chapati.jpg', 17, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (16 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Chapati') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Chapati.jpg',
            description = 'Unleavened flatbread originating from the Indian subcontinent and staple in India, Nepal, Bangladesh, Pakistan, Sri Lanka, East Africa and the Caribbean.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Chapati';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Chapati', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Chapati.jpg', 'Unleavened flatbread originating from the Indian subcontinent and staple in India, Nepal, Bangladesh, Pakistan, Sri Lanka, East Africa and the Caribbean.', 50, true, false, true, 12);
    END IF;


    -- Dish 18: Chicken rezala
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Chicken rezala' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Chicken rezala', '/images/Chicken%20rezala.jpg', 18, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (17 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Chicken rezala') THEN
        UPDATE menu_items SET
            price = 140.00,
            original_price = 160.00,
            discount_percent = 12.50,
            category_id = cat_id,
            image_url = '/images/Chicken%20rezala.jpg',
            description = 'Bhopali style chicken cooked in a rich gravy with mint',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Chicken rezala';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Chicken rezala', 140.00, 160.00, 12.50, cat_id, cant_id, '/images/Chicken%20rezala.jpg', 'Bhopali style chicken cooked in a rich gravy with mint', 50, true, false, true, 12);
    END IF;


    -- Dish 19: Chicken Tikka
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Chicken Tikka' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Chicken Tikka', '/images/Chicken%20Tikka.jpg', 19, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (18 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Chicken Tikka') THEN
        UPDATE menu_items SET
            price = 140.00,
            original_price = 160.00,
            discount_percent = 12.50,
            category_id = cat_id,
            image_url = '/images/Chicken%20Tikka.jpg',
            description = 'Chicken with spices served on a skewer',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Chicken Tikka';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Chicken Tikka', 140.00, 160.00, 12.50, cat_id, cant_id, '/images/Chicken%20Tikka.jpg', 'Chicken with spices served on a skewer', 50, true, false, true, 12);
    END IF;


    -- Dish 20: Chicken tikka masala
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Chicken tikka masala' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Chicken tikka masala', '/images/Chicken%20tikka%20masala.jpg', 20, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (19 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Chicken tikka masala') THEN
        UPDATE menu_items SET
            price = 140.00,
            original_price = 160.00,
            discount_percent = 12.50,
            category_id = cat_id,
            image_url = '/images/Chicken%20tikka%20masala.jpg',
            description = 'Chicken marinated in a Yogurt tomato sauce. It is known to have a creamy texture.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Chicken tikka masala';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Chicken tikka masala', 140.00, 160.00, 12.50, cat_id, cant_id, '/images/Chicken%20tikka%20masala.jpg', 'Chicken marinated in a Yogurt tomato sauce. It is known to have a creamy texture.', 50, true, false, true, 12);
    END IF;


    -- Dish 21: Chole bhature
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Chole bhature' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Chole bhature', '/images/Chole%20bhature.jpg', 21, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (20 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Chole bhature') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Chole%20bhature.jpg',
            description = 'Main course with chickpeas, assorted spices, wheat flour and bhatura yeast.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Chole bhature';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Chole bhature', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Chole%20bhature.jpg', 'Main course with chickpeas, assorted spices, wheat flour and bhatura yeast.', 50, true, false, true, 12);
    END IF;


    -- Dish 22: Daal baati churma
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Daal baati churma' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Daal baati churma', '/images/Daal%20baati%20churma.jpg', 22, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (21 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Daal baati churma') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Daal%20baati%20churma.jpg',
            description = 'A Rajasthani specialty',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Daal baati churma';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Daal baati churma', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Daal%20baati%20churma.jpg', 'A Rajasthani specialty', 50, true, false, true, 12);
    END IF;


    -- Dish 23: Dal makhani (kali dal)
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Dal makhani (kali dal)' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Dal makhani (kali dal)', '/images/Dal%20makhani%20%28kali%20dal%29.jpg', 23, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (22 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Dal makhani (kali dal)') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Dal%20makhani%20%28kali%20dal%29.jpg',
            description = 'Lentils in a creamy and aromatic sauce made of butter, tomato sauce, and a blend of spices',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Dal makhani (kali dal)';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Dal makhani (kali dal)', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Dal%20makhani%20%28kali%20dal%29.jpg', 'Lentils in a creamy and aromatic sauce made of butter, tomato sauce, and a blend of spices', 50, true, false, true, 12);
    END IF;


    -- Dish 24: Dalpuri
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Dalpuri' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Dalpuri', '/images/Dalpuri.jpg', 24, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (23 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Dalpuri') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Dalpuri.jpg',
            description = 'Stuffed dal in parathas',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Dalpuri';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Dalpuri', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Dalpuri.jpg', 'Stuffed dal in parathas', 50, true, false, true, 12);
    END IF;


    -- Dish 25: Dal tadka
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Dal tadka' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Dal tadka', '/images/Dal%20tadka.jpg', 25, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (24 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Dal tadka') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Dal%20tadka.jpg',
            description = 'Typical north Indian tadka',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Dal tadka';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Dal tadka', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Dal%20tadka.jpg', 'Typical north Indian tadka', 50, true, false, true, 12);
    END IF;


    -- Dish 26: Dum aloo
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Dum aloo' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Dum aloo', '/images/Dum%20aloo.jpg', 26, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (25 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Dum aloo') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Dum%20aloo.jpg',
            description = 'Potatoes cooked in curry',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Dum aloo';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Dum aloo', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Dum%20aloo.jpg', 'Potatoes cooked in curry', 50, true, false, true, 12);
    END IF;


    -- Dish 27: Poha
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Poha' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Poha', '/images/Poha.jpg', 27, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (26 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Poha') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Poha.jpg',
            description = 'Specialty from Madhya Pradesh. Common snack in central part of India. Flattened rice, potato, turmeric.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Poha';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Poha', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Poha.jpg', 'Specialty from Madhya Pradesh. Common snack in central part of India. Flattened rice, potato, turmeric.', 50, true, false, true, 12);
    END IF;


    -- Dish 28: Gajar Pak
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Gajar Pak' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Gajar Pak', '/images/Gajar%20Pak.jpg', 28, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (27 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Gajar Pak') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Gajar%20Pak.jpg',
            description = 'Sweet dish made using carrot, milk, ghee, dry fruits.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Gajar Pak';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Gajar Pak', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Gajar%20Pak.jpg', 'Sweet dish made using carrot, milk, ghee, dry fruits.', 50, true, false, true, 12);
    END IF;


    -- Dish 29: Gatte ki Sabzi
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Gatte ki Sabzi' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Gatte ki Sabzi', '/images/Gatte%20ki%20Sabzi.jpg', 29, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (28 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Gatte ki Sabzi') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Gatte%20ki%20Sabzi.jpg',
            description = 'Gatte (made up of besan) are added to spice gravy made of curd.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Gatte ki Sabzi';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Gatte ki Sabzi', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Gatte%20ki%20Sabzi.jpg', 'Gatte (made up of besan) are added to spice gravy made of curd.', 50, true, false, true, 12);
    END IF;


    -- Dish 30: Gobhi matar
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Gobhi matar' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Gobhi matar', '/images/Gobhi%20matar.jpg', 30, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (29 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Gobhi matar') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Gobhi%20matar.jpg',
            description = 'Cauliflower in a tomato sauce',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Gobhi matar';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Gobhi matar', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Gobhi%20matar.jpg', 'Cauliflower in a tomato sauce', 50, true, false, true, 12);
    END IF;


    -- Dish 31: Imarti
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Imarti' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Imarti', '/images/Imarti.jpg', 31, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (30 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Imarti') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Imarti.jpg',
            description = 'spherically meshed sweet dish from North India made up of batter from moong dal dipped in sugary syrup',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Imarti';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Imarti', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Imarti.jpg', 'spherically meshed sweet dish from North India made up of batter from moong dal dipped in sugary syrup', 50, true, false, true, 12);
    END IF;


    -- Dish 32: Jalebi
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Jalebi' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Jalebi', '/images/Jalebi.jpg', 32, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (31 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Jalebi') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Jalebi.jpg',
            description = 'A North Indian twisted noodle like sweet dish dipped in sugary syrup',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Jalebi';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Jalebi', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Jalebi.jpg', 'A North Indian twisted noodle like sweet dish dipped in sugary syrup', 50, true, false, true, 12);
    END IF;


    -- Dish 33: Jalfrezi
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Jalfrezi' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Jalfrezi', '/images/Jalfrezi.jpg', 33, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (32 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Jalfrezi') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Jalfrezi.jpg',
            description = 'Meat and spices fried in a pan. Can be vegetarian as well.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Jalfrezi';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Jalfrezi', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Jalfrezi.jpg', 'Meat and spices fried in a pan. Can be vegetarian as well.', 50, true, false, true, 12);
    END IF;


    -- Dish 34: Kachori
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Kachori' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Kachori', '/images/Kachori.jpg', 34, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (33 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Kachori') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Kachori.jpg',
            description = 'Rajasthani / Marwari special',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Kachori';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Kachori', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Kachori.jpg', 'Rajasthani / Marwari special', 50, true, false, true, 12);
    END IF;


    -- Dish 35: Kadai paneer
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Kadai paneer' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Kadai paneer', '/images/Kadai%20paneer.jpg', 35, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (34 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Kadai paneer') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Kadai%20paneer.jpg',
            description = 'Paneer and green peppers in tomato gravy',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Kadai paneer';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Kadai paneer', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Kadai%20paneer.jpg', 'Paneer and green peppers in tomato gravy', 50, true, false, true, 12);
    END IF;


    -- Dish 36: Katha meetha petha / kaddu halwa
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Katha meetha petha / kaddu halwa' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Katha meetha petha / kaddu halwa', '/images/Katha%20meetha%20petha%20-%20kaddu%20halwa.jpg', 36, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (35 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Katha meetha petha / kaddu halwa') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Katha%20meetha%20petha%20-%20kaddu%20halwa.jpg',
            description = 'Pumpkin cooked in spices',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Katha meetha petha / kaddu halwa';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Katha meetha petha / kaddu halwa', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Katha%20meetha%20petha%20-%20kaddu%20halwa.jpg', 'Pumpkin cooked in spices', 50, true, false, true, 12);
    END IF;


    -- Dish 37: Kheer
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Kheer' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Kheer', '/images/Kheer.jpg', 37, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (36 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Kheer') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Kheer.jpg',
            description = 'Rice cooked with milk and dry fruits',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Kheer';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Kheer', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Kheer.jpg', 'Rice cooked with milk and dry fruits', 50, true, false, true, 12);
    END IF;


    -- Dish 38: Khichdi
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Khichdi' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Khichdi', '/images/Khichdi.jpg', 38, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (37 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Khichdi') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Khichdi.jpg',
            description = 'Rice cooked with daal and veggies and sauteed',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Khichdi';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Khichdi', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Khichdi.jpg', 'Rice cooked with daal and veggies and sauteed', 50, true, false, true, 12);
    END IF;


    -- Dish 39: Kadhi and Khichdi
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Kadhi and Khichdi' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Kadhi and Khichdi', '/images/Kadhi%20and%20Khichdi.jpg', 39, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (38 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Kadhi and Khichdi') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Kadhi%20and%20Khichdi.jpg',
            description = 'Khichdi mixed with kadhi, found mostly in Gujarat. Also referred to as khichdi and kadhi, khichdi-kadhi, and kadhi-khichdi.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Kadhi and Khichdi';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Kadhi and Khichdi', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Kadhi%20and%20Khichdi.jpg', 'Khichdi mixed with kadhi, found mostly in Gujarat. Also referred to as khichdi and kadhi, khichdi-kadhi, and kadhi-khichdi.', 50, true, false, true, 12);
    END IF;


    -- Dish 40: Khoya paneer
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Khoya paneer' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Khoya paneer', '/images/Khoya%20paneer.jpg', 40, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (39 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Khoya paneer') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Khoya%20paneer.jpg',
            description = 'cube of paneer cheese in a gravy made of thickened milk (khoya), onion, garlic, ginger, tomato and spices',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Khoya paneer';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Khoya paneer', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Khoya%20paneer.jpg', 'cube of paneer cheese in a gravy made of thickened milk (khoya), onion, garlic, ginger, tomato and spices', 50, true, false, true, 12);
    END IF;


    -- Dish 41: Kofta
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Kofta' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Kofta', '/images/Kofta.jpg', 41, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (40 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Kofta') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Kofta.jpg',
            description = 'Gram flour balls fried with vegetables. Gram flour, veggies, rolled into balls with gram flour and fried in oil and then cooked with curry.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Kofta';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Kofta', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Kofta.jpg', 'Gram flour balls fried with vegetables. Gram flour, veggies, rolled into balls with gram flour and fried in oil and then cooked with curry.', 50, true, false, true, 12);
    END IF;


    -- Dish 42: Kulfi falooda
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Kulfi falooda' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Kulfi falooda', '/images/Kulfi%20falooda.jpg', 42, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (41 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Kulfi falooda') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Kulfi%20falooda.jpg',
            description = 'dessert to ward off sweltering heat of summers',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Kulfi falooda';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Kulfi falooda', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Kulfi%20falooda.jpg', 'dessert to ward off sweltering heat of summers', 50, true, false, true, 12);
    END IF;


    -- Dish 43: Laapsi
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Laapsi' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Laapsi', '/images/Laapsi.jpg', 43, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (42 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Laapsi') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Laapsi.jpg',
            description = 'Dessert made up of broken wheat',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Laapsi';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Laapsi', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Laapsi.jpg', 'Dessert made up of broken wheat', 50, true, false, true, 12);
    END IF;


    -- Dish 44: Lauki ke kofte
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Lauki ke kofte' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Lauki ke kofte', '/images/Lauki%20ke%20kofte.jpg', 44, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (43 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Lauki ke kofte') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Lauki%20ke%20kofte.jpg',
            description = 'a way to serve bottle gourd',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Lauki ke kofte';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Lauki ke kofte', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Lauki%20ke%20kofte.jpg', 'a way to serve bottle gourd', 50, true, false, true, 12);
    END IF;


    -- Dish 45: Litti chokha
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Litti chokha' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Litti chokha', '/images/Litti%20chokha.jpg', 45, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (44 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Litti chokha') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Litti%20chokha.jpg',
            description = 'A baked salted wheat flour cake filled with sattu (baked chickpea flour) and some special spices',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Litti chokha';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Litti chokha', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Litti%20chokha.jpg', 'A baked salted wheat flour cake filled with sattu (baked chickpea flour) and some special spices', 50, true, false, true, 12);
    END IF;


    -- Dish 46: Lobiya
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Lobiya' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Lobiya', '/images/Lobiya.jpg', 46, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (45 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Lobiya') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Lobiya.jpg',
            description = 'Black eyes peas, onions and tomatoes in a curry sauce',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Lobiya';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Lobiya', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Lobiya.jpg', 'Black eyes peas, onions and tomatoes in a curry sauce', 50, true, false, true, 12);
    END IF;


    -- Dish 47: Makhaan ka kheer
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Makhaan ka kheer' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Makhaan ka kheer', '/images/Makhaan%20ka%20kheer.jpg', 47, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (46 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Makhaan ka kheer') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Makhaan%20ka%20kheer.jpg',
            description = 'Sweet, made up with makhana, milk, sugar, cashew and other savor. Popular in Mithilanchal region of Bihar',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Makhaan ka kheer';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Makhaan ka kheer', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Makhaan%20ka%20kheer.jpg', 'Sweet, made up with makhana, milk, sugar, cashew and other savor. Popular in Mithilanchal region of Bihar', 50, true, false, true, 12);
    END IF;


    -- Dish 48: Makki ki roti, sarson ka saag
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Makki ki roti, sarson ka saag' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Makki ki roti, sarson ka saag', '/images/Makki%20ki%20roti%2C%20sarson%20ka%20saag.jpg', 48, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (47 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Makki ki roti, sarson ka saag') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Makki%20ki%20roti%2C%20sarson%20ka%20saag.jpg',
            description = 'Creamed sarson mustard leaves, with heavily buttered roti made from corn flour. North Indian winter favorite.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Makki ki roti, sarson ka saag';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Makki ki roti, sarson ka saag', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Makki%20ki%20roti%2C%20sarson%20ka%20saag.jpg', 'Creamed sarson mustard leaves, with heavily buttered roti made from corn flour. North Indian winter favorite.', 50, true, false, true, 12);
    END IF;


    -- Dish 49: Matar paneer
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Matar paneer' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Matar paneer', '/images/Matar%20paneer.jpg', 49, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (48 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Matar paneer') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Matar%20paneer.jpg',
            description = 'green peas and cube of paneer cheese in a spiced tomato-based sauce',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Matar paneer';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Matar paneer', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Matar%20paneer.jpg', 'green peas and cube of paneer cheese in a spiced tomato-based sauce', 50, true, false, true, 12);
    END IF;


    -- Dish 50: Mathura peda
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Mathura peda' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Mathura peda', '/images/Mathura%20peda.jpg', 50, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (49 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Mathura peda') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Mathura%20peda.jpg',
            description = 'a sort of a confection',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Mathura peda';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Mathura peda', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Mathura%20peda.jpg', 'a sort of a confection', 50, true, false, true, 12);
    END IF;


    -- Dish 51: Mirchi bada
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Mirchi bada' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Mirchi bada', '/images/Mirchi%20bada.jpg', 51, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (50 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Mirchi bada') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Mirchi%20bada.jpg',
            description = 'Green Chili stuffed with mashed potato, coated with besan batter and fried, it is native to Jodhpur.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Mirchi bada';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Mirchi bada', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Mirchi%20bada.jpg', 'Green Chili stuffed with mashed potato, coated with besan batter and fried, it is native to Jodhpur.', 50, true, false, true, 12);
    END IF;


    -- Dish 52: Missi roti
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Missi roti' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Missi roti', '/images/Missi%20roti.jpg', 52, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (51 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Missi roti') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Missi%20roti.jpg',
            description = 'Whole wheat & gram flour dough ground masalas, pan fried',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Missi roti';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Missi roti', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Missi%20roti.jpg', 'Whole wheat & gram flour dough ground masalas, pan fried', 50, true, false, true, 12);
    END IF;


    -- Dish 53: Moong dal ki Lapsi
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Moong dal ki Lapsi' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Moong dal ki Lapsi', '/images/Moong%20dal%20ki%20Lapsi.jpg', 53, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (52 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Moong dal ki Lapsi') THEN
        UPDATE menu_items SET
            price = 60.00,
            original_price = 70.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Moong%20dal%20ki%20Lapsi.jpg',
            description = 'a dish made with yellow lentils, milk, sugar, and nuts',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Moong dal ki Lapsi';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Moong dal ki Lapsi', 60.00, 70.00, 14.29, cat_id, cant_id, '/images/Moong%20dal%20ki%20Lapsi.jpg', 'a dish made with yellow lentils, milk, sugar, and nuts', 50, true, false, true, 12);
    END IF;


    -- Dish 54: Murgh musallam
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Murgh musallam' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Murgh musallam', '/images/Murgh%20musallam.jpg', 54, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (53 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Murgh musallam') THEN
        UPDATE menu_items SET
            price = 140.00,
            original_price = 160.00,
            discount_percent = 12.50,
            category_id = cat_id,
            image_url = '/images/Murgh%20musallam.jpg',
            description = 'Murgh musallam - authentic Indian preparation.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Murgh musallam';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Murgh musallam', 140.00, 160.00, 12.50, cat_id, cant_id, '/images/Murgh%20musallam.jpg', 'Murgh musallam - authentic Indian preparation.', 50, true, false, true, 12);
    END IF;


    -- Dish 55: Naan
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Naan' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Naan', '/images/Naan.jpg', 55, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (54 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Naan') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Naan.jpg',
            description = 'Tandoor-baked soft flatbread made with refined wheat flour.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Naan';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Naan', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Naan.jpg', 'Tandoor-baked soft flatbread made with refined wheat flour.', 50, true, false, true, 12);
    END IF;


    -- Dish 56: Naan Khatai
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Naan Khatai' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Naan Khatai', '/images/Naan%20Khatai.jpg', 56, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (55 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Naan Khatai') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Naan%20Khatai.jpg',
            description = 'Shortbread biscuits',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Naan Khatai';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Naan Khatai', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Naan%20Khatai.jpg', 'Shortbread biscuits', 50, true, false, true, 12);
    END IF;


    -- Dish 57: Navrattan korma
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Navrattan korma' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Navrattan korma', '/images/Navrattan%20korma.jpg', 57, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (56 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Navrattan korma') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Navrattan%20korma.jpg',
            description = 'Vegetables, Nuts, Paneer cheese in a tomato cream sauce',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Navrattan korma';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Navrattan korma', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Navrattan%20korma.jpg', 'Vegetables, Nuts, Paneer cheese in a tomato cream sauce', 50, true, false, true, 12);
    END IF;


    -- Dish 58: Pakhala
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Pakhala' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Pakhala', '/images/Pakhala.jpg', 58, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (57 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Pakhala') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Pakhala.jpg',
            description = 'Cooked rice with water',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Pakhala';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Pakhala', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Pakhala.jpg', 'Cooked rice with water', 50, true, false, true, 12);
    END IF;


    -- Dish 59: Palak paneer
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Palak paneer' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Palak paneer', '/images/Palak%20paneer.jpg', 59, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (58 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Palak paneer') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Palak%20paneer.jpg',
            description = 'fresh spinach leaves (palak) cooked with cubes of paneer cheese in a rich and creamy tomato-based sauce',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Palak paneer';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Palak paneer', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Palak%20paneer.jpg', 'fresh spinach leaves (palak) cooked with cubes of paneer cheese in a rich and creamy tomato-based sauce', 50, true, false, true, 12);
    END IF;


    -- Dish 60: Paneer butter masala, paneer makhani
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Paneer butter masala, paneer makhani' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Paneer butter masala, paneer makhani', '/images/Paneer%20butter%20masala%2C%20paneer%20makhani.jpg', 60, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (59 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Paneer butter masala, paneer makhani') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Paneer%20butter%20masala%2C%20paneer%20makhani.jpg',
            description = 'curry made with soft cubes of paneer cheese in a creamy and aromatic sauce made of butter, tomato sauce, and a blend of spices',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Paneer butter masala, paneer makhani';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Paneer butter masala, paneer makhani', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Paneer%20butter%20masala%2C%20paneer%20makhani.jpg', 'curry made with soft cubes of paneer cheese in a creamy and aromatic sauce made of butter, tomato sauce, and a blend of spices', 50, true, false, true, 12);
    END IF;


    -- Dish 61: Paneer tikka masala
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Paneer tikka masala' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Paneer tikka masala', '/images/Paneer%20tikka%20masala.jpg', 61, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (60 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Paneer tikka masala') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Paneer%20tikka%20masala.jpg',
            description = 'vegetarian alternative to chicken tikka masala, with paneer instead of chicken',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Paneer tikka masala';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Paneer tikka masala', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Paneer%20tikka%20masala.jpg', 'vegetarian alternative to chicken tikka masala, with paneer instead of chicken', 50, true, false, true, 12);
    END IF;


    -- Dish 62: Pani puri
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Pani puri' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Pani puri', '/images/Pani%20puri.jpg', 62, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (61 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Pani puri') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Pani%20puri.jpg',
            description = 'a typical Indian tadka',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Pani puri';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Pani puri', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Pani%20puri.jpg', 'a typical Indian tadka', 50, true, false, true, 12);
    END IF;


    -- Dish 63: Panjeeri
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Panjeeri' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Panjeeri', '/images/Panjeeri.jpg', 63, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (62 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Panjeeri') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Panjeeri.jpg',
            description = 'a mixture of butter, dried fruits and whole wheat flour served as a dessert.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Panjeeri';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Panjeeri', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Panjeeri.jpg', 'a mixture of butter, dried fruits and whole wheat flour served as a dessert.', 50, true, false, true, 12);
    END IF;


    -- Dish 64: Papad
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Papad' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Papad', '/images/Papad.jpg', 64, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (63 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Papad') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Papad.jpg',
            description = 'A crispy add on to Lunch and Dinner, for adding a spicy and crunchier taste to food.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Papad';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Papad', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Papad.jpg', 'A crispy add on to Lunch and Dinner, for adding a spicy and crunchier taste to food.', 50, true, false, true, 12);
    END IF;


    -- Dish 65: Paratha
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Paratha' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Paratha', '/images/Paratha.jpg', 65, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (64 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Paratha') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Paratha.jpg',
            description = 'flatbread native to the Indian subcontinent, prevalent throughout the modern-day nations of India, Sri Lanka, Pakistan, Nepal, Bangladesh, Maldives, and Myanmar, where wheat is the traditional staple',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Paratha';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Paratha', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Paratha.jpg', 'flatbread native to the Indian subcontinent, prevalent throughout the modern-day nations of India, Sri Lanka, Pakistan, Nepal, Bangladesh, Maldives, and Myanmar, where wheat is the traditional staple', 50, true, false, true, 12);
    END IF;


    -- Dish 66: Patrode
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Patrode' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Patrode', '/images/Patrode.jpg', 66, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (65 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Patrode') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Patrode.jpg',
            description = 'A steamed vegetarian dish made from colocasia leaves (chevu in Tulu, taro, kesuve or arbi)',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Patrode';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Patrode', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Patrode.jpg', 'A steamed vegetarian dish made from colocasia leaves (chevu in Tulu, taro, kesuve or arbi)', 50, true, false, true, 12);
    END IF;


    -- Dish 67: Phirni
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Phirni' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Phirni', '/images/Phirni.jpg', 67, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (66 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Phirni') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Phirni.jpg',
            description = 'Sweet rice pudding, cooked in milk, flavoured with cardamom, saffron, and rose water, and garnished with nuts like almonds and pistachios.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Phirni';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Phirni', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Phirni.jpg', 'Sweet rice pudding, cooked in milk, flavoured with cardamom, saffron, and rose water, and garnished with nuts like almonds and pistachios.', 50, true, false, true, 12);
    END IF;


    -- Dish 68: Pinni
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Pinni' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Pinni', '/images/Pinni.jpg', 68, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (67 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Pinni') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Pinni.jpg',
            description = 'A type of Punjabi and North Indian cuisine dish that is eaten mostly in winters. It is served as a dessert and is made from desi ghee, wheat flour, jaggery and almonds. Raisins may also be used.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Pinni';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Pinni', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Pinni.jpg', 'A type of Punjabi and North Indian cuisine dish that is eaten mostly in winters. It is served as a dessert and is made from desi ghee, wheat flour, jaggery and almonds. Raisins may also be used.', 50, true, false, true, 12);
    END IF;


    -- Dish 69: Rajma
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Rajma' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Rajma', '/images/Rajma.jpg', 69, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (68 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Rajma') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Rajma.jpg',
            description = 'Main. Kidney beans & assorted spices.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Rajma';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Rajma', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Rajma.jpg', 'Main. Kidney beans & assorted spices.', 50, true, false, true, 12);
    END IF;


    -- Dish 70: Samosa
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Samosa' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Samosa', '/images/Samosa.jpg', 70, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (69 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Samosa') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Samosa.jpg',
            description = 'Normally served as an entree or appetiser. Potatoes, onions, peas, coriander, and lentils, may be served with a mint or tamarind sauce',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Samosa';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Samosa', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Samosa.jpg', 'Normally served as an entree or appetiser. Potatoes, onions, peas, coriander, and lentils, may be served with a mint or tamarind sauce', 50, true, false, true, 12);
    END IF;


    -- Dish 71: Shahi paneer or Rajwadi Chhena/Paneer
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Shahi paneer or Rajwadi Chhena/Paneer' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Shahi paneer or Rajwadi Chhena/Paneer', '/images/Shahi%20paneer%20or%20Rajwadi%20Chhena-Paneer.jpg', 71, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (70 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Shahi paneer or Rajwadi Chhena/Paneer') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Shahi%20paneer%20or%20Rajwadi%20Chhena-Paneer.jpg',
            description = 'A popular Indian as well as Nepalese dish, made with chhena or paneer in a thick cream and tomato gravy that is sweeter and spicier than paneer makhani',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Shahi paneer or Rajwadi Chhena/Paneer';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Shahi paneer or Rajwadi Chhena/Paneer', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Shahi%20paneer%20or%20Rajwadi%20Chhena-Paneer.jpg', 'A popular Indian as well as Nepalese dish, made with chhena or paneer in a thick cream and tomato gravy that is sweeter and spicier than paneer makhani', 50, true, false, true, 12);
    END IF;


    -- Dish 72: Shahi tukra
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Shahi tukra' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Shahi tukra', '/images/Shahi%20tukra.jpg', 72, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (71 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Shahi tukra') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Shahi%20tukra.jpg',
            description = 'A bread pudding in a rich gravy of thickened milk, garnished with sliced almonds',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Shahi tukra';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Shahi tukra', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Shahi%20tukra.jpg', 'A bread pudding in a rich gravy of thickened milk, garnished with sliced almonds', 50, true, false, true, 12);
    END IF;


    -- Dish 73: Sooji halwa (Suji Lapsi)
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Sooji halwa (Suji Lapsi)' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Sooji halwa (Suji Lapsi)', '/images/Sooji%20halwa%20%28Suji%20Lapsi%29.jpg', 73, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (72 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Sooji halwa (Suji Lapsi)') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Sooji%20halwa%20%28Suji%20Lapsi%29.jpg',
            description = 'Semolina cooked with clarified butter and dry fruits. Semolina (Suji), clarified butter, cashew nuts.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Sooji halwa (Suji Lapsi)';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Sooji halwa (Suji Lapsi)', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Sooji%20halwa%20%28Suji%20Lapsi%29.jpg', 'Semolina cooked with clarified butter and dry fruits. Semolina (Suji), clarified butter, cashew nuts.', 50, true, false, true, 12);
    END IF;


    -- Dish 74: Tamatar Chaat
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Tamatar Chaat' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Tamatar Chaat', '/images/Tamatar%20Chaat.jpg', 74, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (73 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Tamatar Chaat') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Tamatar%20Chaat.jpg',
            description = 'Tamatar Chaat is an Indian street food which is most popular in north India specially in Varanasi.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Tamatar Chaat';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Tamatar Chaat', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Tamatar%20Chaat.jpg', 'Tamatar Chaat is an Indian street food which is most popular in north India specially in Varanasi.', 50, true, false, true, 12);
    END IF;


    -- Dish 75: Tandoori Chicken
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Tandoori Chicken' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Tandoori Chicken', '/images/Tandoori%20Chicken.jpg', 75, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (74 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Tandoori Chicken') THEN
        UPDATE menu_items SET
            price = 140.00,
            original_price = 160.00,
            discount_percent = 12.50,
            category_id = cat_id,
            image_url = '/images/Tandoori%20Chicken.jpg',
            description = 'Tandoori chicken as a dish originated in the Punjab before the independence of India and Pakistan.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Tandoori Chicken';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Tandoori Chicken', 140.00, 160.00, 12.50, cat_id, cant_id, '/images/Tandoori%20Chicken.jpg', 'Tandoori chicken as a dish originated in the Punjab before the independence of India and Pakistan.', 50, true, false, true, 12);
    END IF;


    -- Dish 76: Tandoori Fish Tikka
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Tandoori Fish Tikka' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Tandoori Fish Tikka', '/images/Tandoori%20Fish%20Tikka.jpg', 76, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (75 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Tandoori Fish Tikka') THEN
        UPDATE menu_items SET
            price = 140.00,
            original_price = 160.00,
            discount_percent = 12.50,
            category_id = cat_id,
            image_url = '/images/Tandoori%20Fish%20Tikka.jpg',
            description = 'Fish marinated in lime and ginger and cooked over an open fire.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Tandoori Fish Tikka';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Tandoori Fish Tikka', 140.00, 160.00, 12.50, cat_id, cant_id, '/images/Tandoori%20Fish%20Tikka.jpg', 'Fish marinated in lime and ginger and cooked over an open fire.', 50, true, false, true, 12);
    END IF;


    -- Dish 77: Ananas menaskai
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Ananas menaskai' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Ananas menaskai', '/images/Ananas%20menaskai.jpg', 77, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (76 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Ananas menaskai') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Ananas%20menaskai.jpg',
            description = 'Pineapple cooked in jaggery and tamarind gravy',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Ananas menaskai';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Ananas menaskai', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Ananas%20menaskai.jpg', 'Pineapple cooked in jaggery and tamarind gravy', 50, true, false, true, 12);
    END IF;


    -- Dish 78: Kesari bat
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Kesari bat' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Kesari bat', '/images/Kesari%20bat.jpg', 78, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (77 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Kesari bat') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Kesari%20bat.jpg',
            description = 'Roasted flat rice flour cooked with sugar and dry fruits.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Kesari bat';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Kesari bat', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Kesari%20bat.jpg', 'Roasted flat rice flour cooked with sugar and dry fruits.', 50, true, false, true, 12);
    END IF;


    -- Dish 79: Avial
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Avial' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Avial', '/images/Avial.jpg', 79, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (78 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Avial') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Avial.jpg',
            description = 'Coconut paste, curd mixed with vegetables and some spices.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Avial';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Avial', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Avial.jpg', 'Coconut paste, curd mixed with vegetables and some spices.', 50, true, false, true, 12);
    END IF;


    -- Dish 80: Baida roti
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Baida roti' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Baida roti', '/images/Baida%20roti.jpg', 80, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (79 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Baida roti') THEN
        UPDATE menu_items SET
            price = 140.00,
            original_price = 160.00,
            discount_percent = 12.50,
            category_id = cat_id,
            image_url = '/images/Baida%20roti.jpg',
            description = 'fried minced chicken stuffed in Egg roll',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Baida roti';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Baida roti', 140.00, 160.00, 12.50, cat_id, cant_id, '/images/Baida%20roti.jpg', 'fried minced chicken stuffed in Egg roll', 50, true, false, true, 12);
    END IF;


    -- Dish 81: Bhajji
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Bhajji' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Bhajji', '/images/Bhajji.jpg', 81, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (80 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Bhajji') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Bhajji.jpg',
            description = 'Vegetable or onion fritters which are known as Pakodas in North India and Pakistani cuisine',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Bhajji';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Bhajji', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Bhajji.jpg', 'Vegetable or onion fritters which are known as Pakodas in North India and Pakistani cuisine', 50, true, false, true, 12);
    END IF;


    -- Dish 82: Bisi bele bath (Karnataka)
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Bisi bele bath (Karnataka)' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Bisi bele bath (Karnataka)', '/images/Bisi%20bele%20bath%20%28Karnataka%29.jpg', 82, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (81 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Bisi bele bath (Karnataka)') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Bisi%20bele%20bath%20%28Karnataka%29.jpg',
            description = 'Rice preparation with vegetables.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Bisi bele bath (Karnataka)';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Bisi bele bath (Karnataka)', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Bisi%20bele%20bath%20%28Karnataka%29.jpg', 'Rice preparation with vegetables.', 50, true, false, true, 12);
    END IF;


    -- Dish 83: Bonda
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Bonda' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Bonda', '/images/Bonda.jpg', 83, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (82 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Bonda') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Bonda.jpg',
            description = 'Potatoes, gram flour.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Bonda';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Bonda', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Bonda.jpg', 'Potatoes, gram flour.', 50, true, false, true, 12);
    END IF;


    -- Dish 84: Chettinadu Chicken
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Chettinadu Chicken' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Chettinadu Chicken', '/images/Chettinadu%20Chicken.jpg', 84, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (83 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Chettinadu Chicken') THEN
        UPDATE menu_items SET
            price = 140.00,
            original_price = 160.00,
            discount_percent = 12.50,
            category_id = cat_id,
            image_url = '/images/Chettinadu%20Chicken.jpg',
            description = 'Dish made chicken and spices',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Chettinadu Chicken';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Chettinadu Chicken', 140.00, 160.00, 12.50, cat_id, cant_id, '/images/Chettinadu%20Chicken.jpg', 'Dish made chicken and spices', 50, true, false, true, 12);
    END IF;


    -- Dish 85: Chicken 65
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Chicken 65' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Chicken 65', '/images/Chicken%2065.jpg', 85, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (84 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Chicken 65') THEN
        UPDATE menu_items SET
            price = 140.00,
            original_price = 160.00,
            discount_percent = 12.50,
            category_id = cat_id,
            image_url = '/images/Chicken%2065.jpg',
            description = 'Popular deep fried chicken preparation. Chicken, onion, ginger',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Chicken 65';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Chicken 65', 140.00, 160.00, 12.50, cat_id, cant_id, '/images/Chicken%2065.jpg', 'Popular deep fried chicken preparation. Chicken, onion, ginger', 50, true, false, true, 12);
    END IF;


    -- Dish 86: Dosa
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Dosa' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Dosa', '/images/Dosa.jpg', 86, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (85 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Dosa') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Dosa.jpg',
            description = 'Pancake/Hopper. Ground rice, urad dal',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Dosa';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Dosa', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Dosa.jpg', 'Pancake/Hopper. Ground rice, urad dal', 50, true, false, true, 12);
    END IF;


    -- Dish 87: Double ka meetha
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Double ka meetha' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Double ka meetha', '/images/Double%20ka%20meetha.jpg', 87, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (86 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Double ka meetha') THEN
        UPDATE menu_items SET
            price = 60.00,
            original_price = 70.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Double%20ka%20meetha.jpg',
            description = 'Bread crumbs fried in ghee and dipped in milk and sugar syrup',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Double ka meetha';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Double ka meetha', 60.00, 70.00, 14.29, cat_id, cant_id, '/images/Double%20ka%20meetha.jpg', 'Bread crumbs fried in ghee and dipped in milk and sugar syrup', 50, true, false, true, 12);
    END IF;


    -- Dish 88: Idiyappam
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Idiyappam' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Idiyappam', '/images/Idiyappam.jpg', 88, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (87 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Idiyappam') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Idiyappam.jpg',
            description = 'Steamed rice noodles or vermicelli with Ground rice',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Idiyappam';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Idiyappam', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Idiyappam.jpg', 'Steamed rice noodles or vermicelli with Ground rice', 50, true, false, true, 12);
    END IF;


    -- Dish 89: Idli
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Idli' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Idli', '/images/Idli.jpg', 89, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (88 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Idli') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Idli.jpg',
            description = 'Steamed cake of fermented rice and pulse flour. Rice, urad dal',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Idli';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Idli', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Idli.jpg', 'Steamed cake of fermented rice and pulse flour. Rice, urad dal', 50, true, false, true, 12);
    END IF;


    -- Dish 90: Indian omelette
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Indian omelette' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Indian omelette', '/images/Indian%20omelette.jpg', 90, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (89 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Indian omelette') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Indian%20omelette.jpg',
            description = 'Egg omelette or veg omelette',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Indian omelette';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Indian omelette', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Indian%20omelette.jpg', 'Egg omelette or veg omelette', 50, true, false, true, 12);
    END IF;


    -- Dish 91: Kanji
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Kanji' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Kanji', '/images/Kanji.jpg', 91, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (90 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Kanji') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Kanji.jpg',
            description = 'a rice porridge',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Kanji';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Kanji', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Kanji.jpg', 'a rice porridge', 50, true, false, true, 12);
    END IF;


    -- Dish 92: Kerala Beef Fry
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Kerala Beef Fry' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Kerala Beef Fry', '/images/Kerala%20Beef%20Fry.jpg', 92, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (91 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Kerala Beef Fry') THEN
        UPDATE menu_items SET
            price = 140.00,
            original_price = 160.00,
            discount_percent = 12.50,
            category_id = cat_id,
            image_url = '/images/Kerala%20Beef%20Fry.jpg',
            description = 'Beef, onions, spices, coconut, curry leaves',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Kerala Beef Fry';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Kerala Beef Fry', 140.00, 160.00, 12.50, cat_id, cant_id, '/images/Kerala%20Beef%20Fry.jpg', 'Beef, onions, spices, coconut, curry leaves', 50, true, false, true, 12);
    END IF;


    -- Dish 93: Koottu
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Koottu' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Koottu', '/images/Koottu.jpg', 93, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (92 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Koottu') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Koottu.jpg',
            description = 'Vegetable, daal or lentil mixture boiled in water',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Koottu';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Koottu', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Koottu.jpg', 'Vegetable, daal or lentil mixture boiled in water', 50, true, false, true, 12);
    END IF;


    -- Dish 94: Kuzhakkattai
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Kuzhakkattai' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Kuzhakkattai', '/images/Kuzhakkattai.jpg', 94, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (93 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Kuzhakkattai') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Kuzhakkattai.jpg',
            description = 'Dumplings with Rice flour, jaggery, and coconut',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Kuzhakkattai';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Kuzhakkattai', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Kuzhakkattai.jpg', 'Dumplings with Rice flour, jaggery, and coconut', 50, true, false, true, 12);
    END IF;


    -- Dish 95: Masala Dosa
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Masala Dosa' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Masala Dosa', '/images/Masala%20Dosa.jpg', 95, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (94 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Masala Dosa') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Masala%20Dosa.jpg',
            description = 'Dosa with masala and potato.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Masala Dosa';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Masala Dosa', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Masala%20Dosa.jpg', 'Dosa with masala and potato.', 50, true, false, true, 12);
    END IF;


    -- Dish 96: Obbattu (holige, bobbattu, pooran-poli)
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Obbattu (holige, bobbattu, pooran-poli)' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Obbattu (holige, bobbattu, pooran-poli)', '/images/Obbattu%20%28holige%2C%20bobbattu%2C%20pooran-poli%29.jpg', 96, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (95 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Obbattu (holige, bobbattu, pooran-poli)') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Obbattu%20%28holige%2C%20bobbattu%2C%20pooran-poli%29.jpg',
            description = 'A stuffed (moong gram dal and jaggery or coconut poornam) paratha. Dish native to South and West India in the states of |- Karnataka, Andhra Pradesh and Maharashtra || Vegetarian|| Festival Sweet dish',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Obbattu (holige, bobbattu, pooran-poli)';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Obbattu (holige, bobbattu, pooran-poli)', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Obbattu%20%28holige%2C%20bobbattu%2C%20pooran-poli%29.jpg', 'A stuffed (moong gram dal and jaggery or coconut poornam) paratha. Dish native to South and West India in the states of |- Karnataka, Andhra Pradesh and Maharashtra || Vegetarian|| Festival Sweet dish', 50, true, false, true, 12);
    END IF;


    -- Dish 97: Olan (dish)
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Olan (dish)' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Olan (dish)', '/images/Olan%20%28dish%29.jpg', 97, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (96 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Olan (dish)') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Olan%20%28dish%29.jpg',
            description = 'Light and subtle-flavored Kerala dish prepared from white gourd, ash-gourd or black-eyed peas, coconut milk and ginger seasoned with coconut oil.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Olan (dish)';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Olan (dish)', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Olan%20%28dish%29.jpg', 'Light and subtle-flavored Kerala dish prepared from white gourd, ash-gourd or black-eyed peas, coconut milk and ginger seasoned with coconut oil.', 50, true, false, true, 12);
    END IF;


    -- Dish 98: Papadum
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Papadum' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Papadum', '/images/Papadum.jpg', 98, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (97 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Papadum') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Papadum.jpg',
            description = 'Thin deep fried disk served as meal accompaniment',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Papadum';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Papadum', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Papadum.jpg', 'Thin deep fried disk served as meal accompaniment', 50, true, false, true, 12);
    END IF;


    -- Dish 99: Parotta
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Parotta' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Parotta', '/images/Parotta.jpg', 99, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (98 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Parotta') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Parotta.jpg',
            description = 'a layered kerala parotta made with maida and dalda.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Parotta';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Parotta', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Parotta.jpg', 'a layered kerala parotta made with maida and dalda.', 50, true, false, true, 12);
    END IF;


    -- Dish 100: Payasam
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Payasam' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Payasam', '/images/Payasam.jpg', 100, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (99 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Payasam') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Payasam.jpg',
            description = 'Rice dessert. Rice, milk.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Payasam';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Payasam', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Payasam.jpg', 'Rice dessert. Rice, milk.', 50, true, false, true, 12);
    END IF;


    -- Dish 101: Pesarattu
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Pesarattu' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Pesarattu', '/images/Pesarattu.jpg', 101, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (100 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Pesarattu') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Pesarattu.jpg',
            description = 'Dosa (pancake or crepe) of Andhra Pradesh made from moong dal (lentils), grains and spice batter.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Pesarattu';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Pesarattu', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Pesarattu.jpg', 'Dosa (pancake or crepe) of Andhra Pradesh made from moong dal (lentils), grains and spice batter.', 50, true, false, true, 12);
    END IF;


    -- Dish 102: Pongal
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Pongal' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Pongal', '/images/Pongal.jpg', 102, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (101 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Pongal') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Pongal.jpg',
            description = 'Pulao',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Pongal';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Pongal', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Pongal.jpg', 'Pulao', 50, true, false, true, 12);
    END IF;


    -- Dish 103: Puttu
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Puttu' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Puttu', '/images/Puttu.jpg', 103, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (102 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Puttu') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Puttu.jpg',
            description = 'Ground rice, jaggery, cardamom powder, mixed and steam cooked',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Puttu';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Puttu', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Puttu.jpg', 'Ground rice, jaggery, cardamom powder, mixed and steam cooked', 50, true, false, true, 12);
    END IF;


    -- Dish 104: Sambar
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Sambar' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Sambar', '/images/Sambar.jpg', 104, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (103 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Sambar') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Sambar.jpg',
            description = 'Lentil soup cooked with vegetables and a blend of south Indian spices (masala). Usually taken with rice, idli, dosa, pongal or upma.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Sambar';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Sambar', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Sambar.jpg', 'Lentil soup cooked with vegetables and a blend of south Indian spices (masala). Usually taken with rice, idli, dosa, pongal or upma.', 50, true, false, true, 12);
    END IF;


    -- Dish 105: Sandige (Karnataka), Vattral
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Sandige (Karnataka), Vattral' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Sandige (Karnataka), Vattral', '/images/Sandige%20%28Karnataka%29%2C%20Vattral.jpg', 105, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (104 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Sandige (Karnataka), Vattral') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Sandige%20%28Karnataka%29%2C%20Vattral.jpg',
            description = 'Deep fried meal accompaniment made with rice, sago and ash gourd',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Sandige (Karnataka), Vattral';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Sandige (Karnataka), Vattral', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Sandige%20%28Karnataka%29%2C%20Vattral.jpg', 'Deep fried meal accompaniment made with rice, sago and ash gourd', 50, true, false, true, 12);
    END IF;


    -- Dish 106: Sevai
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Sevai' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Sevai', '/images/Sevai.jpg', 106, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (105 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Sevai') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Sevai.jpg',
            description = 'Kind of rice vermicelli used for breakfast',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Sevai';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Sevai', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Sevai.jpg', 'Kind of rice vermicelli used for breakfast', 50, true, false, true, 12);
    END IF;


    -- Dish 107: Sponge dosa
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Sponge dosa' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Sponge dosa', '/images/Sponge%20dosa.jpg', 107, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (106 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Sponge dosa') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Sponge%20dosa.jpg',
            description = 'dosa made of fermented poha and rice',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Sponge dosa';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Sponge dosa', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Sponge%20dosa.jpg', 'dosa made of fermented poha and rice', 50, true, false, true, 12);
    END IF;


    -- Dish 108: Thattai
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Thattai' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Thattai', '/images/Thattai.jpg', 108, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (107 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Thattai') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Thattai.jpg',
            description = 'Type of puri made with rice, gram, urad dal flour',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Thattai';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Thattai', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Thattai.jpg', 'Type of puri made with rice, gram, urad dal flour', 50, true, false, true, 12);
    END IF;


    -- Dish 109: Thayir sadam, mosaranna, perugannam
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Thayir sadam, mosaranna, perugannam' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Thayir sadam, mosaranna, perugannam', '/images/Thayir%20sadam%2C%20mosaranna%2C%20perugannam.jpg', 109, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (108 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Thayir sadam, mosaranna, perugannam') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Thayir%20sadam%2C%20mosaranna%2C%20perugannam.jpg',
            description = 'a curd rice dish',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Thayir sadam, mosaranna, perugannam';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Thayir sadam, mosaranna, perugannam', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Thayir%20sadam%2C%20mosaranna%2C%20perugannam.jpg', 'a curd rice dish', 50, true, false, true, 12);
    END IF;


    -- Dish 110: Uttapam Tamil Nadu
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Uttapam Tamil Nadu' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Uttapam Tamil Nadu', '/images/Uttapam%20Tamil%20Nadu.jpg', 110, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (109 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Uttapam Tamil Nadu') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Uttapam%20Tamil%20Nadu.jpg',
            description = 'Rice pancake/hopper with a topping of onions / tomatoes / coconut',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Uttapam Tamil Nadu';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Uttapam Tamil Nadu', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Uttapam%20Tamil%20Nadu.jpg', 'Rice pancake/hopper with a topping of onions / tomatoes / coconut', 50, true, false, true, 12);
    END IF;


    -- Dish 111: Vada
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Vada' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Vada', '/images/Vada.jpg', 111, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (110 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Vada') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Vada.jpg',
            description = 'Savory donut. Urad dal.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Vada';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Vada', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Vada.jpg', 'Savory donut. Urad dal.', 50, true, false, true, 12);
    END IF;


    -- Dish 112: Wheat upma, Uppittu
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Wheat upma, Uppittu' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Wheat upma, Uppittu', '/images/Wheat%20upma%2C%20Uppittu.jpg', 112, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (111 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Wheat upma, Uppittu') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Wheat%20upma%2C%20Uppittu.jpg',
            description = 'A breakfast dish and snack. Upma prepared from wheat dhalia rava.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Wheat upma, Uppittu';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Wheat upma, Uppittu', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Wheat%20upma%2C%20Uppittu.jpg', 'A breakfast dish and snack. Upma prepared from wheat dhalia rava.', 50, true, false, true, 12);
    END IF;


    -- Dish 113: Barfi
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Barfi' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Barfi', '/images/Barfi.jpg', 113, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (112 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Barfi') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Barfi.jpg',
            description = 'Sweet',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Barfi';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Barfi', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Barfi.jpg', 'Sweet', 50, true, false, true, 12);
    END IF;


    -- Dish 114: Bhakri
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Bhakri' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Bhakri', '/images/Bhakri.jpg', 114, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (113 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Bhakri') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Bhakri.jpg',
            description = 'Whole wheat flour bread, thicker than rotli, crispy.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Bhakri';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Bhakri', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Bhakri.jpg', 'Whole wheat flour bread, thicker than rotli, crispy.', 50, true, false, true, 12);
    END IF;


    -- Dish 115: Bombil fry
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Bombil fry' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Bombil fry', '/images/Bombil%20fry.jpg', 115, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (114 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Bombil fry') THEN
        UPDATE menu_items SET
            price = 140.00,
            original_price = 160.00,
            discount_percent = 12.50,
            category_id = cat_id,
            image_url = '/images/Bombil%20fry.jpg',
            description = 'Main Course; Bombay Duck (Fish).',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Bombil fry';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Bombil fry', 140.00, 160.00, 12.50, cat_id, cant_id, '/images/Bombil%20fry.jpg', 'Main Course; Bombay Duck (Fish).', 50, true, false, true, 12);
    END IF;


    -- Dish 116: Chaat
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Chaat' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Chaat', '/images/Chaat_2.jpg', 116, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (115 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Chaat') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Chaat_2.jpg',
            description = 'Snack',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Chaat';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Chaat', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Chaat_2.jpg', 'Snack', 50, true, false, true, 12);
    END IF;


    -- Dish 117: Chevdo
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Chevdo' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Chevdo', '/images/Chevdo.jpg', 117, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (116 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Chevdo') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Chevdo.jpg',
            description = 'Mixture of Flattened rice, groundnut, chana, masala.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Chevdo';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Chevdo', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Chevdo.jpg', 'Mixture of Flattened rice, groundnut, chana, masala.', 50, true, false, true, 12);
    END IF;


    -- Dish 118: Dabeli
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Dabeli' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Dabeli', '/images/Dabeli.jpg', 118, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (117 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Dabeli') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Dabeli.jpg',
            description = 'Snack made by mixing boiled potatoes with a special dabeli masala, putting the mixture in a ladi pav',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Dabeli';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Dabeli', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Dabeli.jpg', 'Snack made by mixing boiled potatoes with a special dabeli masala, putting the mixture in a ladi pav', 50, true, false, true, 12);
    END IF;


    -- Dish 119: Dahi vada
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Dahi vada' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Dahi vada', '/images/Dahi%20vada.jpg', 119, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (118 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Dahi vada') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Dahi%20vada.jpg',
            description = 'Fried lentil balls in a yogurt sauce. Lentils, yogurt.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Dahi vada';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Dahi vada', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Dahi%20vada.jpg', 'Fried lentil balls in a yogurt sauce. Lentils, yogurt.', 50, true, false, true, 12);
    END IF;


    -- Dish 120: Dhokla
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Dhokla' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Dhokla', '/images/Dhokla.jpg', 120, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (119 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Dhokla') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Dhokla.jpg',
            description = 'Lentil snack. Gram.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Dhokla';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Dhokla', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Dhokla.jpg', 'Lentil snack. Gram.', 50, true, false, true, 12);
    END IF;


    -- Dish 121: Dum aaloo
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Dum aaloo' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Dum aaloo', '/images/Dum%20aaloo.jpg', 121, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (120 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Dum aaloo') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Dum%20aaloo.jpg',
            description = 'Main dish. Potatoes deep fry, yogurt, coriander powder, ginger powder.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Dum aaloo';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Dum aaloo', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Dum%20aaloo.jpg', 'Main dish. Potatoes deep fry, yogurt, coriander powder, ginger powder.', 50, true, false, true, 12);
    END IF;


    -- Dish 122: Gajar halwo
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Gajar halwo' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Gajar halwo', '/images/Gajar%20halwo.jpg', 122, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (121 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Gajar halwo') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Gajar%20halwo.jpg',
            description = 'Sweet. Carrot Halwa',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Gajar halwo';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Gajar halwo', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Gajar%20halwo.jpg', 'Sweet. Carrot Halwa', 50, true, false, true, 12);
    END IF;


    -- Dish 123: Gulab jamun
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Gulab jamun' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Gulab jamun', '/images/Gulab%20jamun.jpg', 123, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (122 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Gulab jamun') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Gulab%20jamun.jpg',
            description = 'Sweet',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Gulab jamun';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Gulab jamun', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Gulab%20jamun.jpg', 'Sweet', 50, true, false, true, 12);
    END IF;


    -- Dish 124: Gur
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Gur' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Gur', '/images/Gur.jpg', 124, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (123 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Gur') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Gur.jpg',
            description = 'Sweet unrefined brown sugar sold in blocks.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Gur';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Gur', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Gur.jpg', 'Sweet unrefined brown sugar sold in blocks.', 50, true, false, true, 12);
    END IF;


    -- Dish 125: Jalebi
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Jalebi' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Jalebi', '/images/Jalebi_2.jpg', 125, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (124 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Jalebi') THEN
        UPDATE menu_items SET
            price = 60.00,
            original_price = 70.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Jalebi_2.jpg',
            description = 'Sweet maida & grained semolina flour, baking powder, curd, sugar.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Jalebi';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Jalebi', 60.00, 70.00, 14.29, cat_id, cant_id, '/images/Jalebi_2.jpg', 'Sweet maida & grained semolina flour, baking powder, curd, sugar.', 50, true, false, true, 12);
    END IF;


    -- Dish 126: Jeera Aloo
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Jeera Aloo' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Jeera Aloo', '/images/Jeera%20Aloo.jpg', 126, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (125 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Jeera Aloo') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Jeera%20Aloo.jpg',
            description = 'Typical West Indian dish',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Jeera Aloo';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Jeera Aloo', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Jeera%20Aloo.jpg', 'Typical West Indian dish', 50, true, false, true, 12);
    END IF;


    -- Dish 127: Khakhra
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Khakhra' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Khakhra', '/images/Khakhra.jpg', 127, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (126 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Khakhra') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Khakhra.jpg',
            description = 'Gujarati Snack. Wheat flour, methi.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Khakhra';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Khakhra', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Khakhra.jpg', 'Gujarati Snack. Wheat flour, methi.', 50, true, false, true, 12);
    END IF;


    -- Dish 128: Khandvi
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Khandvi' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Khandvi', '/images/Khandvi.jpg', 128, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (127 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Khandvi') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Khandvi.jpg',
            description = 'Snack. Besan.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Khandvi';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Khandvi', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Khandvi.jpg', 'Snack. Besan.', 50, true, false, true, 12);
    END IF;


    -- Dish 129: Kombdi vade
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Kombdi vade' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Kombdi vade', '/images/Kombdi%20vade.jpg', 129, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (128 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Kombdi vade') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Kombdi%20vade.jpg',
            description = 'Chicken Curry with Bread. Chicken.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Kombdi vade';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Kombdi vade', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Kombdi%20vade.jpg', 'Chicken Curry with Bread. Chicken.', 50, true, false, true, 12);
    END IF;


    -- Dish 130: Laddu
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Laddu' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Laddu', '/images/Laddu.jpg', 130, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (129 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Laddu') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Laddu.jpg',
            description = 'Sweet',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Laddu';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Laddu', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Laddu.jpg', 'Sweet', 50, true, false, true, 12);
    END IF;


    -- Dish 131: Malpua
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Malpua' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Malpua', '/images/Malpua.jpg', 131, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (130 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Malpua') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Malpua.jpg',
            description = 'Sweet',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Malpua';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Malpua', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Malpua.jpg', 'Sweet', 50, true, false, true, 12);
    END IF;


    -- Dish 132: Chakri (chakali)
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Chakri (chakali)' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Chakri (chakali)', '/images/Chakri%20%28chakali%29.jpg', 132, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (131 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Chakri (chakali)') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Chakri%20%28chakali%29.jpg',
            description = 'a Savoury snack. Mixed grain flour.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Chakri (chakali)';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Chakri (chakali)', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Chakri%20%28chakali%29.jpg', 'a Savoury snack. Mixed grain flour.', 50, true, false, true, 12);
    END IF;


    -- Dish 133: Panipuri
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Panipuri' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Panipuri', '/images/Panipuri.jpg', 133, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (132 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Panipuri') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Panipuri.jpg',
            description = 'Snack',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Panipuri';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Panipuri', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Panipuri.jpg', 'Snack', 50, true, false, true, 12);
    END IF;


    -- Dish 134: Pav Bhaji
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Pav Bhaji' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Pav Bhaji', '/images/Pav%20Bhaji.jpg', 134, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (133 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Pav Bhaji') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Pav%20Bhaji.jpg',
            description = 'Mixed curry of onion, capsicum, peas, cauliflower potatoes.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Pav Bhaji';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Pav Bhaji', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Pav%20Bhaji.jpg', 'Mixed curry of onion, capsicum, peas, cauliflower potatoes.', 50, true, false, true, 12);
    END IF;


    -- Dish 135: Pooran-poli
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Pooran-poli' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Pooran-poli', '/images/Pooran-poli.jpg', 135, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (134 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Pooran-poli') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Pooran-poli.jpg',
            description = 'Sweet stuffed bread. Wheat flour, gram.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Pooran-poli';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Pooran-poli', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Pooran-poli.jpg', 'Sweet stuffed bread. Wheat flour, gram.', 50, true, false, true, 12);
    END IF;


    -- Dish 136: Poori
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Poori' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Poori', '/images/Poori.jpg', 136, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (135 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Poori') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Poori.jpg',
            description = 'Bread. Wheat flour.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Poori';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Poori', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Poori.jpg', 'Bread. Wheat flour.', 50, true, false, true, 12);
    END IF;


    -- Dish 137: Puri Bhaji
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Puri Bhaji' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Puri Bhaji', '/images/Puri%20Bhaji.jpg', 137, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (136 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Puri Bhaji') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Puri%20Bhaji.jpg',
            description = 'Breakfast or Snack',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Puri Bhaji';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Puri Bhaji', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Puri%20Bhaji.jpg', 'Breakfast or Snack', 50, true, false, true, 12);
    END IF;


    -- Dish 138: Shankarpali
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Shankarpali' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Shankarpali', '/images/Shankarpali.jpg', 138, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (137 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Shankarpali') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Shankarpali.jpg',
            description = 'Sweet or savoury snack. Plain flour, sugar.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Shankarpali';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Shankarpali', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Shankarpali.jpg', 'Sweet or savoury snack. Plain flour, sugar.', 50, true, false, true, 12);
    END IF;


    -- Dish 139: Shiro
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Shiro' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Shiro', '/images/Shiro.jpg', 139, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (138 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Shiro') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Shiro.jpg',
            description = 'Sweet roasted semolina/flour/dal with milk, butter, sugar, nuts and raisins.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Shiro';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Shiro', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Shiro.jpg', 'Sweet roasted semolina/flour/dal with milk, butter, sugar, nuts and raisins.', 50, true, false, true, 12);
    END IF;


    -- Dish 140: Shrikhand
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Shrikhand' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Shrikhand', '/images/Shrikhand.jpg', 140, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (139 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Shrikhand') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Shrikhand.jpg',
            description = 'A thick yogurt-based sweet dessert garnished with ground nuts, cardamom, and saffron.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Shrikhand';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Shrikhand', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Shrikhand.jpg', 'A thick yogurt-based sweet dessert garnished with ground nuts, cardamom, and saffron.', 50, true, false, true, 12);
    END IF;


    -- Dish 141: Sohan papdi
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Sohan papdi' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Sohan papdi', '/images/Sohan%20papdi.jpg', 141, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (140 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Sohan papdi') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Sohan%20papdi.jpg',
            description = 'Sweet',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Sohan papdi';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Sohan papdi', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Sohan%20papdi.jpg', 'Sweet', 50, true, false, true, 12);
    END IF;


    -- Dish 142: Sukhdi
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Sukhdi' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Sukhdi', '/images/Sukhdi.jpg', 142, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (141 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Sukhdi') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Sukhdi.jpg',
            description = 'Sweet',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Sukhdi';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Sukhdi', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Sukhdi.jpg', 'Sweet', 50, true, false, true, 12);
    END IF;


    -- Dish 143: Upmaa
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Upmaa' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Upmaa', '/images/Upmaa.jpg', 143, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (142 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Upmaa') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Upmaa.jpg',
            description = 'a dish originating from the Indian subcontinent, cooked as a thick porridge from dry-roasted semolina or coarse rice flour.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Upmaa';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Upmaa', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Upmaa.jpg', 'a dish originating from the Indian subcontinent, cooked as a thick porridge from dry-roasted semolina or coarse rice flour.', 50, true, false, true, 12);
    END IF;


    -- Dish 144: Vada pav
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Vada pav' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Vada pav', '/images/Vada%20pav.jpg', 144, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (143 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Vada pav') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Vada%20pav.jpg',
            description = 'Burger. Gram flour, potatoes, chilli, garlic, ginger.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Vada pav';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Vada pav', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Vada%20pav.jpg', 'Burger. Gram flour, potatoes, chilli, garlic, ginger.', 50, true, false, true, 12);
    END IF;


    -- Dish 145: Vindaloo
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Vindaloo' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Vindaloo', '/images/Vindaloo.jpg', 145, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (144 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Vindaloo') THEN
        UPDATE menu_items SET
            price = 140.00,
            original_price = 160.00,
            discount_percent = 12.50,
            category_id = cat_id,
            image_url = '/images/Vindaloo.jpg',
            description = 'Goan pork vindaloo. Pork, goan red chilli paste.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Vindaloo';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Vindaloo', 140.00, 160.00, 12.50, cat_id, cant_id, '/images/Vindaloo.jpg', 'Goan pork vindaloo. Pork, goan red chilli paste.', 50, true, false, true, 12);
    END IF;


    -- Dish 146: Ghebar or Ghevar
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Ghebar or Ghevar' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Ghebar or Ghevar', '/images/Ghebar%20or%20Ghevar.jpg', 146, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (145 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Ghebar or Ghevar') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Ghebar%20or%20Ghevar.jpg',
            description = 'Sweet from Surat',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Ghebar or Ghevar';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Ghebar or Ghevar', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Ghebar%20or%20Ghevar.jpg', 'Sweet from Surat', 50, true, false, true, 12);
    END IF;


    -- Dish 147: Lilva Kachori
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Lilva Kachori' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Lilva Kachori', '/images/Lilva%20Kachori.jpg', 147, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (146 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Lilva Kachori') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Lilva%20Kachori.jpg',
            description = 'Snack. Lilva and whole wheat flour.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Lilva Kachori';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Lilva Kachori', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Lilva%20Kachori.jpg', 'Snack. Lilva and whole wheat flour.', 50, true, false, true, 12);
    END IF;


    -- Dish 148: Maghaz
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Maghaz' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Maghaz', '/images/Maghaz.jpg', 148, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (147 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Maghaz') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Maghaz.jpg',
            description = 'Maghaz - authentic Indian preparation.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Maghaz';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Maghaz', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Maghaz.jpg', 'Maghaz - authentic Indian preparation.', 50, true, false, true, 12);
    END IF;


    -- Dish 149: Daab chingri
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Daab chingri' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Daab chingri', '/images/Daab%20chingri.jpg', 149, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (148 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Daab chingri') THEN
        UPDATE menu_items SET
            price = 140.00,
            original_price = 160.00,
            discount_percent = 12.50,
            category_id = cat_id,
            image_url = '/images/Daab%20chingri.jpg',
            description = 'Prawn curry cooked in green coconut.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Daab chingri';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Daab chingri', 140.00, 160.00, 12.50, cat_id, cant_id, '/images/Daab%20chingri.jpg', 'Prawn curry cooked in green coconut.', 50, true, false, true, 12);
    END IF;


    -- Dish 150: Luchi
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Luchi' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Luchi', '/images/Luchi.jpg', 150, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (149 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Luchi') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Luchi.jpg',
            description = 'A Puffed bread, fried in oil, made from flour. A Bengali speciality.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Luchi';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Luchi', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Luchi.jpg', 'A Puffed bread, fried in oil, made from flour. A Bengali speciality.', 50, true, false, true, 12);
    END IF;


    -- Dish 151: Malpua/Malpoa
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Malpua/Malpoa' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Malpua/Malpoa', '/images/Malpua-Malpoa.jpg', 151, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (150 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Malpua/Malpoa') THEN
        UPDATE menu_items SET
            price = 60.00,
            original_price = 70.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Malpua-Malpoa.jpg',
            description = 'Sweet snacks notable in Northeast and East India, specially in Odisha.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Malpua/Malpoa';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Malpua/Malpoa', 60.00, 70.00, 14.29, cat_id, cant_id, '/images/Malpua-Malpoa.jpg', 'Sweet snacks notable in Northeast and East India, specially in Odisha.', 50, true, false, true, 12);
    END IF;


    -- Dish 152: Momo
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Momo' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Momo', '/images/Momo.jpg', 152, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (151 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Momo') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Momo.jpg',
            description = 'Originally from Tibet, it is a popular snack/ food item in India specially within Indo-Nepalese community.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Momo';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Momo', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Momo.jpg', 'Originally from Tibet, it is a popular snack/ food item in India specially within Indo-Nepalese community.', 50, true, false, true, 12);
    END IF;


    -- Dish 153: Black rice
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Black rice' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Black rice', '/images/Black%20rice.jpg', 153, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (152 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Black rice') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Black%20rice.jpg',
            description = 'A special local variety of rice',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Black rice';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Black rice', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Black%20rice.jpg', 'A special local variety of rice', 50, true, false, true, 12);
    END IF;


    -- Dish 154: Brown Rice
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Brown Rice' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Brown Rice', '/images/Brown%20Rice.jpg', 154, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (153 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Brown Rice') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Brown%20Rice.jpg',
            description = 'A special local variety of rice.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Brown Rice';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Brown Rice', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Brown%20Rice.jpg', 'A special local variety of rice.', 50, true, false, true, 12);
    END IF;


    -- Dish 155: Chhenagaja
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Chhenagaja' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Chhenagaja', '/images/Chhenagaja.jpg', 155, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (154 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Chhenagaja') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Chhenagaja.jpg',
            description = 'Odia Dessert. Cottage cheese, flour, sugar syrup.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Chhenagaja';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Chhenagaja', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Chhenagaja.jpg', 'Odia Dessert. Cottage cheese, flour, sugar syrup.', 50, true, false, true, 12);
    END IF;


    -- Dish 156: Chhenapoda
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Chhenapoda' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Chhenapoda', '/images/Chhenapoda.jpg', 156, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (155 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Chhenapoda') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Chhenapoda.jpg',
            description = 'Dessert. Cottage cheese, flour, sugar syrup. Odia Specialty.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Chhenapoda';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Chhenapoda', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Chhenapoda.jpg', 'Dessert. Cottage cheese, flour, sugar syrup. Odia Specialty.', 50, true, false, true, 12);
    END IF;


    -- Dish 157: Chingri malai curry
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Chingri malai curry' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Chingri malai curry', '/images/Chingri%20malai%20curry.jpg', 157, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (156 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Chingri malai curry') THEN
        UPDATE menu_items SET
            price = 140.00,
            original_price = 160.00,
            discount_percent = 12.50,
            category_id = cat_id,
            image_url = '/images/Chingri%20malai%20curry.jpg',
            description = 'Curry. Prawn, coconut, mustard, steamed. Traditional Bengali Dish.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Chingri malai curry';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Chingri malai curry', 140.00, 160.00, 12.50, cat_id, cant_id, '/images/Chingri%20malai%20curry.jpg', 'Curry. Prawn, coconut, mustard, steamed. Traditional Bengali Dish.', 50, true, false, true, 12);
    END IF;


    -- Dish 158: Dal
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Dal' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Dal', '/images/Dal.jpg', 158, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (157 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Dal') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Dal.jpg',
            description = 'Lentils.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Dal';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Dal', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Dal.jpg', 'Lentils.', 50, true, false, true, 12);
    END IF;


    -- Dish 159: Goja
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Goja' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Goja', '/images/Goja.jpg', 159, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (158 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Goja') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Goja.jpg',
            description = 'A sweet Bengali speciality.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Goja';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Goja', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Goja.jpg', 'A sweet Bengali speciality.', 50, true, false, true, 12);
    END IF;


    -- Dish 160: Ilish or Chingri Bhape
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Ilish or Chingri Bhape' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Ilish or Chingri Bhape', '/images/Ilish%20or%20Chingri%20Bhape.jpg', 160, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (159 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Ilish or Chingri Bhape') THEN
        UPDATE menu_items SET
            price = 140.00,
            original_price = 160.00,
            discount_percent = 12.50,
            category_id = cat_id,
            image_url = '/images/Ilish%20or%20Chingri%20Bhape.jpg',
            description = 'Curry. Ilish (Hilsha fish) or prawn, coconut, mustard, steamed. Traditional Bengali Dish.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Ilish or Chingri Bhape';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Ilish or Chingri Bhape', 140.00, 160.00, 12.50, cat_id, cant_id, '/images/Ilish%20or%20Chingri%20Bhape.jpg', 'Curry. Ilish (Hilsha fish) or prawn, coconut, mustard, steamed. Traditional Bengali Dish.', 50, true, false, true, 12);
    END IF;


    -- Dish 161: Machher Jhol
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Machher Jhol' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Machher Jhol', '/images/Machher%20Jhol_2.jpg', 161, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (160 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Machher Jhol') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Machher%20Jhol_2.jpg',
            description = 'A curry of fish, and various spices.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Machher Jhol';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Machher Jhol', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Machher%20Jhol_2.jpg', 'A curry of fish, and various spices.', 50, true, false, true, 12);
    END IF;


    -- Dish 162: Mishti Doi
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Mishti Doi' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Mishti Doi', '/images/Mishti%20Doi.jpg', 162, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (161 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Mishti Doi') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Mishti%20Doi.jpg',
            description = 'A dessert with curd, sugar syrup or jaggery. Bengali Sweet curd.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Mishti Doi';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Mishti Doi', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Mishti%20Doi.jpg', 'A dessert with curd, sugar syrup or jaggery. Bengali Sweet curd.', 50, true, false, true, 12);
    END IF;


    -- Dish 163: Pakhala
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Pakhala' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Pakhala', '/images/Pakhala_2.jpg', 163, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (162 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Pakhala') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Pakhala_2.jpg',
            description = 'Odia dish with fermented rice, yoghurt, salt & seasonings.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Pakhala';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Pakhala', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Pakhala_2.jpg', 'Odia dish with fermented rice, yoghurt, salt & seasonings.', 50, true, false, true, 12);
    END IF;


    -- Dish 164: Bhaji
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Bhaji' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Bhaji', '/images/Bhaji.jpg', 164, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (163 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Bhaji') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Bhaji.jpg',
            description = 'Fried Vegetables.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Bhaji';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Bhaji', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Bhaji.jpg', 'Fried Vegetables.', 50, true, false, true, 12);
    END IF;


    -- Dish 165: Pantua
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Pantua' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Pantua', '/images/Pantua.jpg', 165, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (164 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Pantua') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Pantua.jpg',
            description = 'It is a traditional Bengali sweet made of deep-fried balls of semolina, chhena, milk, ghee and sugar syrup. Notable in West Bengal, Eastern India and Bangladesh.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Pantua';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Pantua', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Pantua.jpg', 'It is a traditional Bengali sweet made of deep-fried balls of semolina, chhena, milk, ghee and sugar syrup. Notable in West Bengal, Eastern India and Bangladesh.', 50, true, false, true, 12);
    END IF;


    -- Dish 166: Peda
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Peda' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Peda', '/images/Peda.jpg', 166, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (165 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Peda') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Peda.jpg',
            description = 'Sweet',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Peda';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Peda', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Peda.jpg', 'Sweet', 50, true, false, true, 12);
    END IF;


    -- Dish 167: Red Rice
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Red Rice' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Red Rice', '/images/Red%20Rice.jpg', 167, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (166 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Red Rice') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Red%20Rice.jpg',
            description = 'Special local variety of rice.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Red Rice';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Red Rice', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Red%20Rice.jpg', 'Special local variety of rice.', 50, true, false, true, 12);
    END IF;


    -- Dish 168: Rice
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Rice' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Rice', '/images/Rice.jpg', 168, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (167 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Rice') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Rice.jpg',
            description = 'Staple Food.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Rice';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Rice', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Rice.jpg', 'Staple Food.', 50, true, false, true, 12);
    END IF;


    -- Dish 169: Rasagola/Roshogolla
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Rasagola/Roshogolla' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Rasagola/Roshogolla', '/images/Rasagola-Roshogolla.jpg', 169, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (168 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Rasagola/Roshogolla') THEN
        UPDATE menu_items SET
            price = 60.00,
            original_price = 70.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Rasagola-Roshogolla.jpg',
            description = 'A sweet dessert using cottage cheese, flour and sugar syrup. Originated independently in different versions and taste in Odisha and West Bengal, Eastern India.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Rasagola/Roshogolla';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Rasagola/Roshogolla', 60.00, 70.00, 14.29, cat_id, cant_id, '/images/Rasagola-Roshogolla.jpg', 'A sweet dessert using cottage cheese, flour and sugar syrup. Originated independently in different versions and taste in Odisha and West Bengal, Eastern India.', 50, true, false, true, 12);
    END IF;


    -- Dish 170: Shondesh
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Shondesh' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Shondesh', '/images/Shondesh.jpg', 170, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (169 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Shondesh') THEN
        UPDATE menu_items SET
            price = 60.00,
            original_price = 70.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Shondesh.jpg',
            description = 'A dessert with milk and sugar. A signature Bengali dish.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Shondesh';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Shondesh', 60.00, 70.00, 14.29, cat_id, cant_id, '/images/Shondesh.jpg', 'A dessert with milk and sugar. A signature Bengali dish.', 50, true, false, true, 12);
    END IF;


    -- Dish 171: Shukto
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = 'Shukto' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, 'Shukto', '/images/Shukto.jpg', 171, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := (170 % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = 'Shukto') THEN
        UPDATE menu_items SET
            price = 90.00,
            original_price = 105.00,
            discount_percent = 14.29,
            category_id = cat_id,
            image_url = '/images/Shukto.jpg',
            description = 'A Bengali cuisine. Diced potatoes, sweet potatoes, broad beans, eggplant, drumsticks, raw bananas, radish cooked together and sautéed with mustard seeds. This culinary cooked in mustard oil and sometimes shredded coconut can also be used.',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = 'Shukto';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), 'Shukto', 90.00, 105.00, 14.29, cat_id, cant_id, '/images/Shukto.jpg', 'A Bengali cuisine. Diced potatoes, sweet potatoes, broad beans, eggplant, drumsticks, raw bananas, radish cooked together and sautéed with mustard seeds. This culinary cooked in mustard oil and sometimes shredded coconut can also be used.', 50, true, false, true, 12);
    END IF;


    RAISE NOTICE 'Menu items and categories inserted and equally distributed successfully!';
END $$;
