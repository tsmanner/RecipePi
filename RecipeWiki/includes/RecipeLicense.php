<?php


class RecipeLicense {
  public $mId;
  public $mName;
  public $mHTML;

  function __construct($id, $name, $html) {
    $this->mId = $id;
    $this->mName = $name;
    $this->mHTML = $html;
  }

  public static function getAllFromDb() {
    $licenses = array();
    $dbr = wfGetDB(DB_REPLICA);
    $results = $dbr->select('rw_licenses', array('license_id', 'license_name', 'license'));
    foreach ($results as $result) {
      $licenses[] = new RecipeLicense($result->license_id, $result->license_name, $result->license);
    }
    return $licenses;
  }

  public static function newFromId($id) {
    $dbr = wfGetDB(DB_REPLICA);
    if ($id != '') {
      $licenses = $dbr->select('rw_licenses', array('license_id', 'license_name', 'license'), 'license_id=' . $id);
      if ($licenses->numRows() > 0) {
        $license = $licenses->fetchObject();
        return new RecipeLicense($license->license_id, $license->license_name, $license->license);
      }
    }
    return NULL;
  }

  public static function addArticleLicense($article_id, $license_id) {
    $dbm = wfGetDB(DB_MASTER);
    if (
      $dbm->select(
        'rw_article_license',
        array('article_id', 'license_id'),
        array('article_id=' . $article_id)
      )->numRows() == 0
    ) {
      $dbm->insert(
        'rw_article_license',
        array(
          'article_id' => $article_id,
          'license_id' => $license_id
        )
      );
    }
    else {
      $dbm->update(
        'rw_article_license',
        array(
          'article_id' => $article_id,
          'license_id' => $license_id
        ),
        array(
          'article_id=' . $article_id
        )
      );
    }
  }

}

?>
