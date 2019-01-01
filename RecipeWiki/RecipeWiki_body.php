<?php

class RecipeWiki {
  public static function onParserFirstCallInit(Parser $parser) {
    $parser->setHook('recipe', 'RecipeWiki::RecipeWikiRender');
  }

  public static function onLoadExtensionSchemaUpdates( DatabaseUpdater $updater ) {
    $updater->addExtensionTable('rw_permissions', __DIR__ . '/sql/table_rw_permissions.sql');
    $updater->addExtensionTable('rw_implied_permissions', __DIR__ . '/sql/table_rw_implied_permissions.sql');
    $updater->addExtensionTable('rw_article_user_permissions', __DIR__ . '/sql/table_rw_article_user_permissions.sql');
    return true;
  }

  public static function RecipeWikiRender($input, array $args, Parser $parser, PPFrame $frame) {
    // if (RecipeWikiAuthorizedUser($frame->getTitle(), $parser->getUser()->getId()))
    $content = $args;
    $content['body'] = $input;
    $content['user'] = $parser->getUser()->getName();
    $content['pagedbkey'] = $frame->getTitle()->getDBkey();
    $content['article_id'] = $frame->getTitle()->getArticleID();

    $context = stream_context_create(array(
      'http' => array(
        'method' => 'POST',
        'header'=> "Content-type: application/x-www-form-urlencoded",
        'content' => http_build_query($content)
      )
    ));

    return file_get_contents('http://localhost:6543/recipe', FALSE, $context);
  }

  public static function onuserCan(&$title, &$user, $action, &$result) {
    $dbr = wfGetDB(DB_REPLICA);
    $article_id = $title->getArticleID();

    $perms = $dbr->select('rw_permissions', array('permission_id', 'permission_name'));

    $content = array();
    $content['article_id'] = $title->getArticleID();
    $content['permissions'] = array();
    $num_rows = $perms->numRows();
    foreach ($perms as $perm) {
      $content['permissions'][] = $perm->permission_id . ": " . $perm->permission_name;
    }
    $content['num_rows'] = $num_rows;
    $context = stream_context_create(array(
      'http' => array(
        'method' => 'POST',
        'header'=> "Content-type: application/x-www-form-urlencoded",
        'content' => http_build_query($content)
      )
    ));
    file_get_contents('http://localhost:6543/recipe', FALSE, $context);
  }

  public static function getUserPermissions(User $user) {
    return UserPermissions($user);
    // $dbr = wfGetDB(DB_REPLICA);
    // $permissions = array();
    // foreach ($dbr->select('rw_permissions', array('permission_id')) as $perm) {
    //   $permissions[$perm->permission_id] = array();
    // }
    // $result = $dbr->select(
    //   'rw_article_user_permissions',
    //   array('article_id', 'permission_id'),
    //   'user_id=' . $user->getId()
    // );
    // foreach ($result as $res) {
    //   $implied = $dbr->select(
    //     'rw_implied_permissions',
    //     array('implied_permission_id'),
    //     'master_permission_id=' . $res->permission_id
    //   );

    //   if (!in_array($res->article_id, $permissions[$res->permission_id])) {
    //     $permissions[$res->permission_id]->add($res->article_id);
    //   }
    //   foreach ($implied as $impl) {
    //     if (!in_array($res->article_id, $permissions[$impl->implied_permission_id])) {
    //       $permissions[$impl->implied_permission_id]->add($res->article_id);
    //     }
    //   }
    // }
    // return $permissions;
  }
}


//
// Database Initialization
//

// We're writing the db here, so make sure to get the master (DB_MASTER, not DB_REPLICA)
$dbm = wfGetDB(DB_MASTER);

// Populate `rw_permissions`
// Read is id 1
//   Grants ability to read the recipe page
if ($dbm->select('rw_permissions', array('permission_id'), 'permission_id=1')->numRows() == 0) {
  $dbm->insert('rw_permissions',
    array(
      'permission_id'   => 1,
      'permission_name' => 'Read'
    )
  );
}

// Edit is id 2
//   Grants ability to edit the recipe page
if ($dbm->select('rw_permissions', array('permission_id'), 'permission_id=2')->numRows() == 0) {
  $dbm->insert('rw_permissions',
    array(
      'permission_id'   => 2,
      'permission_name' => 'Edit'
    )
  );
}

// Administer is id 3
//   Grants ability to change the recipe license
if ($dbm->select('rw_permissions', array('permission_id'), 'permission_id=3')->numRows() == 0) {
  $dbm->insert('rw_permissions',
    array(
      'permission_id'   => 3,
      'permission_name' => 'Administer'
    )
  );
}

// Populate `rw_implied_permissions`
// Edit implies Read
if ($dbm->select(
      'rw_implied_permissions',
      array('ip_id'),
      array('master_permission_id=2', 'implied_permission_id=1')
    )->numRows() == 0
  ) {
  $dbm->insert(
    'rw_implied_permissions',
    array(
      'master_permission_id'  => 2,
      'implied_permission_id' => 1
    )
  );
}

// Administer implies Read
if ($dbm->select(
      'rw_implied_permissions',
      array('ip_id'),
      array('master_permission_id=3', 'implied_permission_id=1')
    )->numRows() == 0
  ) {
  $dbm->insert(
    'rw_implied_permissions',
    array(
      'master_permission_id'  => 3,
      'implied_permission_id' => 1
    )
  );
}


?>
