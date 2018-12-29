<?php

class RecipeWiki {
  public static function init(Parser $parser) {
    $parser->setHook('recipe', 'RecipeWiki::RecipeWikiRender');
  }

  public static function RecipeWikiRender($input, array $args, Parser $parser, PPFrame $frame) {
    return file_get_contents('http://localhost:6543/recipe');
  }

}

?>
