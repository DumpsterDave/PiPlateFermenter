<?php
    $LogEntries = array();

    if (ISSET($_GET['test'])) {
        $LogEntries['Controller'] = "2022-01-01 14:23:00 TILT [43] : Test Error 1<br />
        2022-01-01 14:23:00 TILT [46] : Test Error 2<br />
        2022-01-01 14:23:00 TILT [44] : Test Error 3<br />
        2022-01-01 14:23:00 CONTROLLER [143] : Test Error 4<br />
        2022-01-01 14:23:00 CONTROLLER [537] : Test Error 5<br />";
        $LogEntries['IoT'] = "2022-01-01 14:23:00 TILT [43] : Test Error 1<br />
        2022-01-01 14:23:00 TILT [46] : Test Error 2<br />
        2022-01-01 14:23:00 TILT [44] : Test Error 3<br />
        2022-01-01 14:23:00 CONTROLLER [143] : Test Error 4<br />
        2022-01-01 14:23:00 CONTROLLER [537] : Test Error 5<br />";
        print(json_encode($LogEntries));
    } elseif (ISSET($_GET['action'])) {
        $Action = $_GET['action'];
        if ($Action == 'reset') {
            file_put_contents('./py/reset_error_counts', 'true');
        } elseif ($Action == 'clear') {
            file_put_contents('./py/reset_error_counts', 'true');
            file_put_contents('./py/clear_logs', 'true');
        }
    } else {
        if (file_exists('python_errors.log')) {
            $LogEntries['Controller'] = shell_exec('tail -n 10 python_errors.log');
            $LogEntries['Controller'] = str_replace("\n", "<br />", $LogEntries['Controller']);
        } else {
            $LogEntries['Controller'] = "No Entries";
        }
        if (file_exists('iot.log')) {
            $LogEntries['IoT'] = shell_exec('tail -n 10 iot.log');
            $LogEntries['IoT'] = str_replace("\n", "<br />", $LogEntries['IoT']);
        } else {
            $LogEntries['IoT'] = "No Entries";
        }
        print(json_encode($LogEntries));
    }
?>