<?php

class RecipeWiki {
  public static function onParserFirstCallInit(Parser $parser) {
    $parser->setHook('recipe', 'RecipeWiki::RecipeWikiRender');
  }

  public static function onLoadExtensionSchemaUpdates( DatabaseUpdater $updater ) {
    $updater->addExtensionTable('rw_is_recipe', __DIR__ . '/sql/table_rw_is_recipe.sql');
    $updater->addExtensionTable('rw_permissions', __DIR__ . '/sql/table_rw_permissions.sql');
    $updater->addExtensionTable('rw_implied_permissions', __DIR__ . '/sql/table_rw_implied_permissions.sql');
    $updater->addExtensionTable('rw_article_user_permissions', __DIR__ . '/sql/table_rw_article_user_permissions.sql');
    $updater->addExtensionTable('rw_licenses', __DIR__ . '/sql/table_rw_licenses.sql');
    $updater->addExtensionTable('rw_article_license', __DIR__ . '/sql/table_rw_article_license.sql');
    $updater->addPostDatabaseUpdateMaintenance(RecipeDatabaseInitializer);
    return true;
  }

  public static function RecipeWikiRender($input, array $args, Parser $parser, PPFrame $frame) {
    RecipeWiki::addRecipe($frame->getTitle()->getArticleID());
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

    $recipe = file_get_contents('http://localhost:6543/recipe', FALSE, $context);
    $license = SpecialRecipeLicenses::getLicenseForArticle($frame->getTitle()->getArticleID());
    return $recipe . '<br/>' . $license->mHTML;
  }

  public static function addRecipe($article_id) {
    // We're writing the db here, so make sure to get the master (DB_MASTER, not DB_REPLICA)
    $dbm = wfGetDB(DB_MASTER);
    if (
      $dbm->select(
        'rw_is_recipe',
        array('article_id'),
        array('article_id=' . $article_id)
      )->numRows() == 0
    ) {
      $dbm->insert(
        'rw_is_recipe',
        array(
          'article_id' => $article_id
        )
      );
    }
  }

  public static function isRecipe($article_id) {
    $dbr = wfGetDB(DB_REPLICA);
    if (
      $dbr->select(
        'rw_is_recipe',
        array('article_id'),
        array('article_id=' . $article_id)
      )->numRows() == 0
    ) {
      return FALSE;
    }
    return TRUE;
  }

  public static function onuserCan(&$title, &$user, $action, &$result) {
    if (RecipeWiki::isRecipe($title->getArticleID())) {
      $userPermissions = new RecipeUserPermissions($user);
      // By default, anyone can read recipes
      if ($action == 'read') {
        $result = TRUE;
        return TRUE;
      }
      // Editing requires Edit permission (ID = 2)
      else if ($action == 'edit') {
        if (in_array($title->getArticleID(), $userPermissions->mPermissions[2])) {
          $result = TRUE;
          return TRUE;
        }
        else {
          $result = FALSE;
          return FALSE;
        }
      }
      // Everything else requires Administer (ID = 3)
      //   'move'
      //   'protect'
      //   'delete'
      //   'deletehistory'
      else {
        if (in_array($title->getArticleID(), $userPermissions->mPermissions[3])) {
          $result = TRUE;
          return TRUE;
        }
        else {
          $result = FALSE;
          return FALSE;
        }
      }
    }
    // If it's not a recipe, just move on
    return TRUE;
  }

}


?>
