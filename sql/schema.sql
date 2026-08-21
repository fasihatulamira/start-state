-- Schema (database): start_state
-- Table created by the app: submissions

CREATE DATABASE IF NOT EXISTS start_state
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE start_state;

CREATE TABLE IF NOT EXISTS submissions (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  unit_name VARCHAR(255) NOT NULL,
  subunits JSON NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_submissions_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- subunits JSON shape:
-- [
--   {
--     "subunit_name": "Alpha",
--     "group_list": "Group A\nGroup B",
--     "place_name": "Hall 1"
--   }
-- ]
