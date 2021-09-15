<?php
    try {
        if (isset($_GET['action'])) {
            $Action = $_GET['action'];
            if ($Action == 'off') {
                file_put_contents('/var/www/html/py/STOP', 'STOP');
                sleep(2);
                $out = shell_exec('sudo shutdown -h now');
            } elseif ($Action == 'reset') {
                $out = shell_exec('sudo shutdown -r now');
            }
        }
    } catch (Exception $ex) {
        $f = fopen('./php_error_log', 'w+');
        fwrite($f, date('Y-m-d H:i:s') . " - POWER - " . $ex->getMessage());
        fclose($f);
    }
?>