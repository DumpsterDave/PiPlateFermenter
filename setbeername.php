<?php
    try {
        if (isset($_GET['NewName'])) {
            $Config = json_decode(file_get_contents("./py/conf.json"));
            $Config->{'BeerName'} = $_GET['NewName'];
            $Enabled = $Config->{'BeaconEnabled'};
            if (isset($_GET['Enabled'])) {
                if (strtolower($_GET['Enabled']) == 'false') {
                    $Enabled = false;
                }
                if (strtolower($_GET['Enabled']) == 'true') {
                    $Enabled = true;
                }
            }
            $Config->{'BeaconEnabled'} = $Enabled;
            file_put_contents('./py/conf.json', json_encode($Config));
            file_put_contents('./py/reload', 'true');
        } else {
            echo "Error: MISSING PARAM!";
        }
    } catch (Exception $ex) {
        $f = fopen('./php_error_log', 'w+');
        fwrite($f, date('Y-m-d H:i:s') . " - SET NAME - " . $ex->getMessage());
        fclose($f);
    }
?>