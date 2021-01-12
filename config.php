<?php
    try{
        #Perform initial data load
        $Config = json_decode(file_get_contents('./py/conf.json'));

        $SaveConfig = $_GET['apply'] ?? false;
        $Test = $_GET['test'] ?? false;

        $TiltColors = array("Black", "Blue", "Green", "Orange", "Pink", "Purple", "Red", "Yellow");

        if ($SaveConfig == 'true') {
            if (strlen($_POST['WorkspaceId']) > 0) {
                $Config->{'WorkspaceId'} = $_POST['WorkspaceId'];
            }
            if (strlen($_POST['WorkspaceKey']) > 0) {
                $Config->{'WorkspaceKey'} = $_POST['WorkspaceKey'];
            }
            $Config->{'LogName'} = $_POST['LogName'];
            $Config->{'LogFrequency'} = intval($_POST['LogFrequency']);
            $LogEnabled = $_POST['LogEnabled'] ?? false;
            if ($LogEnabled == 'true') {
                $Config->{'LogEnabled'} = true;
            } else {
                $Config->{'LogEnabled'} = false;
            }
            $Config->{'BeaconFrequency'} = intval($_POST['BeaconFrequency']);
            $BeaconEnabled = $_POST['BeaconEnabled'] ?? false;
            if ($BeaconEnabled == 'true') {
                $Config->{'BeaconEnabled'} = true;
            } else {
                $Config->{'BeaconEnabled'} = false;
            }
            $Config->{'TempUnits'} = $_POST['TempUnits'];
            $Config->{'GravUnits'} = $_POST['GravUnits'];
            $EnabledTilts = array();
            foreach($TiltColors as $color) {
                $Config->{$color} = $_POST[$color];
                $TiltEnabled = $_POST[$color . 'Enabled'] ?? false;
                if ($TiltEnabled == 'true') {
                    array_push($EnabledTilts, $color);
                }
            }
            $Config->{'EnabledTilts'} = $EnabledTilts;
            $Config->{'Hysteresis'} = floatval($_POST['Hysteresis']);
            $Config->{'TargetTemp'} = floatval($_POST['TargetTemp']);
            $Config->{'CycleFrequency'} = intval($_POST['CycleFrequency']);
            $Config->{'kWhCost'} = floatval($_POST['kWhCost']);

            file_put_contents('./py/conf.json', json_encode($Config));
            file_put_contents('./py/reload', 'true');

            header("Location: config.php");
        }
?>
<html>
    <head>
        <link rel="stylesheet" href="tilt.css"/>
        <link rel="stylesheet" href="config.css"/>
        <script src="config.js"></script>
    </head>
    <body>
        <div id="Main">
            <form action="config.php?apply=true" method="post">
                <div id="SettingsContainer">
                    <span>Workspace ID:</span><input type="text" class="TextIn" id="WorkspaceId" name="WorkspaceId"/><span></span>
                    <span>Workspace Key:</span><input type="text" class="TextIn" id="WorkspaceKey" name="WorkspaceKey"/><span></span>
                    <span>Log Name:</span><input type="text" class="TextIn" id="LogName" name="LogName" value="<?php echo $Config->{'LogName'}; ?>"/><span></span>
                    <span>Log Frequency:</span><div class="rangecontainer"><input type="range" min="10" max="600" class="range" id="LogFrequency" name="LogFrequency" onInput="UpdateSliderValue('LogFrequency');" onChange="UpdateSliderValue('LogFrequency');" value="<?php echo $Config->{'LogFrequency'}; ?>"/></div><span class="SliderValue" id="LogFrequencyValue"><?php echo $Config->{'LogFrequency'}; ?></span><span></span>               
                    <span>Log Enabled:</span><label class="switch single"><input type="checkbox" name="LogEnabled" id="LogEnabled" value="true" <?php if ($Config->{'LogEnabled'}) { echo "checked";} ?>><span class="slider round"></span></label><span></span>
                    <span>Beacon Frequency:</span><div class="rangecontainer"><input type="range" class="range" id="BeaconFrequency" name="BeaconFrequency" min="10" max="600" onInput="UpdateSliderValue('BeaconFrequency');" onChange="UpdateSliderValue('BeaconFrequency');" value="<?php echo $Config->{'BeaconFrequency'}; ?>" /></div><span class="SliderValue" id="BeaconFrequencyValue"><?php echo $Config->{'BeaconFrequency'}; ?></span><span></span>
                    <span>Beacon Enabled:</span><label class="switch single"><input type="checkbox" name="BeaconEnabled" id="BeaconEnabled" value="true" <?php if ($Config->{'BeaconEnabled'}) { echo "checked";} ?>><span class="slider round"></span></label><span></span>
                    <span>Temperature Units:</span><span class="RadioIn">
                        <label class="container">Celsius
                            <input type="radio" id="TempUnitsC" name="TempUnits" value="c" <?php if ($Config->{'TempUnits'} == 'c') {echo "checked";} ?>>
                            <span class="checkmark"></span>
                        </label>
                        <label class="container">Fahrenheit
                            <input type="radio" id="TempUnitsF" name="TempUnits" value="f" <?php if ($Config->{'TempUnits'} == 'f') {echo "checked";} ?>>
                            <span class="checkmark"></span>
                        </label>
                        <label class="container">Kelvin
                            <input type="radio" id="TempUnitsK" name="TempUnits" value="k" <?php if ($Config->{'TempUnits'} == 'k') {echo "checked";} ?>>
                            <span class="checkmark"></span>
                        </label>
                    </span>
                    <span>Gravity Units:</span><span class="RadioIn">
                        <label class="container">Brix
                            <input type="radio" id="GravUnitsB" name="GravUnits" value="b" <?php if ($Config->{'GravUnits'} == 'b') {echo "checked";} ?>>
                            <span class="checkmark"></span>
                        </label>
                        <label class="container">Plato
                            <input type="radio" id="GravUnitsP" name="GravUnits" value="p" <?php if ($Config->{'GravUnits'} == 'p') {echo "checked";} ?>>
                            <span class="checkmark"></span>
                        </label>
                        <label class="container">SG
                            <input type="radio" id="GravUnitsSG" name="GravUnits" value="sg" <?php if ($Config->{'GravUnits'} == 'sg') {echo "checked";} ?>>
                            <span class="checkmark"></span>
                        </label></span>
                        <span>Beer Names:</span>
                        <div id="BeerNames" class="TextIn8">
                            <input class="In8" type="text" style="border-color: #ffffff" id="Black" name="Black" value="<?php echo $Config->{"Black"};?>"/>
                            <input class="In8" type="text" style="border-color: #00a2e8" id="Blue" name="Blue" value="<?php echo $Config->{"Blue"};?>"/>
                            <input class="In8" type="text" style="border-color: #22b14c" id="Green" name="Green" value="<?php echo $Config->{"Green"};?>"/>
                            <input class="In8" type="text" style="border-color: #ff7f27" id="Orange" name="Orange" value="<?php echo $Config->{"Orange"};?>"/>
                            <input class="In8" type="text" style="border-color: #ffaec9" id="Pink" name="Pink" value="<?php echo $Config->{"Pink"};?>"/>
                            <input class="In8" type="text" style="border-color: #a349a4" id="Purple" name="Purple" value="<?php echo $Config->{"Purple"};?>"/>
                            <input class="In8" type="text" style="border-color: #ed1c24" id="Red" name="Red" value="<?php echo $Config->{"Red"};?>"/>
                            <input class="In8" type="text" style="border-color: #fff200" id="Yellow" name="Yellow" value="<?php echo $Config->{"Yellow"};?>"/>
                        </div>
                        <span>Hysteresis:</span><div class="rangecontainer"><input type="range" class="range" id="Hysteresis" name="Hysteresis" min="0" max="5" step="0.1" onInput="UpdateSliderValue('Hysteresis');" onChange="UpdateSliderValue('Hysteresis');" value="<?php echo $Config->{'Hysteresis'}; ?>" /></div><span class="SliderValue" id="HysteresisValue"><?php echo $Config->{'Hysteresis'}; ?></span><span></span>
                        <span>Target Temp:</span><div class="rangecontainer"><input type="range" class="range" id="TargetTemp" name="TargetTemp" min="0" max="36" step="0.1" onInput="UpdateSliderValue('TargetTemp');" onChange="UpdateSliderValue('TargetTemp');" value="<?php echo $Config->{'TargetTemp'}; ?>" /></div><span class="SliderValue" id="TargetTempValue"><?php echo $Config->{'TargetTemp'}; ?></span><span></span>
                        <span>Cycle Frequency:</span><div class="rangecontainer"><input type="range" min="300" max="600" class="range" id="CycleFrequency" name="CycleFrequency" onInput="UpdateSliderValue('CycleFrequency');" onChange="UpdateSliderValue('CycleFrequency');" value="<?php echo $Config->{'CycleFrequency'}; ?>"/></div><span class="SliderValue" id="CycleFrequencyValue"><?php echo $Config->{'CycleFrequency'}; ?></span><span></span>               
                        <span>$/kWh:</span><input type="text" class="TextIn" id="kWhCost" name="kWhCost"/ value="<?php echo $Config->{'kWhCost'};?>"><span></span>
                        <span>Enabled Tilts:</span>
                        <div id="EnabledTiltSwitches" class="TextIn8">
                            <?php
                                foreach ($TiltColors as $color) {
                                    ?>
                                         <label class="switch"><input type="checkbox" name="<?php echo $color;?>Enabled" id="<?php echo $color; ?>Enabled" value="true" <?php if (in_array($color, $Config->{'EnabledTilts'})) { echo "checked"; } ?>><span class="slider round <?php echo $color; ?>"></span></label>
                                    <?php
                                }
                            ?>
                        </div>
                        
                    </span>
                </div>
                <input type="submit" id="submit" name="submit">
            </form>
        </div>
    </body>
</html>
<?php
    } catch (Exception $ex) {
        $f = fopen('/var/www/html/php_error_log', 'w+');
        fwrite($f, date('Y-m-d H:i:s') . " - CONFIG - " . $ex->getMessage());
        fclose($f);
    }
?>