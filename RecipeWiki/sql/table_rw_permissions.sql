BEGIN;
CREATE TABLE /*_*/rw_permissions(
--Permission ID, the primary key
  permission_id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
--Permission name
  permission_name VARCHAR(255) NOT NULL
) /*$wgDBTableOptions*/;
COMMIT;
