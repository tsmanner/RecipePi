BEGIN;
CREATE TABLE /*_*/rw_is_recipe(
--Article ID, the primary key and a foreign key into `page`
  article_id INT UNSIGNED NOT NULL PRIMARY KEY,
--Define foreign keys
  CONSTRAINT FOREIGN KEY (article_id) REFERENCES page(page_id)
) /*$wgDBTableOptions*/;
COMMIT;
