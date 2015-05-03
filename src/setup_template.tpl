<!doctype html>  

<head>  
  <meta charset="utf-8">  
  <title>metanyx administration</title>  
  <meta name="metanyx" content="Welcome to metanyx.">  
  <meta name="viewport" content="width=device-width"> 
  <link rel="stylesheet" href="static/style.css?v=1">  
</head>  
  
<body>  

  <div id="wrapper">  
    <header>  
      <h1>metanyx administration</h1>  
      <nav>  
        <ul>  
          <li><a rel="external" href="setup">Setup</a></li>  
          <li><a rel="external" href="status">Status</a></li>  
          <li><a rel="external" href="update">Update</a></li>  
          <li><a rel="external" href="https://metanyx.net" target="new">About</a></li>  
          <li><a rel="external" href="shutdown">Shutdown</a></li>  
          <li><a rel="external" href="reboot">Reboot</a></li>  
          <li><a rel="external" href="service">Restart Tor</a></li>  
          <li><a rel="external" href="https://check.torproject.org" target="new">Tor Check</a></li>  
        </ul>  
      </nav>  
    </header>  
          
    <div id="core">
      <form id="setup" action="/setup" method="post">
        <fieldset>
          <legend>Ethernet</legend>
          <input type="radio" name="eth_function" id="dhcp_server" value="dhcp_server" checked="checked">
          <label for="dhcp_server">DHCP Server</label>
          <br>
          <input type="radio" name="eth_function" id="static_server" value="static_server">
          <label for="static_server">Static IP Server</label>
          <br>
          <input type="radio" name="eth_function" id="client" value="dhcp_client">
          <label for="client">DHCP client</label>
          <br>
          <input type="radio" name="eth_function" id="disabled" value="disabled">
          <label for="disabled">Off</label>
        </fieldset>

        <fieldset>
          <legend>Access Point</legend>

          %if usb_count < 2:
            <input name="enabled" id="ap_enable" value="ap" checked="checked" type="radio">
            <label for="ap_enable">Enable</label>
          %else:
            <input name="ap_enable" id="ap_enable" value="1" checked="checked" type="checkbox">
            <label for="ap_enable">Enable</label>
          %end
            <br>

          <input type="radio" name="ap_iface" id="wlan1_ap" value="wlan1" checked="checked">
          <label for="wlan1_ap">wlan1</label>
          <input type="radio" name="ap_iface" id="wlan0_ap" value="wlan0">
          <label for="wlan0_ap">wlan0</label>
          <br><br>

          <label for="ssid">SSID</label><br>
          <input id="ssid" name="ap_ssid" type="text" class="text-input"><br>
          <label for="psk">WPA PSK</label><br>
          <input pattern=".{10,63}" title="10-63 characters" id="psk" name="ap_psk" type="password" class="text-input"><br>

        </fieldset>

        <fieldset>
          <legend>WiFi Client</legend>

          %if not 'None' in wlan_client:

                %if usb_count < 2:
                  <input name="enabled" id="client_enable" value="client" type="radio" >
                  <label for="client_enable">Enable</label>
                %else:
                  <input name="client_enable" id="client_enable" value="1" type="checkbox">
                  <label for="client_enable">Enable</label>
                %end
                  <br>
      
                <input type="radio" name="client_iface" id="wlan1_client" value="wlan1">
                <label for="wlan1_client">wlan1</label>
                <input type="radio" name="client_iface" id="wlan0_client" value="wlan0" checked="checked">
                <label for="wlan0_client">wlan0</label>
                <br><br>
      
                SSID<br>
                <select name="client_ssid" class="text-input">
                  <%
                    if not 'None' in wlan_client:
                        import subprocess 
                        aps = subprocess.check_output(['iw', 'dev', 'wlan0', 'scan'])
                        for line in aps.split('\n'):
                            #TODO: turn this into a whitelist
                            if 'SSID' in line and not ('<' or '>' or '%') in line:
                                ssid = line.split(": ")[1]
                  %>
                  <option value="{{ ssid }}">{{ ssid }}</option>
                            %end
                        %end
                    %end
                </select><br>
      
                WPA PSK<br>
                <input name="client_psk" type="password" class="text-input">
          %else:
              <p>No wifi device found.</p>

          %end
  
        </fieldset>

        <fieldset>
          <button type="submit">Save</button>
        </fieldset>


      </form>

    </div>

  </div>

</body>
</html>
