<?php

class UserPermissions {
  public $mUser = NULL;
  public $mPermissions;

  function __construct(User $user) {
    $dbr = wfGetDB(DB_REPLICA);
    // Initialize mPermissions with all the permission IDs we know about
    $this->mPermissions = array();
    foreach (Permission::getAllFromDb() as $perm) {
      $this->mPermissions[$perm->mId] = array();
    }

    // Query for this user's article permissions
    $aups = $dbr->select(
      'rw_article_user_permissions',
      array('article_id', 'user_id', 'permission_id'),
      'user_id=' . $user->getId()
    );

    $this->mUser = $user;

    // For each article user permission, if it hasn't been
    // added yet, add it to mPermissions
    foreach ($aups as $aup) {
      if (!in_array($aup->article_id, $this->mPermissions[$aup->permission_id])) {
        $this->mPermissions[$aup->permission_id][] = $aup->article_id;
        // Also grab the implied permissions
        $implied = $dbr->select(
          'rw_implied_permissions',
          array('implied_permission_id'),
          'master_permission_id=' . $aup->permission_id
        );
        // For each implied article user permission, if it
        // hasn't been added yet, add it to mPermissions
        foreach ($implied as $impl) {
          if (!in_array($aup->article_id, $this->mPermissions[$impl->implied_permission_id])) {
            $this->mPermissions[$impl->implied_permission_id][] = $aup->article_id;
          }
        }
      }
    }
  }

  public static function newFromUserId($user_id) {
    return new UserPermissions(User::fromId($user_id));
  }

  public static function addUserPermission($article_id, $user_id, $permission_id) {
    // If there's no matching entry yet, insert this set of permissions
    $dbm = wfGetDB(DB_MASTER);
    if (
      $dbm->select(
        'rw_article_user_permissions',
        array('aup_id'),
        array(
          'article_id='    . $article_id,
          'user_id='       . $user_id,
          'permission_id=' . $permission_id
        )
      )->numRows() == 0
    ) {
      $dbm->insert(
        'rw_article_user_permissions',
        array(
          'article_id'    => $article_id,
          'user_id'       => $user_id,
          'permission_id' => $permission_id
        )
      );
    }
  }

}

?>
