<?php

class RecipeDatabaseInitializer extends LoggedUpdateMaintenance {
  //
  // Database Initialization
  //
  function doDBUpdates() {
    // Add default permissions
    //   Read
    //   Edit
    //   Administer
    $this->addPermission(1, 'Read');
    $this->addPermission(2, 'Edit');
    $this->addPermission(3, 'Administer');

    // Add implied permissions
    //   Edit implies Read
    //   Administer implies Read
    $this->addImpliedPermission(2, 1);
    $this->addImpliedPermission(3, 1);

    // Add some licenses
    //  - CC_BY
    //      CreativeCommons Attribution 4.0 International
    $this->addLicense(
      'CC_BY',
      '<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.'
    );
    //  - CC_BY_NC_4_0
    //      CreativeCommons Attribution NonCommercial 4.0 International
    $this->addLicense(
      'CC_BY_NC_4_0',
      '<a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/">Creative Commons Attribution-NonCommercial 4.0 International License</a>.'
    );
    //  - CC_BY_ND_4_0
    //      CreativeCommons Attribution NoDerivatives 4.0 International
    $this->addLicense(
      'CC_BY_ND_4_0',
      '<a rel="license" href="http://creativecommons.org/licenses/by-nd/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nd/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nd/4.0/">Creative Commons Attribution-NoDerivatives 4.0 International License</a>.'
    );
    //  - CC_BY_NC_ND_4_0
    //      CreativeCommons Attribution NonCommercial NoDerivatives 4.0 International
    $this->addLicense(
      'CC_BY_NC_ND_4_0',
      '<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-nd/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/4.0/">Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License</a>.'
    );
    //  - CC_BY_SA_4_0
    //      CreativeCommons Attribution ShareAlike 4.0 International
    $this->addLicense(
      'CC_BY_SA_4_0',
      '<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.'
    );
    //  - CC_BY_NC_SA_4_0
    //      CreativeCommons Attribution NonCommercial ShareAlike 4.0 International
    $this->addLicense(
      'CC_BY_NC_SA_4_0',
      '<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>'
    );

    return true;
  }

  public static function addPermission($permission_id, $permission_name) {
    // We're writing the db here, so make sure to get the master (DB_MASTER, not DB_REPLICA)
    $dbm = wfGetDB(DB_MASTER);

    if ($dbm->select('rw_permissions', array('permission_id'), 'permission_id=' . $permission_id)->numRows() == 0) {
      $dbm->insert('rw_permissions',
        array(
          'permission_id'   => $permission_id,
          'permission_name' => $permission_name
        )
      );
    }
  }

  public static function addImpliedPermission($master_permission, $implied_permission) {
    // We're writing the db here, so make sure to get the master (DB_MASTER, not DB_REPLICA)
    $dbm = wfGetDB(DB_MASTER);

    $master_permission_id;
    $implied_permission_id;
    if (gettype($master_permission) == "integer") {
      $master_permission_id = $master_permission;
    }
    else {
      $master_permission_id = $master_permission->mId;
    }
    if (gettype($implied_permission) == "integer") {
      $implied_permission_id = $implied_permission;
    }
    else {
      $implied_permission_id = $implied_permission->mId;
    }

    if (
      $dbm->select(
        'rw_implied_permissions',
        array('ip_id'),
        array(
          'master_permission_id='  . $master_permission_id,
          'implied_permission_id=' . $implied_permission_id
        )
      )->numRows() == 0
    ) {
      $dbm->insert(
        'rw_implied_permissions',
        array(
          'master_permission_id'  => $master_permission_id,
          'implied_permission_id' => $implied_permission_id
        )
      );
    }
  }

  public static function addLicense($license_name, $licenseHTML) {
    // We're writing the db here, so make sure to get the master (DB_MASTER, not DB_REPLICA)
    $dbm = wfGetDB(DB_MASTER);
    if (
      $dbm->select(
        'rw_licenses',
        array('license_id'),
        array('license_name="' . $license_name . '"')
      )->numRows() == 0
    ) {
      $dbm->insert(
        'rw_licenses',
        array(
          'license_name' => $license_name,
          'license'      => $licenseHTML
        )
      );
    }
  }

  function getUpdateKey() {
    return "RecipeWikiDbInit";
  }
}



?>