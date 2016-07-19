/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# Create database
# ------------------------------------------------------------

create database settled;

use settled;


# Dump of table logins
# ------------------------------------------------------------

DROP TABLE IF EXISTS `logins`;

CREATE TABLE `logins` (
  `token` varchar(255) NOT NULL,
  `user_id` bigint(20) unsigned NOT NULL,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


# Dump of table messages
# ------------------------------------------------------------

DROP TABLE IF EXISTS `messages`;

CREATE TABLE `messages` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `owner` bigint(20) unsigned NOT NULL,
  `editor` bigint(20) unsigned NOT NULL,
  `message` text NOT NULL,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `sender_index` (`owner`),
  KEY `receiver_index` (`editor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

# Dump of table users
# ------------------------------------------------------------

DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user` varchar(255) NOT NULL DEFAULT '',
  `pswd` varchar(255) NOT NULL DEFAULT '',
  `enabled` tinyint(1) unsigned NOT NULL DEFAULT '1',
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user` (`user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;

INSERT INTO `users` (`id`, `user`, `pswd`, `enabled`, `name`)
VALUES
	(1,'seller@settled','$2b$12$/GODpqTxkPqXEpgWGQNyTubnZ1JbmfLRNPGPYZg.C9MVClacN3x3e',1,'Jack Seller'),
	(2,'buyer1@settled','$2b$12$/GODpqTxkPqXEpgWGQNyTubnZ1JbmfLRNPGPYZg.C9MVClacN3x3e',1,'Claire Buyer'),
	(3,'buyer2@settled','$2b$12$/GODpqTxkPqXEpgWGQNyTubnZ1JbmfLRNPGPYZg.C9MVClacN3x3e',1,'Jill Buyer'),
	(4,'buyer3@settled','$2b$12$/GODpqTxkPqXEpgWGQNyTubnZ1JbmfLRNPGPYZg.C9MVClacN3x3e',1,'John Buyer'),
	(5,'buyer4@settled','$2b$12$/GODpqTxkPqXEpgWGQNyTubnZ1JbmfLRNPGPYZg.C9MVClacN3x3e',1,'Tom Buyer'),
	(6,'buyer5@settled','$2b$12$/GODpqTxkPqXEpgWGQNyTubnZ1JbmfLRNPGPYZg.C9MVClacN3x3e',1,'Francisco Buyer');

/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
