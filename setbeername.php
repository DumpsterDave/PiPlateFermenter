<?php
    if (isset($_GET['Color']) && isset($_GET['NewName'])) {
        $Config = json_decode(file_get_contents("./py/conf.json"));
        $Config->{$_GET['Color']} = $_GET['NewName'];
        file_put_contents('./py/conf.json', json_encode($Config));
        file_put_contents('./py/reload', 'true');
    } else {
        echo "Error: MISSING PARAM!";
    }
?>