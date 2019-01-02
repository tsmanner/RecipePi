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
    $userPermissions = new RecipeUserPermissions($wgUser);

    //
    // Create `permission_form`
    //   Add/Revoke user permissions to a page.
    //
    // Page       (Text Entry)
    // User       (Text Entry)
    // RecipePermission (Dropdown)
    //
    $output->addWikiText('== Change User Recipe Permissions ==');
    $add_permission_form =
      '<form action="" method="post" name="permission_form">' .
      'Recipe Page: <input type="text" name="apf_page_name" value="' . $_POST['apf_page_name'] . '"><br/>' .
      'User: <input type="text" name="apf_user_name" value="' . $_POST['apf_user_name'] . '"><br/>' .
      'Permission: <select name="apf_permission_id">';

    foreach (RecipePermission::getAllFromDb() as $perm) {
      $add_permission_form .='<option value="' . $perm->mId . '"';
      if ($_POST['apf_permission_id'] == $perm->mId) {
        $add_permission_form .= ' selected="selected"';
      }
      $add_permission_form .= '>' . $perm->mName . "</option>";
    }

    $add_permission_form .= '</select><br/>' .
    '<input name="grant" type="submit" value="Grant">' .
    '<input name="revoke" type="submit" value="Revoke">' .
    '</form>';

    $output->addHTML($add_permission_form);

    //
    // Process `permission_form` POSTed data
    //
    if (
      array_key_exists('apf_page_name', $_POST) && $_POST['apf_page_name'] != '' &&
      array_key_exists('apf_user_name', $_POST) && $_POST['apf_user_name'] != '' &&
      array_key_exists('apf_permission_id', $_POST) && $_POST['apf_permission_id'] != ''
    ) {
      $title = Title::newFromText($_POST['apf_page_name']);
      // Page Not Found
      if ($dbm->select('page', array('page_id'), 'page_title="' . $title->getDBkey() . '"')->numRows() == 0 ) {
        $output->addWikiText('<span style="color: red">Page \'' . $_POST['apf_page_name'] . '\' Not Found</span>');
      }
      // Not an Administrator
      else if (
        !$wgUser->getGroupMemberships()['bureaucrat'] &&
        !in_array($title->getArticleID(), $userPermissions->mPermissions[3])
      ) {
        $output->addWikiText('<span style="color: red">You are not an Administrator of Page \'' . $_POST['apf_page_name'] . '\'</span>');
      }
      // All Good!
      else {
        if ($_POST['grant'] == 'Grant') {
          $user = User::newFromName($_POST['apf_user_name']);
          RecipeUserPermissions::addUserPermission($title->getArticleID(), $user->getId(), $_POST['apf_permission_id']);
          $output->addWikiText(
            '<span style="color: green"> Granted ' .
            $_POST['apf_user_name'] . ' ' .
            RecipePermission::newFromId($_POST['apf_permission_id'])->mName .
            ' permission to ' . $_POST['apf_page_name'] .
            '</span>'
          );
        }
        else if ($_POST['revoke'] == 'Revoke') {
          $user = User::newFromName($_POST['apf_user_name']);
          RecipeUserPermissions::removeUserPermission($title->getArticleID(), $user->getId(), $_POST['apf_permission_id']);
          $output->addWikiText(
            '<span style="color: green">Revoked ' .
            $_POST['apf_user_name'] . ' ' .
            RecipePermission::newFromId($_POST['apf_permission_id'])->mName .
            ' permission to ' . $_POST['apf_page_name'] .
            '</span>'
          );
        }
      }
    }

    //
    // Create `license_form`
    //   Assign 
    //
    $output->addWikiText('== Change Recipe Licenses ==');
    $add_license_form =
      '<form action="" method="post" name="license_form">' .
      'Recipe Page: <input type="text" name="alf_page_name" value="' . $_POST['alf_page_name'] . '"><br/>' .
      'License: <select name="alf_license_id">';
    foreach (RecipeLicense::getAllFromDb() as $license) {
      $add_license_form .='<option value="' . $license->mId . '"';
      if ($_POST['alf_license_id'] == $license->mId) {
        $add_license_form .= ' selected="selected"';
      }
      $add_license_form .= '>' . $license->mName . "</option>";
    }
    $add_license_form .=
      '</select>' .
      '<input type="submit" value="Apply"/>' .
      '</form>';
    $output->addHTML($add_license_form);

    //
    // Process `license_form` POSTed data
    //
    if (
      array_key_exists('alf_page_name', $_POST) && $_POST['alf_page_name'] != '' &&
      array_key_exists('alf_license_id', $_POST) && $_POST['alf_license_id'] != ''
    ) {
      $title = Title::newFromText($_POST['alf_page_name']);
      // Page Not Found
      if ($dbm->select('page', array('page_id'), 'page_title="' . $title->getDBkey() . '"')->numRows() == 0 ) {
        $output->addWikiText('<span style="color: red">Page \'' . $_POST['apf_page_name'] . '\' Not Found</span>');
      }
      // Not an Administrator
      else if (
        !$wgUser->getGroupMemberships()['bureaucrat'] &&
        !in_array($title->getArticleID(), $userPermissions->mPermissions[3])
      ) {
        $output->addWikiText('<span style="color: red">You are not an Administrator of Page \'' . $_POST['alf_page_name'] . '\'</span>');
      }
      // All Good!
      else {
        RecipeLicense::addArticleLicense($title->getArticleID(), $_POST['alf_license_id']);
        $output->addWikiText(
          '<span style="color: green">Applied ' .
          RecipeLicense::newFromId($_POST['alf_license_id'])->mName .
          ' to ' . $_POST['alf_page_name'] .
          '</span>'
        );
      }
    }

    //
    // Report the user's permissions
    //
    $output->addWikiText('== Your Permissions ==');
    $userPermissions = new RecipeUserPermissions($wgUser);
    foreach ($userPermissions->mPermissions as $perm => $articles) {
      $permission = RecipePermission::newFromId($perm);
      $wikitext = 'RecipePermission ' . $permission->mName . ':';
      foreach ($articles as $article_id) { 
        $title = Title::newFromId($article_id);
        if ($title) {
          $wikitext .= ' ' . $title->getText();
        }
      }

      $output->addWikiText($wikitext);
    }
  }


  public static function getLicenseForArticle($article_id) {
    $dbr = wfGetDB(DB_REPLICA);
    $results = $dbr->select(
      'rw_article_license',
      array('license_id'),
      'article_id=' . $article_id
    );
    if ($results->numRows() == 0) {
      $license_name = MediaWiki\MediaWikiServices::getInstance()->getConfigFactory()->makeConfig('recipewiki')->get('RecipeWikiDefaultLicense');
      $default_result = $dbr->select(
        'rw_licenses',
        array('license_id', 'license_name', 'license'),
        'license_name="' . $license_name . '"'
      );
      $row = $default_result->fetchObject();
      return new RecipeLicense($row->license_id, $row->license_name, $row->license);
    }
    return RecipeLicense::newFromId($results->fetchObject()->license_id);
  }
}

?>
