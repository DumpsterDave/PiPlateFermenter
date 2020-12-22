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
            Thermometer Icon by Yannick Lung
            https://www.iconfinder.com/iconsets/hawcons
        -->
        <meta http-equiv="Cache-control" content="no-cache">
        <script src="tilt.js"></script>
        <link rel="stylesheet" href="tilt.css">
    </head>
    <body onLoad="InitializeTimers();">
        <div id="Main">
            <div id="Sv">
                <span id="SvHeader">Sv</span>
                <span id="SvText"></span>
                <span id="SvFooter">&#176;C</span>
            </div>
            <div id="Pv">
                <span id="PvHeader">Pv</span>
                <span id="PvText" class="TempOk"></span>
                <span id="PvFooter">&#176;C</span>
            </div>
            <div id="Tilts">
                <div class="Tilt Black" onClick="ShowBeerName('Black');"><div id="BlackName" class="BeerName"></div><div id="BlackGrav" class="BeerGrav"></div><div id="BlackTemp" class="BeerTemp"></div></div>
                <div class="Tilt Blue" onClick="ShowBeerName('Blue');"><div id="BlueName" class="BeerName"></div><div id="BlueGrav" class="BeerGrav"></div><div id="BlueTemp" class="BeerTemp"></div></div>
                <div class="Tilt Green" onClick="ShowBeerName('Green');"><div id="GreenName" class="BeerName"></div><div id="GreenGrav" class="BeerGrav"></div><div id="GreenTemp" class="BeerTemp"></div></div>
                <div class="Tilt Orange" onClick="ShowBeerName('Orange');"><div id="OrangeName" class="BeerName"></div><div id="OrangeGrav" class="BeerGrav"></div><div id="OrangeTemp" class="BeerTemp"></div></div>
                <div class="Tilt Pink" onClick="ShowBeerName('Pink');"><div id="PinkName" class="BeerName"></div><div id="PinkGrav" class="BeerGrav"></div><div id="PinkTemp" class="BeerTemp"></div></div>
                <div class="Tilt Purple" onClick="ShowBeerName('Purple');"><div id="PurpleName" class="BeerName"></div><div id="PurpleGrav" class="BeerGrav"></div><div id="PurpleTemp" class="BeerTemp"></div></div>
                <div class="Tilt Red" onClick="ShowBeerName('Red');"><div id="RedName" class="BeerName"></div><div id="RedGrav" class="BeerGrav"></div><div id="RedTemp" class="BeerTemp"></div></div>
                <div class="Tilt Yellow" onClick="ShowBeerName('Yellow');"><div id="YellowName" class="BeerName"></div><div id="YellowGrav" class="BeerGrav"></div><div id="YellowTemp" class="BeerTemp"></div></div>    
            </div>
            <div id="Metrics">
                <div class="Metric">Main Volts: <span id="MainVolts"></Span></div>
                <div class="Metric">Cold Amps: <span id="ColdAmps"></Span></div>
                <div class="Metric">Up: <span id="Uptime"></Span></div>
                <div class="MetricButtons" id="MetricButtons"><img src="img/refresh.png" onClick="window.location.reload(true);" style="cursor: pointer;"/><img id="AzureIcon" src="img/la_on.png"/><img src="img/config.png" onClick="ShowConfig();" style="cursor: pointer;"/></div>
                <div class="Metric">Main Amps: <span id="MainAmps"></Span></div>
                <div class="Metric">Hot Amps: <span id="HotAmps"></Span></div>
                <div class="Metric">LB: <span id="LastBeacon"></Span></div>
                <div class="Metric">CPU Temp: <span id="CpuTemp"></Span></div>
                <div class="Metric"></div>
                <div class="Metric"></div>
            </div>
        </div>
        <div id="BeerName">
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
                <div class="BeerNameButtonVertical" id="bksp" onclick="BeerName('bksp');">&larr;</div>
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
                <div class="BeerNameButton" id="esc" onclick="BeerName('esc');">&#8855;</div>
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
                <div class="BeerNameButtonVertical" id="ok" onclick="BeerName('ok');">&#10004;</div>
                
                <!--Bottom Row-->
                <div class="BeerNameButtonDouble" id="clr" onclick="BeerName('clr');">CLR</div>
                <div class="BeerNameButton Letter" id="z" onclick="BeerName('z');">z</div>
                <div class="BeerNameButton Letter" id="x" onclick="BeerName('x');">x</div>
                <div class="BeerNameButton Letter" id="c" onclick="BeerName('c');">c</div>
                <div class="BeerNameButton Letter" id="v" onclick="BeerName('v');">v</div>
                <div class="BeerNameButton Letter" id="b" onclick="BeerName('b');">b</div>
                <div class="BeerNameButton Letter" id="n" onclick="BeerName('n');">n</div>
                <div class="BeerNameButton Letter" id="m" onclick="BeerName('m');">m</div>
                <div class="BeerNameButtonDouble" id="spc" onclick="BeerName('spc');">&blank;</div>
                <input id="NewNameColor" type="hidden" value=""/>
            </div>
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