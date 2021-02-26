<?php
    $MIN_LOG_FREQ = 15;
    $MIN_BEACON_FREQ = 15;
    $MIN_CYCLE_FREQ = 300;
    $MIN_HYSTERESIS = .1;
    $VALID_TEMP_UNITS = array('c', 'f', 'k');
    $VALID_GRAV_UNITS = array('brix', 'plato', 'sg');

    try {
        $Conf = json_decode(file_get_contents('./py/conf.json'));
        $LogEnabled = $_GET['LogEnabled'];
        if ($LogEnabled == 'false') {
            $Conf->{'LogEnabled'} = false;
        } elseif ($LogEnabled == 'true') {
            $Conf->{'LogEnabled'} = true;
        }
        $LogFreq = intval($_GET['LogFreq']) ?? 300;
        if ($LogFreq < $MIN_LOG_FREQ) {
            $LogFreq = $MIN_LOG_FREQ;  #Minimum log freq
        }
        $Conf->{'LogFrequency'} = $LogFreq;

        $BeaconFreq = intval($_GET['BeaconFreq']) ?? 15;
        if ($BeaconFreq < $MIN_BEACON_FREQ) {
            $BeaconFreq = $MIN_BEACON_FREQ;
        }
        $Conf->{'BeaconFrequency'} = $BeaconFreq;

        $TempUnits = strtolower($_GET['TempUnits']) ?? 'f';
        if (!in_array($TempUnits, $VALID_TEMP_UNITS)) {
            $TempUnits = 'f';
        }
        $Conf->{'TempUnits'} = $TempUnits;

        $GravUnits = strtolower($_GET['GravUnits']) ?? 'sg';
        if (!in_array($GravUnits, $VALID_GRAV_UNITS)) {
            $GravUnits = 'sg';
        }
        $Conf->{'GravUnits'} = $GravUnits;

        $Hysteresis = floatval($_GET['Hysteresis']) ?? 0.5;
        if ($Hysteresis < $MIN_HYSTERESIS) {
            $Hysteresis = $MIN_HYSTERESIS;
        }
        if ($TempUnits == 'f') {
            $Hysteresis = ($Hysteresis - 32) / 1.8;
        } elseif ($TempUnits == 'k') {
            $Hysteresis = $Hysteresis - 273.15;
        }
        $Conf->{'Hysteresis'} = $Hysteresis;

        $CycleFreq = intval($_GET['CycleFreq']) ?? 300;
        if ($CycleFreq < $MIN_CYCLE_FREQ){
            $CycleFreq = $MIN_CYCLE_FREQ;
        }
        $Conf->{'CycleFrequency'} = $CycleFreq;

        file_put_contents('./py/conf.json', json_encode($Conf));
        file_put_contents('./py/reload', 'true');
    } catch (Exception $ex) {
        $f = fopen('./php_error_log', 'w+');
        fwrite($f, date('Y-m-d H:i:s') . " - SAVE CONFIG - " . $ex->getMessage());
        fclose($f);
    }
?>