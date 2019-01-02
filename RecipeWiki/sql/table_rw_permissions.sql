BEGIN;
CREATE TABLE /*_*/rw_permissions(
--Permission ID, the primary key
  permission_id INT UNSIGNED NOT NULL PRIMARY KEY,
--Permission name
  permission_name VARCHAR(255) NOT NULL
) /*$wgDBTableOptions*/;


--INSERT INTO /*_*/rw_permissions (permission_id, permission_name) VALUES (1, "Read") ON DUPLICATE KEY UPDATE;
--INSERT INTO /*_*/rw_permissions (permission_id, permission_name) VALUES (2, "Edit") ON DUPLICATE KEY UPDATE;
--INSERT INTO /*_*/rw_permissions (permission_id, permission_name) VALUES (3, "Administer") ON DUPLICATE KEY UPDATE;

COMMIT;
