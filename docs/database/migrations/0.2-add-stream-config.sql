ALTER TABLE lifestream_entry ADD COLUMN `visible` bool NOT NULL DEFAULT true;

ALTER TABLE lifestream_stream ADD COLUMN `config` longtext NOT NULL;
ALTER TABLE lifestream_stream ADD COLUMN  `edit_list` longtext NOT NULL;
