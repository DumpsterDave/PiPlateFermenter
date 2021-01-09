<?php
    try {
        if (isset($_GET['Color']) && isset($_GET['NewName'])) {
            $Enabled = true;
            if (strtolower($_GET['Enabled']) == 'false') {
                $Enabled = false;
            }
            $Config = json_decode(file_get_contents("./py/conf.json"));
            $Config->{$_GET['Color']} = $_GET['NewName'];
            $IsEnabled = array_search($_GET['Color'], $Config->{"EnabledTilts"});
            if (($IsEnabled != false) && ($Enabled == false)) {
                array_splice($Config->{"EnabledTilts"}, $IsEnabled, 1);
            } elseif (($IsEnabled == false) && ($Enabled == true)) {
                $Config->{"EnabledTilts"}[] = $_GET['Color'];
            }
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