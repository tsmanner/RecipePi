BEGIN;
CREATE TABLE /*_*/rw_article_user_permissions(
--Permission ID, the primary key
  aup_id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
--Article ID
  article_id INT UNSIGNED NOT NULL,
--User ID
  user_id INT UNSIGNED NOT NULL,
--Permission ID
  permission_id INT UNSIGNED NOT NULL,
--Define foreign keys
  CONSTRAINT FOREIGN KEY (article_id)    REFERENCES page(page_id),
  CONSTRAINT FOREIGN KEY (user_id)       REFERENCES user(user_id),
  CONSTRAINT FOREIGN KEY (permission_id) REFERENCES rw_permissions(permission_id),
--Unique the permission being set
  UNIQUE(article_id, user_id, permission_id)
) /*$wgDBTableOptions*/;
COMMIT;
