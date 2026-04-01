
CREATE OR REPLACE FUNCTION search_phonebook(p text)
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