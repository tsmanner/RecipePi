BEGIN;
CREATE TABLE /*_*/rw_licenses(
--License ID, the primary key
  license_id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
--License name
  license_name VARCHAR(255) NOT NULL,
--License HTML
  license TEXT NOT NULL,
--Constraints
  UNIQUE(license_name)
) /*$wgDBTableOptions*/;
COMMIT;
