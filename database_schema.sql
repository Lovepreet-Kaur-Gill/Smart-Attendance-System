-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: attendance_db_final
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `attendance`
--

DROP TABLE IF EXISTS `attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Roll_No` varchar(50) NOT NULL,
  `Name` varchar(50) DEFAULT NULL,
  `Time` varchar(50) DEFAULT NULL,
  `Date` varchar(50) DEFAULT NULL,
  `Status` varchar(50) DEFAULT NULL,
  `Subject` varchar(50) DEFAULT NULL,
  `Marked_By` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `Roll_No` (`Roll_No`),
  CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`Roll_No`) REFERENCES `student` (`Roll_No`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance`
--

LOCK TABLES `attendance` WRITE;
/*!40000 ALTER TABLE `attendance` DISABLE KEYS */;
INSERT INTO `attendance` VALUES (1,'2301301130','Lovepreet Kaur','15:05:52','2025-12-04','Present','DV','Priya'),(2,'2301301171','Diya gupta','15:06:06','2025-12-04','Present','DV','Priya'),(3,'2301301130','Lovepreet Kaur','10:30:10','2025-12-05','Present','Project','Priya'),(4,'2301301130','Lovepreet Kaur','19:15:40','2025-12-07','Present','Data Structures','aditi'),(5,'2301301130','Lovepreet Kaur','14:17:51','2025-12-10','Present','Operating system','priya'),(6,'999','Test User','14:20:20','2025-12-10','Present','Giography','neha'),(7,'2301301130','Lovepreet Kaur','14:26:10','2025-12-10','Present','Java','abc');
/*!40000 ALTER TABLE `attendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student`
--

DROP TABLE IF EXISTS `student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student` (
  `Student_ID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(50) DEFAULT NULL,
  `Roll_No` varchar(50) NOT NULL,
  `Department` varchar(50) DEFAULT NULL,
  `Course` varchar(50) DEFAULT NULL,
  `Year` varchar(20) DEFAULT NULL,
  `Semester` varchar(20) DEFAULT NULL,
  `Section` varchar(10) DEFAULT NULL,
  `DOB` varchar(20) DEFAULT NULL,
  `Gender` varchar(20) DEFAULT NULL,
  `Phone` varchar(20) DEFAULT NULL,
  `Address` varchar(100) DEFAULT NULL,
  `Photo_Sample` varchar(10) DEFAULT 'No',
  `Parent_Email` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`Student_ID`),
  UNIQUE KEY `Roll_No` (`Roll_No`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student`
--

LOCK TABLES `student` WRITE;
/*!40000 ALTER TABLE `student` DISABLE KEYS */;
INSERT INTO `student` VALUES (2,'Lovepreet Kaur','2301301130','CSE','B.Tech','2024-25','Semester-1','A','2004-09-05','Female','9789006455','Tohana','Yes','preetkaurgill437@gmail.com'),(4,'Test User','999','Arts','B.A','2024-25','Semester-1','B','2003-12-09','Female','9867845678','Zind','Yes','2301301130.lovepreet@geetauniversity.edu.in'),(5,'Diya gupta','2301301171','CSE','B.Tech','2024-25','Semester-1','A','2005-10-12','Female','8976034567','Hisar','Yes','rekhagupta39762@gmail.com'),(6,'Sahil Singh','2301301121','CSE','B.Tech','2024-25','Semester-5','D','2005-06-21','Male','9812019772','Hisar, Haryana','Yes','sahilsingh19772@gmail.com');
/*!40000 ALTER TABLE `student` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacher`
--

DROP TABLE IF EXISTS `teacher`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teacher` (
  `Teacher_ID` int NOT NULL AUTO_INCREMENT,
  `Phone` varchar(20) DEFAULT NULL,
  `Department` varchar(50) DEFAULT NULL,
  `Username` varchar(50) DEFAULT NULL,
  `Password` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`Teacher_ID`),
  UNIQUE KEY `Username` (`Username`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacher`
--

LOCK TABLES `teacher` WRITE;
/*!40000 ALTER TABLE `teacher` DISABLE KEYS */;
INSERT INTO `teacher` VALUES (1,'8790645678','CSE','aditi','aditi1'),(2,'9856723145','Arts','neha','neha1'),(3,'9867845632','CSE','priya','priya1'),(4,'8976512123','CSE','abc','a1');
/*!40000 ALTER TABLE `teacher` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `timetable`
--

DROP TABLE IF EXISTS `timetable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `timetable` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Department` varchar(50) DEFAULT NULL,
  `Year` varchar(20) DEFAULT NULL,
  `Semester` varchar(20) DEFAULT NULL,
  `Section` varchar(10) DEFAULT NULL,
  `Day` varchar(20) DEFAULT NULL,
  `Time_Start` time DEFAULT NULL,
  `Time_End` time DEFAULT NULL,
  `Subject` varchar(50) DEFAULT NULL,
  `Teacher_Username` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_class_slot` (`Year`,`Section`,`Day`,`Time_Start`),
  UNIQUE KEY `unique_teacher_slot` (`Teacher_Username`,`Day`,`Time_Start`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `timetable`
--

LOCK TABLES `timetable` WRITE;
/*!40000 ALTER TABLE `timetable` DISABLE KEYS */;
INSERT INTO `timetable` VALUES (5,'CSE','2024-25','Semester-1','A','Monday','09:00:00','10:00:00','java','priya'),(7,'CSE','2024-25','Semester-2','A','Monday','10:00:00','11:00:00','DSA','abc'),(8,'Arts','2024-25','Semester-1','B','Monday','09:00:00','10:00:00','History','neha'),(9,'CSE','2024-25','Semester-1','A','Wednesday','14:00:00','15:00:00','Operating system','priya'),(10,'Arts','2024-25','Semester-1','B','Wednesday','14:00:00','15:00:00','Giography','neha'),(11,'CSE','2023-24','Semester-2','A','Wednesday','14:00:00','15:00:00','Java','abc');
/*!40000 ALTER TABLE `timetable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_credentials`
--

DROP TABLE IF EXISTS `user_credentials`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_credentials` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `role` varchar(20) DEFAULT 'admin',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_credentials`
--

LOCK TABLES `user_credentials` WRITE;
/*!40000 ALTER TABLE `user_credentials` DISABLE KEYS */;
INSERT INTO `user_credentials` VALUES (1,'admin','admin123','admin'),(2,'abc','abc1','admin'),(3,'root','root123','super_admin');
/*!40000 ALTER TABLE `user_credentials` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-11  1:04:33
