CREATE DATABASE  IF NOT EXISTS `match_db` 
USE `match_db`;

DROP TABLE IF EXISTS `customers`;
CREATE TABLE `customers` (
  `customer_id` int NOT NULL AUTO_INCREMENT,
  `customer_name` varchar(255) NOT NULL,
  `customer_phone` varchar(20) NOT NULL,
  PRIMARY KEY (`customer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOCK TABLES `customers` WRITE;

INSERT INTO `customers` VALUES (1,'ОБЕ КОМАНДЫ','00000000000'),(2,'КРАСНАЯ МАШИНА ЮНИОР','89123456789'),(3,'СКА','89256789012'),(4,'Армия СКА','89112345678'),(5,'ДИНАМО','89267890123'),(6,'ДИНАМО ПИТЕР','89134567890'),(7,'ДИНАМО ЮНИОР','89290123456'),(8,'СКА ЗВЕЗДА','89156789012'),(9,'СКА ПЕТЕРГОФ','89213456789'),(10,'СКА СТРЕЛЬНА ','89278901234');
UNLOCK TABLES;


DROP TABLE IF EXISTS `event_staff`;

CREATE TABLE `event_staff` (
  `event_staff_id` int NOT NULL AUTO_INCREMENT,
  `event_id` int DEFAULT NULL,
  `staff_id` int DEFAULT NULL,
  PRIMARY KEY (`event_staff_id`),
  KEY `fk_event_id` (`event_id`),
  KEY `fk_staff_id` (`staff_id`),
  CONSTRAINT `event_staff_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `events` (`event_id`),
  CONSTRAINT `event_staff_ibfk_2` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`staff_id`),
  CONSTRAINT `fk_event_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`event_id`),
  CONSTRAINT `fk_staff_id` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`staff_id`)
) ENGINE=InnoDB AUTO_INCREMENT=356901 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



LOCK TABLES `event_staff` WRITE;

INSERT INTO `event_staff` VALUES (356883,6699,26),(356884,6699,27),(356885,6699,28),(356886,6699,29),(356887,6699,30),(356888,6699,33),(356889,6700,26),(356890,6700,27),(356891,6700,28),(356892,6700,29),(356893,6700,30),(356894,6700,33),(356895,6701,31),(356896,6701,27),(356897,6701,26),(356898,6701,29),(356899,6701,30),(356900,6701,33);

UNLOCK TABLES;


DROP TABLE IF EXISTS `events`;

CREATE TABLE `events` (
  `event_id` int NOT NULL AUTO_INCREMENT,
  `location_id` int DEFAULT NULL,
  `home_team_id` int DEFAULT NULL,
  `away_team_id` int DEFAULT NULL,
  `match_date` date NOT NULL,
  `match_time` time NOT NULL,
  `broadcast_key` varchar(255) NOT NULL,
  `customer_id` int DEFAULT NULL,
  `comment` text,
  `operator_id` int DEFAULT NULL,
  `director_id` int DEFAULT NULL,
  `commentator_id` int DEFAULT NULL,
  `photograph_id` int DEFAULT NULL,
  `employee1_id` int DEFAULT NULL,
  `employee2_id` int DEFAULT NULL,
  `employee3_id` int DEFAULT NULL,
  PRIMARY KEY (`event_id`),
  KEY `location_id` (`location_id`),
  KEY `home_team_id` (`home_team_id`),
  KEY `away_team_id` (`away_team_id`),
  KEY `customer_id` (`customer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6702 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `events` WRITE;

INSERT INTO `events` VALUES (6699,2,2,5,'2024-06-20','22:00:00','Ghdus7868sdcs',3,'ФИНАЛ СНИМАЕМ ХОРОШО',25,26,27,28,29,30,33),(6700,2,2,5,'2024-06-16','22:00:00','Ghdus7868sdcs',3,'ФИНАЛ СНИМАЕМ ХОРОШО',25,26,27,28,29,30,33),(6701,2,1,5,'2024-06-16','22:00:00','Ghdus7868sdcs',3,'',25,31,27,26,29,30,33);

UNLOCK TABLES;

DELIMITER ;;

DELIMITER ;

DELIMITER ;;


DROP TABLE IF EXISTS `locations`;

CREATE TABLE `locations` (
  `location_id` int NOT NULL,
  `location_name` varchar(255) NOT NULL,
  PRIMARY KEY (`location_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



LOCK TABLES `locations` WRITE;

INSERT INTO `locations` VALUES (1,'АСК-С'),(2,'АКХ'),(3,'СКА');

UNLOCK TABLES;


DROP TABLE IF EXISTS `staff`;

CREATE TABLE `staff` (
  `staff_id` int NOT NULL AUTO_INCREMENT,
  `staff_name` varchar(255) NOT NULL,
  `role` varchar(255) NOT NULL,
  `password` varbinary(255) DEFAULT NULL,
  `chat_id` int DEFAULT NULL,
  `staff_level` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`staff_id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOCK TABLES `staff` WRITE;

-- Вставка данных с шифрованием пароля
INSERT INTO `staff` (staff_id, staff_name, role, password, chat_id, staff_level) VALUES
(25, 'Артем', 'Оператор', AES_ENCRYPT('Password1', 'my_secret_key'), 780023471, 'Профессионал'),
(26, 'Михаил', 'Оператор', AES_ENCRYPT('Password1', 'my_secret_key'), NULL, 'Начинаюший'),
(27, 'Александр', 'Режиссер', AES_ENCRYPT('Password1', 'my_secret_key'), NULL, 'Профессионал'),
(28, 'Владлен', 'Оператор', AES_ENCRYPT('Password1', 'my_secret_key'), NULL, 'Профессионал'),
(29, 'Лев', 'Режиссер', AES_ENCRYPT('Password1', 'my_secret_key'), NULL, 'Начинаюший'),
(30, 'Сергей', 'Оператор', AES_ENCRYPT('Password1', 'my_secret_key'), NULL, 'Начинаюший'),
(31, 'Илья', 'Коментатор', AES_ENCRYPT('', 'my_secret_key'), NULL, 'Стажер'),
(32, 'Андрей', 'Режиссер', AES_ENCRYPT('Password1', 'my_secret_key'), NULL, 'Профессионал'),
(33, 'Гриша', 'Оператор', AES_ENCRYPT('Password1', 'my_secret_key'), NULL, 'Стажер');

UNLOCK TABLES;



DROP TABLE IF EXISTS `teams`;

CREATE TABLE `teams` (
  `team_id` int NOT NULL AUTO_INCREMENT,
  `team_name` varchar(255) NOT NULL,
  PRIMARY KEY (`team_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOCK TABLES `teams` WRITE;

INSERT INTO `teams` VALUES (1,'КМЮ'),(2,'СКА'),(3,'ДНС'),(4,'ДНЮ'),(5,'АРМИЯ СКА');

UNLOCK TABLES;

