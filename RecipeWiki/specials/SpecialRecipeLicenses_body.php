<?php

class SpecialRecipeLicenses extends SpecialPage {
  function __construct() {
    parent::__construct( 'RecipeLicenses' );
  }

  function execute($par) {
    global $wgUser;
    $request = $this->getRequest();
    $output = $this->getOutput();
    $this->setHeaders();

    $dbm = wfGetDB(DB_MASTER);
    $userPermissions = new UserPermissions($wgUser);

    //
    // Page       (Text Entry)
    // User       (Text Entry)
    // Permission (Dropdown)
    //
    $add_permission_form = '<form action="" method="post">' .
    'Recipe Page: <input type="text" name="page_name" value="' . $_POST['page_name'] . '"><br/>' .
    'User: <input type="text" name="user_name" value="' . $_POST['user_name'] . '"><br/>' .
    'Permission: <select name="permission_id">';

    foreach(Permission::getAllFromDb() as $perm) {
      $add_permission_form .=
        '<option value="' . $perm->mId . '">' .
        $perm->mName . "</option>";
    }

    $add_permission_form .= '</select><br/>' .
    '<input type="submit" value="Grant">' .
    '</form>';

    $output->addHTML($add_permission_form);

    if (
      array_key_exists('page_name', $_POST) && $_POST['page_name'] != '' &&
      array_key_exists('user_name', $_POST) && $_POST['user_name'] != '' &&
      array_key_exists('permission_id', $_POST) && $_POST['permission_id'] != ''
    ) {
      $title = Title::newFromText($_POST['page_name']);
      // Page Not Found
      if ($dbm->select('page', array('page_id'), 'page_title="' . $title->getDBkey() . '"')->numRows() == 0 ) {
        $output->addWikiText('<span style="color: red">Page \'' . $_POST['page_name'] . '\' Not Found</span>');
      }
      // Not an Administrator
      else if (
        !$wgUser->getGroupMemberships()['bureaucrat'] &&
        !in_array($title->getArticleID(), $userPermissions->mPermissions[2])
      ) {
        $output->addWikiText('<span style="color: red">You are not an Administrator of Page \'' . $_POST['page_name'] . '\'</span>');
      }
      // All Good!
      else {
        $user = User::newFromName($_POST['user_name']);
        UserPermissions::addUserPermission($title->getArticleID(), $user->getId(), $_POST['permission_id']);
      }
    }

    //
    // Report the user's permissions
    //
    foreach ($userPermissions->mPermissions as $perm => $articles) {
      $permission = Permission::newFromId($perm);
      $wikitext = 'Permission ' . $permission->mName . ':';
      foreach ($articles as $article_id) {
        $title = Title::newFromId($article_id);
        if ($title) {
          $wikitext .= ' ' . $title->getText();
        }
      }

      $output->addWikiText($wikitext);
    }
  }
}
?>
