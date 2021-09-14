<?php
    try{
        #Perform initial data load
        $Data = json_decode(file_get_contents('/var/www/html/py/data.json'));
?>
<html>
    <head>
        <!--
            All code and artwork (C) 2020 Scott Corio except:
            Restart Icon by Frank Souza
            https://www.iconfinder.com/iconsets/fs-icons-ubuntu-by-franksouza-
            Power Icon by Artyom Khamitov
            https://www.iconfinder.com/iconsets/glyphs
            Up/Down Icons by Vathanx
            https://www.iconfinder.com/iconsets/ionicons
            Gear Icon by Assyifa Art
            https://www.iconfinder.com/iconsets/user-interface-glyph-5
            Toggle Icon by wishforge.games
            https://www.iconfinder.com/iconsets/user-interface-584

        -->
        <script src="tilt.js"></script>
        <link rel="stylesheet" href="tilt.css">
    </head>
    <body onLoad="InitializeTimers();">
        <div id="Main">
            <div id="Sv">
                <span id="SvHeader">Sv</span>
                <span id="SvText" onClick="ShowTargetTemp();"></span>
                <span id="SvFooter">&#176;C</span>
            </div>
            <div id="Pv">
                <span id="PvHeader">Pv</span>
                <span id="PvText" class="TempOk"></span>
                <span id="PvFooter">&#176;C</span>
            </div>
            <div id="Tilts">
                <div class="Tilt Black" onClick="ShowBeerName('Black');"><div id="BlackName" class="BeerName"></div><div id="BlackGrav" class="BeerGrav"></div><div class="TiltData"><div id="BlackBeacon" class="TiltBeacon"></div><div id="BlackTemp" class="TiltTemp"></div></div></div>
                <div class="Tilt Blue" onClick="ShowBeerName('Blue');"><div id="BlueName" class="BeerName"></div><div id="BlueGrav" class="BeerGrav"></div><div class="TiltData"><div id="BlueBeacon" class="TiltBeacon"></div><div id="BlueTemp" class="TiltTemp"></div></div></div>
                <div class="Tilt Green" onClick="ShowBeerName('Green');"><div id="GreenName" class="BeerName"></div><div id="GreenGrav" class="BeerGrav"></div><div class="TiltData"><div id="GreenBeacon" class="TiltBeacon"></div><div id="GreenTemp" class="TiltTemp"></div></div></div>
                <div class="Tilt Orange" onClick="ShowBeerName('Orange');"><div id="OrangeName" class="BeerName"></div><div id="OrangeGrav" class="BeerGrav"></div><div class="TiltData"><div id="OrangeBeacon" class="TiltBeacon"></div><div id="OrangeTemp" class="TiltTemp"></div></div></div>
                <div class="Tilt Pink" onClick="ShowBeerName('Pink');"><div id="PinkName" class="BeerName"></div><div id="PinkGrav" class="BeerGrav"></div><div class="TiltData"><div id="PinkBeacon" class="TiltBeacon"></div><div id="PinkTemp" class="TiltTemp"></div></div></div>
                <div class="Tilt Purple" onClick="ShowBeerName('Purple');"><div id="PurpleName" class="BeerName"></div><div id="PurpleGrav" class="BeerGrav"></div><div class="TiltData"><div id="PurpleBeacon" class="TiltBeacon"></div><div id="PurpleTemp" class="TiltTemp"></div></div></div>
                <div class="Tilt Red" onClick="ShowBeerName('Red');"><div id="RedName" class="BeerName"></div><div id="RedGrav" class="BeerGrav"></div><div class="TiltData"><div id="RedBeacon" class="TiltBeacon"></div><div id="RedTemp" class="TiltTemp"></div></div></div>
                <div class="Tilt Yellow" onClick="ShowBeerName('Yellow');"><div id="YellowName" class="BeerName"></div><div id="YellowGrav" class="BeerGrav"></div><div class="TiltData"><div id="YellowBeacon" class="TiltBeacon"></div><div id="YellowTemp" class="TiltTemp"></div></div></div>
            </div>
            <div id="Metrics">
                <div class="Metric">Main Volts: <span id="MainVolts">125</Span></div>
                <div class="Metric">Cold Amps: <span id="ColdAmps">0</Span></div>
                <div class="Metric">Up: <span id="Uptime">00:00:00</Span></div>
                <div class="MetricButtons" id="MetricButtons"><img src="img/refresh.png" onClick="window.location.reload(true);" style="cursor: pointer;"/><img id="AzureIcon" src="img/la_on.png"/><img src="img/config.png" onClick="ShowConfig();" style="cursor: pointer;"/></div>
                <div class="Metric">Main Amps: <span id="MainAmps">0</Span></div>
                <div class="Metric">Hot Amps: <span id="HotAmps">0</Span></div>
                <div class="Metric">LL: <span id="LastLog">0:0:0</Span></div>
                <div class="Metric">kWh: <span id="kWh">0</span></div>
                <div class="Metric">Energy Cost: $<span id="EnCost">0.00</span></div>
                <div class="Metric">CPU Temp: <span id="CpuTemp">45</Span></div>
            </div>
        </div>
        <div id="BeerName">
            <div id="BeerToggle"><img id="TiltToggle" src="img/toggleoff.png" onClick="ToggleTilt();"/></div>
            <div id="BeerNameDisplay"></div>
            <div id="BeerNameButtons">
                <!--Top Row-->
                <div class="BeerNameButton Special" id="tilde" onclick="BeerName('tilde');">`</div>
                <div class="BeerNameButton Number" id="1" onclick="BeerName('1');">1</div>
                <div class="BeerNameButton Number" id="2" onclick="BeerName('2');">2</div>
                <div class="BeerNameButton Number" id="3" onclick="BeerName('3');">3</div>
                <div class="BeerNameButton Number" id="4" onclick="BeerName('4');">4</div>
                <div class="BeerNameButton Number" id="5" onclick="BeerName('5');">5</div>
                <div class="BeerNameButton Number" id="6" onclick="BeerName('6');">6</div>
                <div class="BeerNameButton Number" id="7" onclick="BeerName('7');">7</div>
                <div class="BeerNameButton Number" id="8" onclick="BeerName('8');">8</div>
                <div class="BeerNameButton Number" id="9" onclick="BeerName('9');">9</div>
                <div class="BeerNameButton Number" id="0" onclick="BeerName('0');">0</div>
                <div class="BeerNameButtonVertical ButtonYellow" id="bksp" onclick="BeerName('bksp');">&larr;</div>
                <!--Second Row-->
                <div class="BeerNameButton Letter" id="q" onClick="BeerName('q');">q</div>
                <div class="BeerNameButton Letter" id="w" onclick="BeerName('w');">w</div>
                <div class="BeerNameButton Letter" id="e" onclick="BeerName('e');">e</div>
                <div class="BeerNameButton Letter" id="r" onclick="BeerName('r');">r</div>
                <div class="BeerNameButton Letter" id="t" onclick="BeerName('t');">t</div>
                <div class="BeerNameButton Letter" id="y" onclick="BeerName('y');">y</div>
                <div class="BeerNameButton Letter" id="u" onclick="BeerName('u');">u</div>
                <div class="BeerNameButton Letter" id="i" onclick="BeerName('i');">i</div>
                <div class="BeerNameButton Letter" id="o" onclick="BeerName('o');">o</div>
                <div class="BeerNameButton Letter" id="p" onclick="BeerName('p');">p</div>
                <div class="BeerNameButton ButtonRed" id="esc" onclick="BeerName('esc');">&#8855;</div>
                <!--Third Row-->
                <div class="BeerNameButtonDouble" id="shift" onClick="ToggleShift();">&uarr;</div>
                <div class="BeerNameButton Letter" id="a" onclick="BeerName('a');">a</div>
                <div class="BeerNameButton Letter" id="s" onclick="BeerName('s');">s</div>
                <div class="BeerNameButton Letter" id="d" onclick="BeerName('d');">d</div>
                <div class="BeerNameButton Letter" id="f" onclick="BeerName('f');">f</div>
                <div class="BeerNameButton Letter" id="g" onclick="BeerName('g');">g</div>
                <div class="BeerNameButton Letter" id="h" onclick="BeerName('h');">h</div>
                <div class="BeerNameButton Letter" id="j" onclick="BeerName('j');">j</div>
                <div class="BeerNameButton Letter" id="k" onclick="BeerName('k');">k</div>
                <div class="BeerNameButton Letter" id="l" onclick="BeerName('l');">l</div>
                <div class="BeerNameButtonVertical ButtonGreen" id="ok" onclick="BeerName('ok');">&#10004;</div>
                
                <!--Bottom Row-->
                <div class="BeerNameButtonDouble ButtonRed" id="clr" onclick="BeerName('clr');">CLR</div>
                <div class="BeerNameButton Letter" id="z" onclick="BeerName('z');">z</div>
                <div class="BeerNameButton Letter" id="x" onclick="BeerName('x');">x</div>
                <div class="BeerNameButton Letter" id="c" onclick="BeerName('c');">c</div>
                <div class="BeerNameButton Letter" id="v" onclick="BeerName('v');">v</div>
                <div class="BeerNameButton Letter" id="b" onclick="BeerName('b');">b</div>
                <div class="BeerNameButton Letter" id="n" onclick="BeerName('n');">n</div>
                <div class="BeerNameButton Letter" id="m" onclick="BeerName('m');">m</div>
                <div class="BeerNameButtonDouble" id="spc" onclick="BeerName('spc');">&blank;</div>
                <input id="NewNameColor" type="hidden" value=""/>
                <input id="TiltEnabled" type="hidden" value=""/>
            </div>
        </div>
        <div id="SetTargetTemp">
            <div id="NewTargetTemp"></div>
            <div id="CurrTargetTemp"></div>
            <div id="TargetTempNumPad">
                <!--Top Row-->
                <div class="TargetTempButton ButtonRed" id="ttc" onClick="TargetTemp('ttc');">C</div>
                <div class="TargetTempButton" id="tt0" onClick="TargetTemp('tt0');">0</div>
                <div class="TargetTempButton ButtonYellow" id="ttb" onClick="TargetTemp('ttb');">&larr;</div>
                <!--Second Row-->
                <div class="TargetTempButton" id="tt7" onClick="TargetTemp('tt7');">7</div>
                <div class="TargetTempButton" id="tt8" onClick="TargetTemp('tt8');">8</div>
                <div class="TargetTempButton" id="tt9" onClick="TargetTemp('tt9');">9</div>
                <!--Third Row-->
                <div class="TargetTempButton" id="tt4" onClick="TargetTemp('tt4');">4</div>
                <div class="TargetTempButton" id="tt5" onClick="TargetTemp('tt5');">5</div>
                <div class="TargetTempButton" id="tt6" onClick="TargetTemp('tt6');">6</div>
                <!--Fourth Row-->
                <div class="TargetTempButton" id="tt1" onClick="TargetTemp('tt1');">1</div>
                <div class="TargetTempButton" id="tt2" onClick="TargetTemp('tt2');">2</div>
                <div class="TargetTempButton" id="tt3" onClick="TargetTemp('tt3');">3</div>
                <!--Bottom Row-->
                <div class="TargetTempButton ButtonRed" id="ttx" onClick="TargetTemp('ttx');">&#8855;</div>
                <div class="TargetTempButtonDouble ButtonGreen" id="ttok" onClick="TargetTemp('ttok');">&#10004;</div>
            </div>
        </div>
        <div id="Config">
            <!--Log Analytics Row-->
            <div class="ConfigLabel">Log Analytics:</div>
            <div class="ConfigButton" id="LogEnabled" onClick="ToggleLogs();">Enabled</div>
            <div class="empty"></div>
            <div class="empty"></div>
            <!--Log Frequency-->
            <div class="ConfigLabel">Log Freq:</div>
            <div class="ConfigLabel" id="LogFrequency">300</div>
            <div class="ConfigButton" id="DecLogFreq" onClick="AdjustLogFreq(-1);">&darr;</div>
            <div class="ConfigButton" id="IncLogFreq" onClick="AdjustLogFreq(1);">&uarr;</div>
            <!--Beacon Frequency-->
            <div class="ConfigLabel">Beacon Freq:</div>
            <div class="ConfigLabel" id="BeaconFrequency">15</div>
            <div class="ConfigButton" id="DecBeaconFreq" onClick="AdjustBeaconFreq(-1);">&darr;</div>
            <div class="ConfigButton" id="IncBeaconFreq" onClick="AdjustBeaconFreq(1);">&uarr;</div>
            <!--Temp Units-->
            <div class="ConfigLabel">Temperature:</div>
            <div class="ConfigButton" id="TempUnitsC" onClick="ToggleTempUnits('c');">&#176;C</div>
            <div class="ConfigButton" id="TempUnitsF" onClick="ToggleTempUnits('f');">&#176;F</div>
            <div class="ConfigButton" id="TempUnitsK" onClick="ToggleTempUnits('k');">&#176;K</div>
            <!--Grav Units-->
            <div class="ConfigLabel">Gravity</div>
            <div class="ConfigButton" id="GravUnitsB" onClick="ToggleGravUnits('brix');">Brix</div>
            <div class="ConfigButton" id="GravUnitsP" onClick="ToggleGravUnits('plato');">Plato</div>
            <div class="ConfigButton" id="GravUnitsS" onClick="ToggleGravUnits('sg');">SG</div>
            <!--Hysteresis-->
            <div class="ConfigLabel">Hysteresis:</div>
            <div class="ConfigLabel" id="Hysteresis">0.5</div>
            <div class="ConfigButton" id="DecHysteresis" onClick="AdjustHysteresis(-0.1);">&darr;</div>
            <div class="ConfigButton" id="IncHysteresis" onClick="AdjustHysteresis(0.1);">&uarr;</div>
            <!--Cycle Length-->
            <div class="ConfigLabel">Cycle Freq:</div>
            <div class="ConfigLabel" id="CycleFrequency">300</div>
            <div class="ConfigButton" id="DecCycleFreq" onClick="AdjustCycleFreq(-1);">&darr;</div>
            <div class="ConfigButton" id="IncCycleFreq" onClick="AdjustCycleFreq(1);">&uarr;</div>
            <!--Controls-->
            <div class="ConfigButton ButtonRed" onClick="Power('off');">Shutdown</div>
            <div class="ConfigButton ButtonYellow" onClick="Power('reset');">Restart</div>
            <div class="ConfigButton" onClick="HideConfig();">X</div>
            <div class="ConfigButton ButtonGreen" onClick="SaveConfig();">&#10004;</div>

            <input type="hidden" id="NewLogEnabled" value="false"/>
            <input type="hidden" id="NewLogFrequency" value="300"/>
            <input type="hidden" id="NewBeaconFrequency" value="15"/>
            <input type="hidden" id="NewTempUnits" value="f"/>
            <input type="hidden" id="NewGravUnits" value="sg"/>
            <input type="hidden" id="NewHysteresis" value="0.5"/>
            <input type="hidden" id="NewCycleFrequency" value="300"/>
        </div>
    </body>
</html>
<?php
    } catch (Exception $ex) {
        $f = fopen('/var/www/html/php_error_log', 'w+');
        fwrite($f, date('Y-m-d H:i:s') . " - INDEX - " . $ex->getMessage());
        fclose($f);
    }
?>