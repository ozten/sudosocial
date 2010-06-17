ALTER TABLE lifestream_feed ADD COLUMN `etag` varchar(140) NOT NULL;
ALTER TABLE lifestream_feed ADD COLUMN `last_modified` datetime NOT NULL;
ALTER TABLE lifestream_feed ADD COLUMN `enabled` bool NOT NULL;
ALTER TABLE lifestream_feed ADD COLUMN `disabled_reason` varchar(2048) NOT NULL;


UPDATE lifestream_feed SET `enabled` = true;



-- Ran into some serious utf8 issues
-- udpated my.cnf with utf8 settings
ALTER DATABASE patchouli_prod_6_13 charset=utf8;

--show create table auth_user;
ALTER TABLE auth_user charset=utf8;
ALTER TABLE auth_user MODIFY username VARCHAR(30) CHARACTER SET utf8;
ALTER TABLE auth_user MODIFY first_name VARCHAR(30) CHARACTER SET utf8;
ALTER TABLE auth_user MODIFY last_name VARCHAR(30) CHARACTER SET utf8;
ALTER TABLE auth_user MODIFY email VARCHAR(75) CHARACTER SET utf8;

ALTER TABLE lifestream_feed charset=utf8;
ALTER TABLE lifestream_feed MODIFY title TEXT CHARACTER SET utf8;

ALTER TABLE lifestream_entry charset=utf8;
ALTER TABLE lifestream_entry MODIFY raw longtext CHARACTER SET utf8;

ALTER TABLE lifestream_feed charset=utf8;
ALTER TABLE lifestream_feed MODIFY url longtext CHARACTER SET utf8;
ALTER TABLE lifestream_feed MODIFY title longtext CHARACTER SET utf8;
ALTER TABLE lifestream_feed MODIFY etag longtext CHARACTER SET utf8;
ALTER TABLE lifestream_feed MODIFY disabled_reason longtext CHARACTER SET utf8;


ALTER TABLE lifestream_feed_streams charset=utf8;

show create table lifestream_stream;
ALTER TABLE lifestream_stream charset=utf8;
ALTER TABLE lifestream_stream MODIFY name varchar(140) CHARACTER SET utf8;
ALTER TABLE lifestream_stream MODIFY config longtext CHARACTER SET utf8;
ALTER TABLE lifestream_stream MODIFY edit_list longtext CHARACTER SET utf8;

ALTER TABLE patchouli_auth_userprofile charset=utf8;
ALTER TABLE patchouli_auth_userprofile MODIFY properties longtext  CHARACTER SET utf8;
