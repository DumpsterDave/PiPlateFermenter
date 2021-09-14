<?php
    try {
        $NewTargetTemp = floatval($_GET['setpoint']) ?? 20.0;
        if (isset($_GET['scale'])) {
            if ($_GET['scale'] == 'f') {
                $NewTargetTemp = ($NewTargetTemp - 32) / 1.8;
            } elseif ($_GET['scale'] == 'k') {
                $NewTargetTemp -= 273.15;
            }
        }
        
        $Config = json_decode(file_get_contents('./py/conf.json'));
        $Config->{'TargetTemp'} = $NewTargetTemp;
        file_put_contents('./py/conf.json', json_encode($Config));
        file_put_contents('./py/reload', 'X');
    } catch (Exception $ex) {
        $f = fopen('./php_error_log', 'w+');
        fwrite($f, date('Y-m-d H:i:s') . " - SET TEMP - " . $ex->getMessage());
        fclose($f);
    }
?>