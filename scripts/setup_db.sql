-- =====================================================
-- EDUAI CAMEROUN — Script de création de base MySQL
-- Exécuter dans phpMyAdmin ou MySQL Workbench
-- =====================================================

CREATE DATABASE IF NOT EXISTS eduai_cameroun
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE eduai_cameroun;

-- L'utilisateur root de XAMPP est utilisé par défaut.
-- Optionnel : créer un utilisateur dédié
-- CREATE USER 'eduai_user'@'localhost' IDENTIFIED BY 'eduai_password_2025';
-- GRANT ALL PRIVILEGES ON eduai_cameroun.* TO 'eduai_user'@'localhost';
-- FLUSH PRIVILEGES;

SELECT 'Base de données eduai_cameroun créée avec succès !' AS message;
