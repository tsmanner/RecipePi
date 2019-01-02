<?php

class RecipePermission {
  public $mId;
  public $mName;

  function __construct($id, $name) {
    $this->mId = $id;
    $this->mName = $name;
  }

  public static function getAllFromDb() {
    $permissions = array();
    $dbr = wfGetDB(DB_REPLICA);
    $perms = $dbr->select('rw_permissions', array('permission_id', 'permission_name'));
    foreach ($perms as $perm) {
      $permissions[] = new RecipePermission($perm->permission_id, $perm->permission_name);
    }
    return $permissions;
  }

  public static function newFromId($id) {
    $dbr = wfGetDB(DB_REPLICA);
    if ($id != '') {
      $perms = $dbr->select('rw_permissions', array('permission_id', 'permission_name'), 'permission_id=' . $id);
      if ($perms->numRows() > 0) {
        $perm = $perms->fetchObject();
        return new RecipePermission($perm->permission_id, $perm->permission_name);
      }
    }
    return NULL;
  }

}

?>
