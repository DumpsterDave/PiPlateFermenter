var TiltColors = new Array("Black", "Blue", "Green", "Orange", "Pink", "Purple", "Red", "Yellow");
var TempSymbol;
var ShiftOn = false;
var Values;

function TempToF(Celsius) {
    return ((Celsius * 1.8) + 32);
}

function TempToK(Celsius) {
    return Celsius + 273.15;
}

function SgToBrix(SG) {
    return (((182.4601 * SG - 775.6821) * SG + 1262.7794) * SG - 669.5622).toFixed(1);
}

function SgToPlato(SG) {
    return (-616.868 + (1111.14 * SG) - (630.272 * Math.pow(SG,2)) + (135.997 * Math.pow(SG,3))).toFixed(1);
}

function ConvertUnits(Values) {
    //Temperature Unit Adjustments
    if (Values['TempUnits'] == "f") {
        TempSymbol = "&#176;F";
        Values['CpuTemp'] = TempToF(Values['CpuTemp']);
        Values['ProbeTemp'] = TempToF(Values['ProbeTemp']);
        Values['TargetTemp'] = TempToF(Values['TargetTemp']);
    } else if (Values['TempUnits'] == "k") {
        TempSymbol = "&#176;K";
        Values['CpuTemp'] = TempToK(Values['CpuTemp']);
        Values['ProbeTemp'] = TempToK(Values['ProbeTemp']);
        Values['TargetTemp'] = TempToK(Values['TargetTemp']);
    } else {
        TempSymbol = "&#176;C";
    }
    document.getElementById('SvFooter').innerHTML = TempSymbol;
    document.getElementById('PvFooter').innerHTML = TempSymbol;

    

    //Tilt Unit Adjustments
    TiltColors.forEach(color=>{
        if (Values['GravUnits'] == 'sg') {
            Values[color]['Grav'] = Values[color]['Grav'].toFixed(3);
        } else if (Values['GravUnits'] == 'b') {
            Values[color]['Grav'] = SgToBrix(Values[color]['Grav']);
        } else {
            Values[color]['Grav'] = SgToPlato(Values[color]['Grav']);
        }

        if(Values['TempUnits'] == 'f') {
            Values[color]['Temp'] = TempToF(Values[color]['Temp']).toFixed(1);
        } else if (Values['TempUnits'] == 'k') {
            Values[color]['Temp'] = TempToK(Values[color]['Temp']).toFixed(1);
        } else {
            Values[color]['Temp'] = Values[color]['Temp'].toFixed(1);
        }
    });

    
}

function InitializeTimers() {
    setInterval(RefreshElements, 1000);
}

function RefreshElements() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            Values = JSON.parse(this.responseText);
            ConvertUnits(Values);

            //Process Sv
            document.getElementById('SvText').innerHTML = Values['TargetTemp'].toFixed(1);

            //Process Pv
            document.getElementById('PvText').innerHTML = Values['ProbeTemp'].toFixed(1);
            if (Values['ProbeTemp'] < (Values['TargetTemp'] - Values['Hysteresis'])) {
                document.getElementById('PvText').className = 'TempLow';
            } else if (Values['ProbeTemp'] > (Values['TargetTemp'] + Values['Hysteresis'])) {
                document.getElementById('PvText').className = 'TempHigh';
            } else {
                document.getElementById('PvText').className = 'TempOk';
            }

            //Process Tilts
            TiltColors.forEach(color=>{
                document.getElementById(color + "Name").innerHTML = Values[color]['Name'];
                document.getElementById(color + "Grav").innerHTML = Values[color]['Grav'];
                document.getElementById(color + "Temp").innerHTML = Values[color]['Temp'] + TempSymbol;
                document.getElementById(color + "Beacon").innerHTML = Values[color]['LastBeacon'];
            });

            //Process Metrics
            document.getElementById("MainVolts").innerHTML = Values['MainVolts'].toFixed(1);
            document.getElementById("MainAmps").innerHTML = Values['MainAmps'].toFixed(1);
            document.getElementById("kWh").innerHTML = Values['kWh'].toFixed(4);
            document.getElementById("EnCost").innerHTML = (Values['kWh'] * .09).toFixed(2);
            document.getElementById("ColdAmps").innerHTML = Values['ColdAmps'].toFixed(1);
            document.getElementById("HotAmps").innerHTML = Values['HotAmps'].toFixed(1);
            var UpTimeParts = Values['Uptime'].split(":");
            var Sec = parseFloat(UpTimeParts[2]).toFixed(2);
            var SecString = Sec;
            if (Sec < 10) {
                SecString = "0" + Sec;
            }
            document.getElementById("Uptime").innerHTML = UpTimeParts[0] + ":" + UpTimeParts[1] + ":" + SecString + " (" + parseInt(Values['SinceLastCycle']) + ")";
            document.getElementById("LastLog").innerHTML = Values['LastLog'];
            document.getElementById("CpuTemp").innerHTML = Values['CpuTemp'].toFixed(1) + TempSymbol;

            if(Values['LogEnabled'] == true) {
                document.getElementById("AzureIcon").src = 'img/la_on.png';
            } else {
                document.getElementById("AzureIcon").src = 'img/la_off.png';
            }
        }
    };

    xhttp.open("GET", "refresh.php", true);
    xhttp.send();
}

function ShowBeerName(color) {
    document.getElementById("BeerName").style.visibility = 'visible';
    document.getElementById('BeerNameDisplay').innerHTML = Values[color]["Name"];
    document.getElementById("NewNameColor").value = color;
    if (Values[color]["Enabled"]) {
        document.getElementById('TiltEnabled').value = "true";
        document.getElementById('TiltToggle').src = "img/toggleon.png";
    } else {
        document.getElementById('TiltEnabled').value = "false";
        document.getElementById('TiltToggle').src = "img/toggleoff.png";
    }

}

function ToggleTilt() {
    if (document.getElementById('TiltEnabled').value == 'true') {
        document.getElementById('TiltEnabled').value = 'false';
        document.getElementById('TiltToggle').src = "img/toggleoff.png";
    } else {
        document.getElementById('TiltEnabled').value = 'true';
        document.getElementById('TiltToggle').src = "img/toggleon.png";
    }
}

function HideBeerName() {
    document.getElementById('BeerNameDisplay').innerHTML = "";
    document.getElementById("BeerName").style.visibility = 'hidden';
}

function SaveConfig() {
    var NewLogEnabled, NewLogFrequency, NewBeaconFrequency, NewTempUnits, NewGravUnits, NewHysteresis, NewCycleFrequency;
    NewLogEnabled = document.getElementById('NewLogEnabled').value;
    NewLogFrequency = document.getElementById('NewLogFrequency').value;
    NewBeaconFrequency = document.getElementById('NewBeaconFrequency').value;
    NewTempUnits = document.getElementById('NewTempUnits').value;
    NewGravUnits = document.getElementById('NewGravUnits').value;
    NewHysteresis = document.getElementById('NewHysteresis').value;
    NewCycleFrequency = document.getElementById('NewCycleFrequency').value;

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            HideConfig();
        }
    };

    xhttp.open("GET", "saveconfig.php?LogEnabled=" + NewLogEnabled + "&LogFreq=" + NewLogFrequency + "&BeaconFreq=" + NewBeaconFrequency + "&TempUnits=" + NewTempUnits + "&GravUnits=" + NewGravUnits + "&Hysteresis=" + NewHysteresis + "&CycleFreq=" + NewCycleFrequency, true);
    xhttp.send();
}

function HideConfig() {
    document.getElementById('Config').style.visibility = 'hidden';
}

function ShowConfig() {
    if (Values['LogEnabled']) {
        document.getElementById('NewLogEnabled').value = 'true';
        document.getElementById('LogEnabled').innerHTML = 'Enabled';
        document.getElementById('LogEnabled').classList.add('ButtonBlue');

    } else {
        document.getElementById('NewLogEnabled').value = 'false';
        document.getElementById('LogEnabled').innerHTML = 'Disabled';
        document.getElementById('LogEnabled').classList.remove('ButtonBlue');
    }

    if(Values['TempUnits'] == 'f') {
        document.getElementById('NewTempUnits').value = 'f';
        document.getElementById('TempUnitsC').classList.remove('ButtonBlue');
        document.getElementById('TempUnitsF').classList.add('ButtonBlue');
        document.getElementById('TempUnitsK').classList.remove('ButtonBlue');
    } else if(Values['TempUnits'] == 'k') {
        document.getElementById('NewTempUnits').value = 'k';
        document.getElementById('TempUnitsC').classList.remove('ButtonBlue');
        document.getElementById('TempUnitsF').classList.remove('ButtonBlue');
        document.getElementById('TempUnitsK').classList.add('ButtonBlue');
    } else {
        document.getElementById('NewTempUnits').value = 'c';
        document.getElementById('TempUnitsC').classList.add('ButtonBlue');
        document.getElementById('TempUnitsF').classList.remove('ButtonBlue');
        document.getElementById('TempUnitsK').classList.remove('ButtonBlue');
    }

    if(Values['GravUnits'] == 'sg') {
        document.getElementById('NewGravUnits').value = 'sg';
        document.getElementById('GravUnitsB').classList.remove('ButtonBlue');
        document.getElementById('GravUnitsP').classList.remove('ButtonBlue');
        document.getElementById('GravUnitsS').classList.add('ButtonBlue');
    } else if (Values['GravUnits'] == 'brix') {
        document.getElementById('NewGravUnits').value = 'brix';
        document.getElementById('GravUnitsB').classList.add('ButtonBlue');
        document.getElementById('GravUnitsP').classList.remove('ButtonBlue');
        document.getElementById('GravUnitsS').classList.remove('ButtonBlue');
    } else {
        document.getElementById('NewGravUnits').value = 'plato';
        document.getElementById('GravUnitsB').classList.remove('ButtonBlue');
        document.getElementById('GravUnitsP').classList.add('ButtonBlue');
        document.getElementById('GravUnitsS').classList.remove('ButtonBlue');
    }

    document.getElementById('LogFrequency').innerHTML = Values['LogFrequency'];
    document.getElementById('NewLogFrequency').value = Values['LogFrequency'];
    document.getElementById('BeaconFrequency').innerHTML = Values['BeaconFrequency'];
    document.getElementById('NewBeaconFrequency').value = Values['BeaconFrequency'];
    document.getElementById('Hysteresis').innerHTML = Values['Hysteresis'].toFixed(1);
    document.getElementById('NewHysteresis').value = Values['Hysteresis'].toFixed(1);
    document.getElementById('NewCycleFrequency').value = Values['CycleFrequency'];
    document.getElementById('CycleFrequency').innerHTML = Values['CycleFrequency'];
    document.getElementById('Config').style.visibility = 'visible';
}

function SetBeerName(color, newName, enabled) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            HideBeerName();
        }
    };
    xhttp.open("GET", "setbeername.php?Color=" + color + "&NewName=" + newName + "&Enabled=" + enabled, true);
    xhttp.send();
}

function BeerName(id){
    if(id == 'bksp') {
        if (document.getElementById('BeerNameDisplay').innerHTML.length > 0) {
            document.getElementById('BeerNameDisplay').innerHTML = document.getElementById('BeerNameDisplay').innerHTML.slice(0, -1);
        }
    } else if (id == 'clr') {
        document.getElementById('BeerNameDisplay').innerHTML = '';
    } else if (id == 'ok') {
        SetBeerName(document.getElementById("NewNameColor").value, document.getElementById('BeerNameDisplay').innerHTML, document.getElementById('TiltEnabled').value);
    } else if (id == 'esc') {
        HideBeerName();
    } else if (id == 'spc') {
        document.getElementById('BeerNameDisplay').innerHTML += ' ';
    } else {
        document.getElementById('BeerNameDisplay').innerHTML += document.getElementById(id).innerHTML;
    }
}

function ToggleShift() {
    var i;
    if (ShiftOn) {
        ShiftOn = false;
        var letters = document.getElementsByClassName("Letter");
        for(i = 0; i < letters.length; i++) {
            letters[i].innerHTML = letters[i].innerHTML.toLowerCase();
        }
        var numbers = document.getElementsByClassName("Number");
        for(i = 0; i < numbers.length; i++) {
            switch(numbers[i].innerHTML) {
                case '!':
                    numbers[i].innerHTML = '1';
                    break;
                case '@':
                    numbers[i].innerHTML = '2';
                    break;
                case '#':
                    numbers[i].innerHTML = '3';
                    break;
                case '$':
                    numbers[i].innerHTML = '4';
                    break;
                case '%':
                    numbers[i].innerHTML = '5';
                    break;
                case '^':
                    numbers[i].innerHTML = '6';
                    break;
                case '&amp;':
                    numbers[i].innerHTML = '7';
                    break;
                case '*':
                    numbers[i].innerHTML = '8';
                    break;
                case '(':
                    numbers[i].innerHTML = '9';
                    break;
                case ')':
                    numbers[i].innerHTML = '0';
                    break;
            }
        }
        var special = document.getElementsByClassName("Special");
        for(i = 0; i < special.length; i++) {
            switch(special[i].innerHTML) {
                case '~':
                    special[i].innerHTML = '`';
                    break;
            }
        }
    } else {
        ShiftOn = true;
        var letters = document.getElementsByClassName("Letter");
        for(i = 0; i < letters.length; i++) {
            letters[i].innerHTML = letters[i].innerHTML.toUpperCase();
        }
        var numbers = document.getElementsByClassName("Number");
        for(i = 0; i < numbers.length; i++) {
            switch(numbers[i].innerHTML) {
                case '1':
                    numbers[i].innerHTML = '!';
                    break;
                case '2':
                    numbers[i].innerHTML = '@';
                    break;
                case '3':
                    numbers[i].innerHTML = '#';
                    break;
                case '4':
                    numbers[i].innerHTML = '$';
                    break;
                case '5':
                    numbers[i].innerHTML = '%';
                    break;
                case '6':
                    numbers[i].innerHTML = '^';
                    break;
                case '7':
                    numbers[i].innerHTML = '&amp;';
                    break;
                case '8':
                    numbers[i].innerHTML = '*';
                    break;
                case '9':
                    numbers[i].innerHTML = '(';
                    break;
                case '0':
                    numbers[i].innerHTML = ')';
                    break;
            }
        }
        var special = document.getElementsByClassName("Special");
        for(i = 0; i < special.length; i++) {
            switch(special[i].innerHTML) {
                case '`':
                    special[i].innerHTML = '~';
                    break;
            }
        }
    }
}

function SetTargetTemp(NewTarget) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            HideTargetTemp();
        }
    };

    xhttp.open("GET", "settargettemp.php?setpoint=" + NewTarget + "&scale=" + Values['TempUnits'], true);
    xhttp.send();
}

function HideTargetTemp() {
    document.getElementById('NewTargetTemp').innerHTML = '';
    document.getElementById('SetTargetTemp').style.visibility = 'hidden';
}

function ShowTargetTemp() {
    document.getElementById('CurrTargetTemp').innerHTML = parseFloat(Values['TargetTemp']).toFixed(1) + TempSymbol;
    document.getElementById('NewTargetTemp').innerHTML = parseFloat(Values['TargetTemp']).toFixed(1);
    document.getElementById('SetTargetTemp').style.visibility = 'visible';
}

function TargetTemp(id) {
    var val = document.getElementById('NewTargetTemp').innerHTML;
    if (id == 'ttx') {
        HideTargetTemp();
    } else if (id == 'ttb') {
        if(val.length > 1) {
            val = parseFloat(val) * 10;
            val = val.toString().slice(0, -1);
            val = parseFloat(val) / 10;
            document.getElementById('NewTargetTemp').innerHTML = val.toFixed(1);
        } if (val.length == 1) {
            document.getElementById('NewTargetTemp').innerHTML = '';
        }
    } else if (id == 'ttc') {
        document.getElementById('NewTargetTemp').innerHTML = '';
    } else if (id == 'ttok') {
        SetTargetTemp(document.getElementById('NewTargetTemp').innerHTML);
    } else {
        if(val.length == 0) {
            document.getElementById('NewTargetTemp').innerHTML = "." + id.substring(2);
        } else if(val.length < 4){
            val = parseFloat(val) * 10;
            val = val.toString();
            val += id.substring(2);
            val = (parseFloat(val) / 10).toFixed(1);
            document.getElementById('NewTargetTemp').innerHTML = val;
        }
    }
}

function ToggleLogs(){
    if (document.getElementById('NewLogEnabled').value == 'true') {
        document.getElementById('NewLogEnabled').value = 'false';
        document.getElementById('LogEnabled').innerHTML = 'Disabled';
        document.getElementById('LogEnabled').classList.remove('ButtonBlue');
    } else {
        document.getElementById('NewLogEnabled').value = 'true';
        document.getElementById('LogEnabled').innerHTML = 'Enabled';
        document.getElementById('LogEnabled').classList.add('ButtonBlue');
    }
}

function AdjustLogFreq(amount) {
    var newVal = parseInt(document.getElementById('NewLogFrequency').value);
    newVal += amount;
    document.getElementById('NewLogFrequency').value = newVal;
    document.getElementById('LogFrequency').innerHTML = newVal;
}

function AdjustBeaconFreq(amount) {
    var newVal = parseInt(document.getElementById('NewBeaconFrequency').value)
    newVal += amount;
    document.getElementById('NewBeaconFrequency').value = newVal;
    document.getElementById('BeaconFrequency').innerHTML = newVal;
}

function ToggleTempUnits(unit) {
    if (unit == 'f') {
        document.getElementById('NewTempUnits').value = 'f';
        document.getElementById('TempUnitsF').classList.add('ButtonBlue');
        document.getElementById('TempUnitsC').classList.remove('ButtonBlue');
        document.getElementById('TempUnitsK').classList.remove('ButtonBlue');
    } else if (unit == 'c') {
        document.getElementById('NewTempUnits').value = 'c';
        document.getElementById('TempUnitsF').classList.remove('ButtonBlue');
        document.getElementById('TempUnitsC').classList.add('ButtonBlue');
        document.getElementById('TempUnitsK').classList.remove('ButtonBlue');
    } else {
        document.getElementById('NewTempUnits').value = 'k';
        document.getElementById('TempUnitsF').classList.remove('ButtonBlue');
        document.getElementById('TempUnitsC').classList.remove('ButtonBlue');
        document.getElementById('TempUnitsK').classList.add('ButtonBlue');
    }
}

function ToggleGravUnits(unit) {
    if (unit == 'brix') {
        document.getElementById('NewGravUnits').value = 'brix';
        document.getElementById('GravUnitsB').classList.add('ButtonBlue');
        document.getElementById('GravUnitsP').classList.remove('ButtonBlue');
        document.getElementById('GravUnitsS').classList.remove('ButtonBlue');
    } else if (unit == 'plato') {
        document.getElementById('NewGravUnits').value = 'plato';
        document.getElementById('GravUnitsB').classList.remove('ButtonBlue');
        document.getElementById('GravUnitsP').classList.add('ButtonBlue');
        document.getElementById('GravUnitsS').classList.remove('ButtonBlue');
    } else {
        document.getElementById('NewGravUnits').value = 'sg';
        document.getElementById('GravUnitsB').classList.remove('ButtonBlue');
        document.getElementById('GravUnitsP').classList.remove('ButtonBlue');
        document.getElementById('GravUnitsS').classList.add('ButtonBlue');
    }
}

function AdjustHysteresis(amount) {
    var newVal = parseFloat(document.getElementById('NewHysteresis').value);
    newVal += amount;
    newVal = newVal.toFixed(1);
    document.getElementById('NewHysteresis').value = newVal;
    document.getElementById('Hysteresis').innerHTML = newVal;
}

function AdjustCycleFreq(amount) {
    var newVal = parseInt(document.getElementById('NewCycleFrequency').value);
    newVal += amount;
    document.getElementById('NewCycleFrequency').value = newVal;
    document.getElementById('CycleFrequency').innerHTML = newVal;
}

function Power(action) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
        }
    };

    xhttp.open("GET", "power.php?action=" + action, true);
    xhttp.send();
}