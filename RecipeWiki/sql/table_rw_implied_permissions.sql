BEGIN;
CREATE TABLE /*_*/rw_implied_permissions(
-- Implied Permission ID, the primary key
  ip_id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
-- Master Permission ID
  master_permission_id INT UNSIGNED NOT NULL,
-- Implied Permission ID
  implied_permission_id INT UNSIGNED NOT NULL,
-- Define foreign keys
  CONSTRAINT FOREIGN KEY (master_permission_id) REFERENCES rw_permissions(permission_id),
  CONSTRAINT FOREIGN KEY (implied_permission_id) REFERENCES rw_permissions(permission_id),
-- Make sure that the permission IDs aren't the same
  CONSTRAINT CHECK (master_permission_id!=implied_permission_id)
) /*$wgDBTableOptions*/;

-- Edit implies Read
--INSERT INTO /*_*/rw_implied_permissions (master_permission_id, implied_permission_id) VALUES (2, 1) ON DUPLICATE KEY UPDATE;
-- Administer impies Read
--INSERT INTO /*_*/rw_implied_permissions (master_permission_id, implied_permission_id) VALUES (3, 1) ON DUPLICATE KEY UPDATE;

COMMIT;
