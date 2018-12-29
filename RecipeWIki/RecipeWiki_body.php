<?php

$wgHooks['ParserFirstCallInit'][] = 'RecipeWikiSetup';

function RecipeWikiSetup(Parser $parser) {
  $parser->setHook('recipe', 'RecipeWikiRender');
  return true;
}

function RecipeWikiRender($input, array $args, Parser $parser, PPFrame $frame) {
  return file_get_contents('http://localhost:6543/recipe');
}

?>
