
ALTER TABLE lifestream_feed ADD COLUMN `fetch_error_count` TINYINT NOT NULL DEFAULT 0 AFTER last_modified;
