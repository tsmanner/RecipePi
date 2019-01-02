BEGIN;
CREATE TABLE /*_*/rw_article_license(
--Article ID, the primary key and a foreign key into `page`
  article_id INT UNSIGNED NOT NULL PRIMARY KEY,
--License texID
  license_id INT UNSIGNED NOT NULL,
--Define foreign keys
  CONSTRAINT FOREIGN KEY (article_id) REFERENCES page(page_id),
  CONSTRAINT FOREIGN KEY (license_id) REFERENCES rw_licenses(license_id)
) /*$wgDBTableOptions*/;
COMMIT;
