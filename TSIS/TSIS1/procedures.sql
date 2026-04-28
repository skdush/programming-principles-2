CREATE OR REPLACE PROCEDURE upsert_contact(
    p_username VARCHAR, p_first_name VARCHAR, p_last_name VARCHAR, p_phone VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE username = p_username) THEN
        UPDATE phonebook SET phone = p_phone WHERE username = p_username;
    ELSE
        INSERT INTO phonebook (username, first_name, last_name, phone)
        VALUES (p_username, p_first_name, p_last_name, p_phone);
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE bulk_insert(
    p_usernames VARCHAR[],
    p_phones    VARCHAR[],
    OUT invalid_data TEXT
)
LANGUAGE plpgsql AS $$
DECLARE
    i   INT;
    bad TEXT := '';
BEGIN
    FOR i IN 1 .. array_length(p_usernames, 1) LOOP
        IF p_phones[i] !~ '^\+?[0-9\s\-\(\)]{7,15}$' THEN
            bad := bad || p_usernames[i] || ':' || p_phones[i] || '; ';
        ELSE
            IF EXISTS (SELECT 1 FROM phonebook WHERE username = p_usernames[i]) THEN
                UPDATE phonebook SET phone = p_phones[i] WHERE username = p_usernames[i];
            ELSE
                INSERT INTO phonebook (username, phone) VALUES (p_usernames[i], p_phones[i]);
            END IF;
        END IF;
    END LOOP;
    invalid_data := bad;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_contact(
    p_username VARCHAR DEFAULT NULL,
    p_phone    VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_username IS NOT NULL THEN
        DELETE FROM phonebook WHERE username = p_username;
    ELSIF p_phone IS NOT NULL THEN
        DELETE FROM phonebook WHERE phone = p_phone;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_id INTEGER;
BEGIN
    SELECT id INTO v_id FROM phonebook WHERE username = p_contact_name;
    IF v_id IS NULL THEN
        RAISE EXCEPTION 'Contact not found: %', p_contact_name;
    END IF;
    INSERT INTO phones (contact_id, phone, type) VALUES (v_id, p_phone, p_type);
END;
$$;

CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    SELECT id INTO v_contact_id FROM phonebook WHERE username = p_contact_name;
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact not found: %', p_contact_name;
    END IF;
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    IF v_group_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name) RETURNING id INTO v_group_id;
    END IF;
    UPDATE phonebook SET group_id = v_group_id WHERE id = v_contact_id;
END;
$$;

CREATE OR REPLACE FUNCTION search_phonebook(p TEXT)
RETURNS TABLE(id INT, username VARCHAR, first_name VARCHAR, last_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
        SELECT pb.id, pb.username, pb.first_name, pb.last_name, pb.phone
        FROM phonebook pb
        WHERE pb.username   ILIKE '%' || p || '%'
           OR pb.first_name ILIKE '%' || p || '%'
           OR pb.last_name  ILIKE '%' || p || '%'
           OR pb.phone      ILIKE '%' || p || '%';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_phonebook_page(p_limit INT, p_offset INT)
RETURNS TABLE(id INT, username VARCHAR, first_name VARCHAR, last_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
        SELECT pb.id, pb.username, pb.first_name, pb.last_name, pb.phone
        FROM phonebook pb
        ORDER BY pb.username
        LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(
    id         INT,
    username   VARCHAR,
    first_name VARCHAR,
    last_name  VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR,
    phone      VARCHAR,
    phone_type VARCHAR
) AS $$
BEGIN
    RETURN QUERY
        SELECT pb.id, pb.username, pb.first_name, pb.last_name,
               pb.email, pb.birthday, g.name, ph.phone, ph.type
        FROM phonebook pb
        LEFT JOIN groups g  ON g.id  = pb.group_id
        LEFT JOIN phones ph ON ph.contact_id = pb.id
        WHERE pb.username   ILIKE '%' || p_query || '%'
           OR pb.first_name ILIKE '%' || p_query || '%'
           OR pb.last_name  ILIKE '%' || p_query || '%'
           OR pb.email      ILIKE '%' || p_query || '%'
           OR ph.phone      ILIKE '%' || p_query || '%';
END;
$$ LANGUAGE plpgsql;
