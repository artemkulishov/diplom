
-- Триггер на проверку даты и времени записи матча 
DELIMITER //

CREATE TRIGGER check_event_datetime
BEFORE INSERT ON events
FOR EACH ROW
BEGIN
    IF NEW.match_date < CURDATE() OR (NEW.match_date = CURDATE() AND NEW.match_time <= CURTIME()) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Event datetime cannot be in the past or present.';
    END IF;
END//

DELIMITER ;





 -- Триггер на заполнение таблицы event_staff
DELIMITER //

CREATE TRIGGER after_event_insert
AFTER INSERT ON events
FOR EACH ROW
BEGIN

    INSERT INTO event_staff (event_id, staff_id)
    VALUES (NEW.event_id, NEW.director_id),
           (NEW.event_id, NEW.commentator_id),
           (NEW.event_id, NEW.photograph_id),
           (NEW.event_id, NEW.employee1_id),
           (NEW.event_id, NEW.employee2_id),
           (NEW.event_id, NEW.employee3_id);
END;
//

DELIMITER ;








USE match_db;


SET @key_str = 'my_secret_key';


INSERT INTO staff (staff_name, role, password)
VALUES ('Иван.Иванов', 'Менеджер', AES_ENCRYPT('my_secure_password', @key_str));


